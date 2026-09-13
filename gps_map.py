import csv
import math
import os
import folium


CSV_FILE = "location_history.csv"
MAP_FILE = "gps_history_map.html"


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS coordinates in kilometers."""

    R = 6371.0

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    dlat = lat2 - lat1
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def load_gps_data():
    """Load GPS data from location_history.csv."""

    points = []

    if not os.path.exists(CSV_FILE):
        print(f"❌ {CSV_FILE} not found.")
        return points

    try:
        with open(
            CSV_FILE,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.reader(file)

            for row in reader:

                # Ignore empty rows
                if not row:
                    continue

                # Ignore possible header
                if row[0].strip().lower() == "timestamp":
                    continue

                # Need at least:
                # timestamp, latitude, longitude
                if len(row) < 3:
                    continue

                try:
                    timestamp = row[0].strip()

                    latitude = float(row[1].strip())
                    longitude = float(row[2].strip())

                    # City and country may or may not exist
                    city = row[3].strip() if len(row) >= 4 else "Unknown"
                    country = row[4].strip() if len(row) >= 5 else "Unknown"

                    # Accuracy may exist in newer rows
                    accuracy = None

                    if len(row) >= 6:
                        try:
                            accuracy = float(row[5].strip())
                        except ValueError:
                            accuracy = None

                    # Basic coordinate validation
                    if not (-90 <= latitude <= 90):
                        continue

                    if not (-180 <= longitude <= 180):
                        continue

                    points.append(
                        {
                            "timestamp": timestamp,
                            "latitude": latitude,
                            "longitude": longitude,
                            "city": city,
                            "country": country,
                            "accuracy": accuracy,
                        }
                    )

                except (ValueError, TypeError):
                    continue

    except Exception as e:
        print(f"❌ Error reading CSV: {e}")

    return points


def calculate_total_distance(points):
    """Calculate total distance of the recorded route."""

    total_distance = 0.0

    if len(points) < 2:
        return total_distance

    for i in range(1, len(points)):

        previous = points[i - 1]
        current = points[i]

        distance = haversine_distance(
            previous["latitude"],
            previous["longitude"],
            current["latitude"],
            current["longitude"]
        )

        total_distance += distance

    return total_distance


def create_map(points):
    """Create the GPS history map."""

    if not points:
        print("❌ No valid GPS points found.")
        return

    # First and latest locations
    first = points[0]
    latest = points[-1]

    # Calculate total route distance
    total_distance = calculate_total_distance(points)

    # Start map at latest location
    gps_map = folium.Map(
        location=[
            latest["latitude"],
            latest["longitude"]
        ],
        zoom_start=13,
        control_scale=True,
        tiles="OpenStreetMap"
    )

    # =========================================================
    # TITLE
    # =========================================================

    title_html = f"""
    <div style="
        position: fixed;
        top: 15px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 9999;
        background: white;
        padding: 15px 25px;
        border-radius: 12px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.25);
        font-family: Arial, sans-serif;
        text-align: center;
        min-width: 280px;
    ">

        <div style="
            font-size: 20px;
            font-weight: bold;
        ">
            📱 Phone GPS Tracker
        </div>

        <div style="
            font-size: 14px;
            color: #555;
            margin-top: 5px;
        ">
            GPS History & Route Map
        </div>

        <div style="
            margin-top: 10px;
            font-size: 14px;
        ">
            📍 GPS Points:
            <b>{len(points)}</b>
        </div>

        <div style="
            font-size: 14px;
            margin-top: 3px;
        ">
            🛣️ Total Distance:
            <b>{total_distance:.2f} km</b>
        </div>

    </div>
    """

    gps_map.get_root().html.add_child(
        folium.Element(title_html)
    )

    # =========================================================
    # ROUTE LINE
    # =========================================================

    route_coordinates = [
        [
            point["latitude"],
            point["longitude"]
        ]
        for point in points
    ]

    if len(route_coordinates) >= 2:

        folium.PolyLine(
            route_coordinates,
            weight=5,
            opacity=0.8,
            tooltip=f"Total Route: {total_distance:.2f} km"
        ).add_to(gps_map)

    # =========================================================
    # GPS POINTS
    # =========================================================

    for index, point in enumerate(points):

        accuracy_text = ""

        if point["accuracy"] is not None:
            accuracy_text = f"""
            <br>
            <b>🎯 Accuracy:</b>
            {point["accuracy"]:.1f} m
            """

        popup_html = f"""
        <div style="
            font-family: Arial, sans-serif;
            min-width: 220px;
        ">

            <h4 style="
                margin-top: 0;
                margin-bottom: 10px;
            ">
                📍 GPS Point #{index + 1}
            </h4>

            <b>🕒 Time:</b>
            {point["timestamp"]}

            <br><br>

            <b>🌐 Latitude:</b>
            {point["latitude"]:.6f}

            <br>

            <b>🌐 Longitude:</b>
            {point["longitude"]:.6f}

            <br><br>

            <b>📍 Location:</b>
            {point["city"]}, {point["country"]}

            {accuracy_text}

        </div>
        """

        folium.CircleMarker(
            location=[
                point["latitude"],
                point["longitude"]
            ],
            radius=5,
            popup=folium.Popup(
                popup_html,
                max_width=300
            ),
            tooltip=f"GPS Point #{index + 1}",
            fill=True,
            fill_opacity=0.8,
            weight=1
        ).add_to(gps_map)

    # =========================================================
    # START MARKER
    # =========================================================

    start_popup = f"""
    <div style="
        font-family: Arial, sans-serif;
        min-width: 220px;
    ">

        <h4 style="margin-top: 0;">
            🟢 Starting Location
        </h4>

        <b>🕒 Time:</b>
        {first["timestamp"]}

        <br><br>

        <b>🌐 Latitude:</b>
        {first["latitude"]:.6f}

        <br>

        <b>🌐 Longitude:</b>
        {first["longitude"]:.6f}

        <br><br>

        <b>📍 Location:</b>
        {first["city"]}, {first["country"]}

    </div>
    """

    folium.Marker(
        location=[
            first["latitude"],
            first["longitude"]
        ],
        popup=folium.Popup(
            start_popup,
            max_width=300
        ),
        tooltip="🟢 Starting Location",
        icon=folium.Icon(
            color="green",
            icon="play"
        )
    ).add_to(gps_map)

    # =========================================================
    # LATEST LOCATION MARKER
    # =========================================================

    latest_popup = f"""
    <div style="
        font-family: Arial, sans-serif;
        min-width: 220px;
    ">

        <h4 style="margin-top: 0;">
            🔴 Latest Location
        </h4>

        <b>🕒 Time:</b>
        {latest["timestamp"]}

        <br><br>

        <b>🌐 Latitude:</b>
        {latest["latitude"]:.6f}

        <br>

        <b>🌐 Longitude:</b>
        {latest["longitude"]:.6f}

        <br><br>

        <b>📍 Location:</b>
        {latest["city"]}, {latest["country"]}

        <br><br>

        <b>🛣️ Total Route:</b>
        {total_distance:.2f} km

    </div>
    """

    folium.Marker(
        location=[
            latest["latitude"],
            latest["longitude"]
        ],
        popup=folium.Popup(
            latest_popup,
            max_width=300
        ),
        tooltip="🔴 Latest Location",
        icon=folium.Icon(
            color="red",
            icon="flag"
        )
    ).add_to(gps_map)

    # =========================================================
    # FIT MAP TO ALL GPS POINTS
    # =========================================================

    if len(points) > 1:

        gps_map.fit_bounds(
            [
                [
                    point["latitude"],
                    point["longitude"]
                ]
                for point in points
            ]
        )

    # =========================================================
    # LEGEND
    # =========================================================

    legend_html = """
    <div style="
        position: fixed;
        bottom: 25px;
        left: 25px;
        z-index: 9999;
        background: white;
        padding: 14px 18px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.25);
        font-family: Arial, sans-serif;
        font-size: 13px;
    ">

        <div style="
            font-size: 15px;
            font-weight: bold;
            margin-bottom: 8px;
        ">
            Map Legend
        </div>

        <div>🟢 Starting Location</div>

        <div>🔴 Latest Location</div>

        <div>🔵 Recorded Route</div>

        <div>⚪ GPS Points</div>

    </div>
    """

    gps_map.get_root().html.add_child(
        folium.Element(legend_html)
    )

    # =========================================================
    # SAVE MAP
    # =========================================================

    gps_map.save(MAP_FILE)

    print()
    print("========================================")
    print("📱 GPS HISTORY MAP")
    print("========================================")
    print(f"✅ GPS points: {len(points)}")
    print(f"🛣️ Total distance: {total_distance:.2f} km")
    print(f"🟢 Start: {first['timestamp']}")
    print(f"🔴 Latest: {latest['timestamp']}")
    print(
        f"📍 Latest location: "
        f"{latest['city']}, {latest['country']}"
    )
    print(f"🗺️ Map created: {MAP_FILE}")
    print("========================================")


def main():
    print()
    print("📍 Loading GPS history...")

    points = load_gps_data()

    if not points:
        print("❌ No valid GPS points found.")
        return

    create_map(points)


if __name__ == "__main__":
    main()