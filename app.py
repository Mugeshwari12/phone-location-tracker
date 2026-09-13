from flask import Flask, send_file, request, jsonify
import csv
from datetime import datetime
import math
import subprocess
import sys
from geopy.geocoders import Nominatim


app = Flask(__name__)


# ---------------------------------------------------------
# CURRENT GPS STATE
# ---------------------------------------------------------

last_latitude = None
last_longitude = None
current_speed = 0.0


# ---------------------------------------------------------
# GPS SETTINGS
# ---------------------------------------------------------

MAX_GPS_ACCURACY_METERS = 100
MAX_GPS_JUMP_METERS = 1000
MAX_REALISTIC_SPEED_KMH = 200


# ---------------------------------------------------------
# GEOCODER
# ---------------------------------------------------------

geolocator = Nominatim(
    user_agent="phone_location_tracker"
)


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------

@app.route("/")
def home():
    return send_file("gps.html")


# ---------------------------------------------------------
# READ GPS LOCATIONS
# ---------------------------------------------------------

def read_locations():

    locations = []

    try:

        with open(
            "location_history.csv",
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.reader(file)

            for row in reader:

                if not row:
                    continue

                # Skip header
                if row[0].strip().lower() in [
                    "timestamp",
                    "date",
                    "time"
                ]:
                    continue

                # Minimum required columns
                if len(row) < 3:
                    continue

                try:

                    timestamp = row[0].strip()

                    latitude = float(row[1])

                    longitude = float(row[2])

                    # City
                    city = (
                        row[3].strip()
                        if len(row) >= 4 and row[3].strip()
                        else "Unknown"
                    )

                    # Country
                    country = (
                        row[4].strip()
                        if len(row) >= 5 and row[4].strip()
                        else "Unknown"
                    )

                    # GPS Accuracy
                    accuracy = None

                    if len(row) >= 6 and row[5].strip():

                        try:
                            accuracy = float(row[5])
                        except (ValueError, TypeError):
                            accuracy = None

                    dt = datetime.strptime(
                        timestamp,
                        "%Y-%m-%d %H:%M:%S"
                    )

                    locations.append({
                        "timestamp": timestamp,
                        "datetime": dt,
                        "latitude": latitude,
                        "longitude": longitude,
                        "city": city,
                        "country": country,
                        "accuracy": accuracy
                    })

                except (ValueError, TypeError):
                    continue

    except FileNotFoundError:

        return []

    locations.sort(
        key=lambda x: x["datetime"]
    )

    return locations


# ---------------------------------------------------------
# CALCULATE DISTANCE
# ---------------------------------------------------------

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    earth_radius = 6371000

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    delta_lat = math.radians(
        lat2 - lat1
    )

    delta_lon = math.radians(
        lon2 - lon1
    )

    a = (
        math.sin(delta_lat / 2) ** 2
        +
        math.cos(lat1)
        *
        math.cos(lat2)
        *
        math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius * c


# ---------------------------------------------------------
# CALCULATE PERIOD STATISTICS
# ---------------------------------------------------------

def calculate_period_statistics(locations):

    if not locations:

        return {
            "points": 0,
            "distance": 0,
            "average_speed": 0,
            "max_speed": 0,
            "first_tracking": None,
            "last_tracking": None,
            "tracking_duration": "0m"
        }

    total_distance = 0

    speeds = []

    valid_points = 1

    previous = locations[0]

    for current in locations[1:]:

        distance = calculate_distance(
            previous["latitude"],
            previous["longitude"],
            current["latitude"],
            current["longitude"]
        )

        time_difference = (
            current["datetime"]
            -
            previous["datetime"]
        ).total_seconds()

        # Ignore extremely large GPS jumps
        if distance > 500:
            continue

        if time_difference > 0:

            speed_kmh = (
                distance
                /
                time_difference
                *
                3.6
            )

            # Ignore unrealistic speed
            if speed_kmh > MAX_REALISTIC_SPEED_KMH:
                continue

            speeds.append(speed_kmh)

        total_distance += distance

        valid_points += 1

        previous = current

    if speeds:

        average_speed = (
            sum(speeds) / len(speeds)
        )

        max_speed = max(speeds)

    else:

        average_speed = 0

        max_speed = 0

    duration_seconds = (
        locations[-1]["datetime"]
        -
        locations[0]["datetime"]
    ).total_seconds()

    if duration_seconds < 0:
        duration_seconds = 0

    hours = int(
        duration_seconds // 3600
    )

    minutes = int(
        (duration_seconds % 3600) // 60
    )

    if hours > 0:

        tracking_duration = (
            f"{hours}h {minutes}m"
        )

    else:

        tracking_duration = (
            f"{minutes}m"
        )

    return {

        "points": valid_points,

        "distance": round(
            total_distance / 1000,
            2
        ),

        "average_speed": round(
            average_speed,
            2
        ),

        "max_speed": round(
            max_speed,
            2
        ),

        "first_tracking":
            locations[0]["datetime"].strftime(
                "%H:%M:%S"
            ),

        "last_tracking":
            locations[-1]["datetime"].strftime(
                "%H:%M:%S"
            ),

        "tracking_duration":
            tracking_duration
    }


# ---------------------------------------------------------
# CURRENT STATS
# ---------------------------------------------------------

@app.route("/stats")
def stats():

    locations = read_locations()

    if not locations:

        return jsonify({

            "points": 0,

            "distance": 0,

            "latitude": None,

            "longitude": None,

            "current_location": "Unknown",

            "current_speed": 0,

            "accuracy": None,

            "average_speed": 0,

            "max_speed": 0,

            "first_tracking": None,

            "last_tracking": None,

            "tracking_duration": "0m"
        })

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    today_locations = [

        location

        for location in locations

        if location["datetime"].strftime(
            "%Y-%m-%d"
        ) == today

    ]

    statistics = calculate_period_statistics(
        today_locations
    )

    latest = locations[-1]

    return jsonify({

        "points":
            statistics["points"],

        "distance":
            statistics["distance"],

        "latitude":
            latest["latitude"],

        "longitude":
            latest["longitude"],

        "current_location":
            f'{latest["city"]}, {latest["country"]}',

        "current_speed":
            round(current_speed, 2),

        "accuracy":
            latest["accuracy"],

        "average_speed":
            statistics["average_speed"],

        "max_speed":
            statistics["max_speed"],

        "first_tracking":
            statistics["first_tracking"],

        "last_tracking":
            statistics["last_tracking"],

        "tracking_duration":
            statistics["tracking_duration"]
    })


# ---------------------------------------------------------
# DAILY STATISTICS
# ---------------------------------------------------------

@app.route("/daily_stats")
def daily_stats():

    locations = read_locations()

    daily_data = {}

    for location in locations:

        date = location["datetime"].strftime(
            "%Y-%m-%d"
        )

        if date not in daily_data:

            daily_data[date] = []

        daily_data[date].append(location)

    result = []

    for date in sorted(
        daily_data.keys(),
        reverse=True
    ):

        statistics = calculate_period_statistics(
            daily_data[date]
        )

        result.append({

            "date": date,

            "points":
                statistics["points"],

            "distance":
                statistics["distance"],

            "average_speed":
                statistics["average_speed"],

            "max_speed":
                statistics["max_speed"],

            "first_tracking":
                statistics["first_tracking"],

            "last_tracking":
                statistics["last_tracking"],

            "tracking_duration":
                statistics["tracking_duration"]
        })

    return jsonify(result)


# ---------------------------------------------------------
# DATE STATISTICS
# ---------------------------------------------------------

@app.route("/date_stats")
def date_stats():

    selected_date = request.args.get(
        "date"
    )

    if not selected_date:

        return jsonify({

            "error":
                "Date is required"

        }), 400

    try:

        datetime.strptime(
            selected_date,
            "%Y-%m-%d"
        )

    except ValueError:

        return jsonify({

            "error":
                "Invalid date format"

        }), 400

    locations = read_locations()

    selected_locations = [

        location

        for location in locations

        if location["datetime"].strftime(
            "%Y-%m-%d"
        ) == selected_date

    ]

    statistics = calculate_period_statistics(
        selected_locations
    )

    return jsonify({

        "date":
            selected_date,

        "points":
            statistics["points"],

        "distance":
            statistics["distance"],

        "average_speed":
            statistics["average_speed"],

        "max_speed":
            statistics["max_speed"],

        "first_tracking":
            statistics["first_tracking"],

        "last_tracking":
            statistics["last_tracking"],

        "tracking_duration":
            statistics["tracking_duration"]
    })


# ---------------------------------------------------------
# OVERALL SUMMARY
# ---------------------------------------------------------

@app.route("/summary_stats")
def summary_stats():

    locations = read_locations()

    if not locations:

        return jsonify({

            "total_tracking_days": 0,

            "total_distance_km": 0,

            "overall_max_speed_kmh": 0,

            "total_gps_points": 0,

            "highest_speed_day": None,

            "highest_speed_value": 0,

            "longest_distance_day": None,

            "longest_distance_value": 0,

            "most_gps_points_day": None,

            "most_gps_points_value": 0
        })

    daily_data = {}

    for location in locations:

        date = location["datetime"].strftime(
            "%Y-%m-%d"
        )

        if date not in daily_data:

            daily_data[date] = []

        daily_data[date].append(location)

    daily_statistics = []

    for date, day_locations in daily_data.items():

        statistics = calculate_period_statistics(
            day_locations
        )

        daily_statistics.append({

            "date": date,

            "points":
                statistics["points"],

            "distance":
                statistics["distance"],

            "average_speed":
                statistics["average_speed"],

            "max_speed":
                statistics["max_speed"]
        })

    total_tracking_days = len(
        daily_statistics
    )

    total_distance_km = sum(
        day["distance"]
        for day in daily_statistics
    )

    overall_max_speed = max(

        (
            day["max_speed"]
            for day in daily_statistics
        ),

        default=0
    )

    highest_speed_record = max(

        daily_statistics,

        key=lambda x:
            x["max_speed"],

        default=None
    )

    longest_distance_record = max(

        daily_statistics,

        key=lambda x:
            x["distance"],

        default=None
    )

    most_points_record = max(

        daily_statistics,

        key=lambda x:
            x["points"],

        default=None
    )

    total_gps_points = sum(

        day["points"]

        for day in daily_statistics

    )

    return jsonify({

        "total_tracking_days":
            total_tracking_days,

        "total_distance_km":
            round(
                total_distance_km,
                2
            ),

        "overall_max_speed_kmh":
            round(
                overall_max_speed,
                2
            ),

        "total_gps_points":
            total_gps_points,

        "highest_speed_day":
            highest_speed_record["date"]
            if highest_speed_record
            else None,

        "highest_speed_value":
            round(
                highest_speed_record["max_speed"],
                2
            )
            if highest_speed_record
            else 0,

        "longest_distance_day":
            longest_distance_record["date"]
            if longest_distance_record
            else None,

        "longest_distance_value":
            round(
                longest_distance_record["distance"],
                2
            )
            if longest_distance_record
            else 0,

        "most_gps_points_day":
            most_points_record["date"]
            if most_points_record
            else None,

        "most_gps_points_value":
            most_points_record["points"]
            if most_points_record
            else 0
    })


# ---------------------------------------------------------
# EXPORT RAW GPS HISTORY
# ---------------------------------------------------------

@app.route("/export_locations")
def export_locations():

    locations = read_locations()

    filename = (
        "gps_location_history_export.csv"
    )

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([

            "Timestamp",

            "Latitude",

            "Longitude",

            "City",

            "Country",

            "Accuracy (m)"

        ])

        for location in locations:

            writer.writerow([

                location["timestamp"],

                location["latitude"],

                location["longitude"],

                location["city"],

                location["country"],

                location["accuracy"]

                if location["accuracy"] is not None

                else ""

            ])

    return send_file(

        filename,

        as_attachment=True,

        download_name=filename,

        mimetype="text/csv"
    )


# ---------------------------------------------------------
# EXPORT DAILY ANALYTICS
# ---------------------------------------------------------

@app.route("/export_daily_stats")
def export_daily_stats():

    locations = read_locations()

    daily_data = {}

    for location in locations:

        date = location["datetime"].strftime(
            "%Y-%m-%d"
        )

        if date not in daily_data:

            daily_data[date] = []

        daily_data[date].append(location)

    filename = (
        "gps_daily_analytics_export.csv"
    )

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([

            "Date",

            "GPS Points",

            "Distance (km)",

            "Average Speed (km/h)",

            "Maximum Speed (km/h)",

            "First Tracking",

            "Last Tracking",

            "Tracking Duration"

        ])

        for date in sorted(

            daily_data.keys(),

            reverse=True

        ):

            statistics = calculate_period_statistics(
                daily_data[date]
            )

            writer.writerow([

                date,

                statistics["points"],

                statistics["distance"],

                statistics["average_speed"],

                statistics["max_speed"],

                statistics["first_tracking"],

                statistics["last_tracking"],

                statistics["tracking_duration"]

            ])

    return send_file(

        filename,

        as_attachment=True,

        download_name=filename,

        mimetype="text/csv"
    )


# ---------------------------------------------------------
# SAVE GPS LOCATION
# ---------------------------------------------------------

@app.route(
    "/save_location",
    methods=["POST"]
)
def save_location():

    global last_latitude
    global last_longitude
    global current_speed

    data = request.get_json()

    if not data:

        return jsonify({

            "success": False,

            "message":
                "No location data received"

        }), 400

    # -----------------------------------------------------
    # COORDINATES
    # -----------------------------------------------------

    try:

        latitude = float(
            data.get("latitude")
        )

        longitude = float(
            data.get("longitude")
        )

    except (TypeError, ValueError):

        return jsonify({

            "success": False,

            "message":
                "Invalid coordinates"

        }), 400

    # -----------------------------------------------------
    # GPS ACCURACY
    # -----------------------------------------------------

    accuracy = None

    try:

        if data.get("accuracy") is not None:

            accuracy = float(
                data.get("accuracy")
            )

            if accuracy < 0:
                accuracy = None

    except (TypeError, ValueError):

        accuracy = None

    # -----------------------------------------------------
    # IGNORE INACCURATE GPS READINGS
    # -----------------------------------------------------

    if (
        accuracy is not None
        and
        accuracy > MAX_GPS_ACCURACY_METERS
    ):

        return jsonify({

            "success": False,

            "message":
                f"GPS accuracy too low "
                f"({accuracy:.1f} m). "
                f"Reading ignored."

        })

    now = datetime.now()

    # -----------------------------------------------------
    # DISTANCE AND SPEED CHECK
    # -----------------------------------------------------

    distance = 0

    if (
        last_latitude is not None
        and
        last_longitude is not None
    ):

        distance = calculate_distance(

            last_latitude,

            last_longitude,

            latitude,

            longitude

        )

        # Ignore huge GPS jumps
        if distance > MAX_GPS_JUMP_METERS:

            return jsonify({

                "success": False,

                "message":
                    "GPS jump ignored"

            })

        # Calculate speed
        if hasattr(
            save_location,
            "last_time"
        ):

            time_difference = (

                now
                -
                save_location.last_time

            ).total_seconds()

            if time_difference > 0:

                speed_kmh = (

                    distance
                    /
                    time_difference
                    *
                    3.6

                )

                # Ignore unrealistic speed
                if speed_kmh > MAX_REALISTIC_SPEED_KMH:

                    return jsonify({

                        "success": False,

                        "message":
                            "Unrealistic GPS speed ignored"

                    })

                current_speed = speed_kmh

    else:

        current_speed = 0.0

    # -----------------------------------------------------
    # REVERSE GEOCODING
    # -----------------------------------------------------

    city = "Unknown"

    country = "Unknown"

    try:

        location = geolocator.reverse(

            f"{latitude}, {longitude}",

            language="en",

            timeout=10

        )

        if location:

            address = location.raw.get(
                "address",
                {}
            )

            city = (

                address.get("city")

                or

                address.get("town")

                or

                address.get("village")

                or

                address.get("municipality")

                or

                "Unknown"

            )

            country = (

                address.get("country")

                or

                "Unknown"

            )

    except Exception:

        pass

    # -----------------------------------------------------
    # SAVE TO CSV
    # -----------------------------------------------------

    with open(

        "location_history.csv",

        "a",

        newline="",

        encoding="utf-8"

    ) as file:

        writer = csv.writer(file)

        writer.writerow([

            now.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            latitude,

            longitude,

            city,

            country,

            accuracy

            if accuracy is not None

            else ""

        ])

    # -----------------------------------------------------
    # UPDATE CURRENT STATE
    # -----------------------------------------------------

    last_latitude = latitude

    last_longitude = longitude

    save_location.last_time = now

    # -----------------------------------------------------
    # REGENERATE HISTORY MAP
    # -----------------------------------------------------

    try:

        subprocess.Popen(

            [

                sys.executable,

                "gps_map.py"

            ],

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL

        )

    except Exception:

        pass

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return jsonify({

        "success": True,

        "latitude":
            latitude,

        "longitude":
            longitude,

        "city":
            city,

        "country":
            country,

        "accuracy":
            accuracy,

        "speed":
            round(
                current_speed,
                2
            )

    })


# ---------------------------------------------------------
# HISTORY MAP
# ---------------------------------------------------------

@app.route(
    "/gps_history_map.html"
)
def gps_history_map():

    return send_file(
        "gps_history_map.html"
    )


# ---------------------------------------------------------
# RUN APPLICATION
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True
    )