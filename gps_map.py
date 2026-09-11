import csv
import folium
from geopy.distance import geodesic
from datetime import datetime


print("GPS History Map")
print("Loading saved locations...")


# ==================================================
# GPS locations
# ==================================================

locations = []


# ==================================================
# Maximum realistic travel speed
# ==================================================

MAX_SPEED_KMH = 150


# ==================================================
# Read GPS history
# ==================================================

try:

    with open(
        "location_history.csv",
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.reader(file)

        for row in reader:

            if len(row) >= 3:

                try:

                    time = row[0]

                    latitude = float(row[1])

                    longitude = float(row[2])

                    city = (
                        row[3]
                        if len(row) >= 4
                        else "Unknown"
                    )

                    country = (
                        row[4]
                        if len(row) >= 5
                        else "Unknown"
                    )

                    # Check valid coordinates

                    if (
                        -90 <= latitude <= 90
                        and -180 <= longitude <= 180
                    ):

                        locations.append(
                            (
                                time,
                                latitude,
                                longitude,
                                city,
                                country
                            )
                        )

                except ValueError:

                    continue

except FileNotFoundError:

    print("No GPS history file found.")
    print("Create location_history.csv first.")


# ==================================================
# Check whether GPS locations exist
# ==================================================

if locations:

    # ==================================================
    # Sort locations by time
    # ==================================================

    locations.sort(
        key=lambda x: x[0]
    )


    # ==================================================
    # Filter suspicious GPS jumps
    # ==================================================

    filtered_locations = [
        locations[0]
    ]

    maximum_speed = 0.0

    ignored_points = 0


    for location in locations[1:]:

        previous = filtered_locations[-1]


        # ==================================================
        # Convert timestamps
        # ==================================================

        try:

            previous_time = datetime.strptime(
                previous[0],
                "%Y-%m-%d %H:%M:%S"
            )

            current_time = datetime.strptime(
                location[0],
                "%Y-%m-%d %H:%M:%S"
            )

        except ValueError:

            ignored_points += 1

            continue


        # ==================================================
        # Calculate time difference
        # ==================================================

        time_difference = (
            current_time - previous_time
        ).total_seconds()


        # ==================================================
        # Calculate distance
        # ==================================================

        distance = geodesic(
            (
                previous[1],
                previous[2]
            ),
            (
                location[1],
                location[2]
            )
        ).meters


        # ==================================================
        # Calculate speed
        # ==================================================

        if time_difference > 0:

            speed_kmh = (
                distance / time_difference
            ) * 3.6

        else:

            speed_kmh = 999999


        # ==================================================
        # Accept realistic movement
        # ==================================================

        if speed_kmh <= MAX_SPEED_KMH:

            filtered_locations.append(
                location
            )

            if speed_kmh > maximum_speed:

                maximum_speed = speed_kmh

        else:

            ignored_points += 1


    # Replace with filtered locations

    locations = filtered_locations


    # ==================================================
    # Latest valid location
    # ==================================================

    latest = locations[-1]


    # ==================================================
    # Calculate total distance
    # ==================================================

    total_distance = 0.0


    for i in range(
        1,
        len(locations)
    ):

        previous_point = (
            locations[i - 1][1],
            locations[i - 1][2]
        )

        current_point = (
            locations[i][1],
            locations[i][2]
        )

        total_distance += geodesic(
            previous_point,
            current_point
        ).meters


    # ==================================================
    # Today's locations
    # ==================================================

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )


    today_locations = [

        location

        for location in locations

        if location[0].startswith(today)

    ]


    # ==================================================
    # Calculate today's distance
    # ==================================================

    today_distance = 0.0


    for i in range(
        1,
        len(today_locations)
    ):

        previous_point = (
            today_locations[i - 1][1],
            today_locations[i - 1][2]
        )

        current_point = (
            today_locations[i][1],
            today_locations[i][2]
        )

        today_distance += geodesic(
            previous_point,
            current_point
        ).meters


    # ==================================================
    # Convert distance to kilometres
    # ==================================================

    total_distance_km = (
        total_distance / 1000
    )

    today_distance_km = (
        today_distance / 1000
    )


    # ==================================================
    # Create map
    # ==================================================

    gps_map = folium.Map(

        location=[
            latest[1],
            latest[2]
        ],

        zoom_start=15

    )


    # ==================================================
    # Draw GPS route
    # ==================================================

    route_points = [

        [
            latitude,
            longitude
        ]

        for (
            time,
            latitude,
            longitude,
            city,
            country
        ) in locations

    ]


    if len(route_points) > 1:

        folium.PolyLine(

            route_points,

            tooltip="GPS Movement History",

            weight=5

        ).add_to(gps_map)


    # ==================================================
    # Add GPS point markers
    # ==================================================

    for index, location in enumerate(locations):

        time = location[0]

        latitude = location[1]

        longitude = location[2]

        city = location[3]

        country = location[4]


        # Calculate speed from previous point

        point_speed = 0.0


        if index > 0:

            previous = locations[index - 1]


            try:

                previous_time = datetime.strptime(
                    previous[0],
                    "%Y-%m-%d %H:%M:%S"
                )

                current_time = datetime.strptime(
                    time,
                    "%Y-%m-%d %H:%M:%S"
                )

                time_difference = (
                    current_time - previous_time
                ).total_seconds()


                if time_difference > 0:

                    distance = geodesic(

                        (
                            previous[1],
                            previous[2]
                        ),

                        (
                            latitude,
                            longitude
                        )

                    ).meters


                    point_speed = (
                        distance / time_difference
                    ) * 3.6


                    if point_speed > MAX_SPEED_KMH:

                        point_speed = 0.0


            except ValueError:

                point_speed = 0.0


        # Create popup

        popup_text = f"""
        <div style="width:220px">

        <h4>📍 GPS Point {index + 1}</h4>

        <b>Time:</b><br>
        {time}<br><br>

        <b>Latitude:</b><br>
        {latitude:.6f}<br><br>

        <b>Longitude:</b><br>
        {longitude:.6f}<br><br>

        <b>Location:</b><br>
        {city}, {country}<br><br>

        <b>Speed:</b><br>
        {point_speed:.2f} km/h

        </div>
        """


        folium.CircleMarker(

            location=[
                latitude,
                longitude
            ],

            radius=5,

            popup=folium.Popup(
                popup_text,
                max_width=300
            ),

            tooltip=f"GPS Point {index + 1}"

        ).add_to(gps_map)


    # ==================================================
    # Starting location
    # ==================================================

    first = locations[0]


    folium.Marker(

        [
            first[1],
            first[2]
        ],

        popup=f"""
        <b>🏁 Starting Location</b><br><br>

        Time: {first[0]}<br>

        Latitude: {first[1]:.6f}<br>

        Longitude: {first[2]:.6f}<br>

        Location: {first[3]}, {first[4]}
        """,

        tooltip="🏁 Start"

    ).add_to(gps_map)


    # ==================================================
    # Latest location
    # ==================================================

    folium.Marker(

        [
            latest[1],
            latest[2]
        ],

        popup=f"""
        <b>📍 Latest GPS Location</b><br><br>

        Time: {latest[0]}<br>

        Latitude: {latest[1]:.6f}<br>

        Longitude: {latest[2]:.6f}<br>

        Location: {latest[3]}, {latest[4]}
        """,

        tooltip="📍 Latest Location"

    ).add_to(gps_map)


    # ==================================================
    # Summary panel
    # ==================================================

    summary_html = f"""

    <div style="
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 9999;
        background-color: white;
        padding: 15px;
        border: 2px solid black;
        border-radius: 8px;
        font-size: 14px;
        line-height: 1.6;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    ">

        <b>📱 GPS Tracker Summary</b>

        <hr>

        <b>Valid GPS Points:</b>
        {len(locations)}

        <br>

        <b>Ignored GPS Jumps:</b>
        {ignored_points}

        <br>

        <b>Maximum Speed:</b>
        {maximum_speed:.2f} km/h

        <br>

        <b>Total Distance:</b>
        {total_distance_km:.2f} km

        <br>

        <b>Today's Distance:</b>
        {today_distance_km:.2f} km

        <br>

        <b>Latest Location:</b>
        {latest[3]}, {latest[4]}

        <br>

        <b>Latest Time:</b>
        {latest[0]}

    </div>

    """


    gps_map.get_root().html.add_child(

        folium.Element(
            summary_html
        )

    )


    # ==================================================
    # Save map
    # ==================================================

    gps_map.save(
        "gps_history_map.html"
    )


    # ==================================================
    # Console output
    # ==================================================

    print(
        "GPS history map created successfully!"
    )

    print(
        f"Valid GPS points: {len(locations)}"
    )

    print(
        f"Ignored GPS jumps: {ignored_points}"
    )

    print(
        f"Maximum speed: {maximum_speed:.2f} km/h"
    )

    print(
        f"Total distance travelled: "
        f"{total_distance_km:.2f} km"
    )

    print(
        f"Today's distance: "
        f"{today_distance_km:.2f} km"
    )

    print(
        f"Latest location: "
        f"{latest[3]}, {latest[4]}"
    )

    print(
        "Open gps_history_map.html"
    )


else:

    print(
        "No GPS locations found."
    )