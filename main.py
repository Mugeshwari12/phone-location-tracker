import csv
import folium

print("Phone Location Tracker")
print("Creating location history map...")

locations = []

with open("location_history.csv", "r", encoding="utf-8") as file:
    reader = csv.reader(file)

    for row in reader:
        if len(row) >= 5:
            time = row[0]
            latitude = float(row[1])
            longitude = float(row[2])
            city = row[3]
            country = row[4]

            locations.append(
                (time, latitude, longitude, city, country)
            )

if locations:
    latest = locations[-1]

    map = folium.Map(
        location=[latest[1], latest[2]],
        zoom_start=12
    )

    for time, latitude, longitude, city, country in locations:
        folium.Marker(
            [latitude, longitude],
            popup=f"Time: {time}<br>City: {city}<br>Country: {country}"
        ).add_to(map)Ś

    map.save("location_history_map.html")

    print("Map created successfully!")
    print("Open location_history_map.html")

else:
    print("No location history found.")