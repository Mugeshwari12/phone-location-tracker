# 📱 Phone GPS Tracker

## Real-Time Location Tracking System

A **Python Flask-based GPS tracking application** that captures the user's real-time location, stores GPS coordinates, calculates travel distance, filters inaccurate GPS data, and visualizes current and historical routes on interactive maps.

This project demonstrates practical use of **Python, Flask, JavaScript, browser geolocation, CSV data storage, geospatial calculations, and interactive maps**.

---

## 🚀 Features

- 📍 Real-time GPS location tracking
- 🗺️ Interactive map using Leaflet.js
- 🛣️ Historical GPS route visualization
- 💾 GPS location history stored in CSV
- 📏 Automatic travel-distance calculation
- 🎯 Ignores movements smaller than 10 meters
- 🛡️ Filters unrealistic GPS jumps
- 📊 Displays GPS tracking statistics
- 🌍 Converts GPS coordinates into city and country names
- ▶️ Start and stop tracking controls
- 📤 Export GPS location history
- 📅 Daily tracking statistics
- 📈 Tracking duration and speed statistics

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| **Python** | Backend programming |
| **Flask** | Web application framework |
| **HTML** | Webpage structure |
| **CSS** | User interface styling |
| **JavaScript** | GPS location collection |
| **Leaflet.js** | Interactive maps |
| **Folium** | Historical route maps |
| **GeoPy** | Reverse geocoding |
| **OpenStreetMap** | Map data |
| **CSV** | Location data storage |

---

## 📂 Project Structure

```text
phone_location_tracker/
│
├── app.py
├── gps.html
├── gps_map.py
├── gps_history_map.html
├── location_history.csv
├── README.md
├── .gitignore
└── venv/
```

---

## ⚙️ How It Works

1. The user opens the GPS Tracker web application.
2. The browser requests permission to access the device's location.
3. JavaScript obtains the device's latitude and longitude.
4. GPS coordinates are sent to the Flask backend.
5. Flask validates the received GPS data.
6. Movements smaller than 10 meters are ignored.
7. Unrealistic GPS jumps are filtered.
8. Valid locations are stored in `location_history.csv`.
9. GeoPy converts coordinates into city and country information.
10. GPS statistics such as distance and speed are calculated.
11. Leaflet displays the current location on an interactive map.
12. A historical map displays previously recorded GPS locations and routes.

---

## ▶️ How to Run

### 1. Open the project folder

Open the project in **VS Code**.

### 2. Activate the virtual environment

In PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

### 3. Start the Flask server

```powershell
python app.py
```

### 4. Open the application

Open your browser and visit:

```text
http://127.0.0.1:5000
```

### 5. Allow location access

When the browser asks for location permission, select **Allow**.

### 6. Start tracking

Click:

**▶ Start Tracking**

The application will begin collecting GPS coordinates.

---

## 📊 GPS Data

GPS history is stored in:

```text
location_history.csv
```

Each record contains:

```text
Timestamp, Latitude, Longitude, City, Country
```

The application uses this data to calculate:

- Total distance
- Today's distance
- GPS point count
- Current speed
- Average speed
- Maximum speed
- Tracking duration
- Daily tracking statistics

---

## 🗺️ Maps

### Current Location Map

Displays the user's current GPS position using **Leaflet.js** and **OpenStreetMap**.

### Historical Route Map

Displays previously recorded GPS locations and the route traveled using **Folium**.

The historical map can be opened using:

**🗺️ View History Map**

---

## 🛡️ GPS Data Validation

The application includes basic GPS-data validation to improve tracking accuracy.

### Minimum Movement Filter

Locations that are less than **10 meters** from the previous saved location are ignored.

This helps prevent unnecessary duplicate GPS points.

### GPS Jump Detection

Unrealistic GPS movements are filtered using distance and speed validation.

This prevents incorrect GPS readings from producing extremely large travel distances.

---

## 📤 Data Export

The application provides an option to export the recorded GPS history for further analysis.

Exported data can be used for:

- Data analysis
- Visualization
- Travel-history review
- Future database integration

---

## 🎯 Project Objectives

- Build a real-time GPS tracking web application.
- Learn how browser geolocation works.
- Develop a Flask-based backend.
- Store and process GPS coordinates.
- Calculate travel distance and speed.
- Visualize geographical data on interactive maps.
- Handle inaccurate GPS readings.
- Build a practical project suitable for a software-development portfolio.

---

## 🔮 Future Improvements

Possible future versions could include:

- 👤 User authentication
- 🗄️ MySQL/PostgreSQL database integration
- ☁️ Cloud deployment
- 📱 Mobile application
- 🔐 Secure user-location storage
- 📍 Multiple-device tracking
- 📊 Advanced GPS analytics dashboard
- 📅 Weekly and monthly reports
- 🚨 Geofencing and location alerts
- ☁️ Real-time cloud synchronization

---

## 📌 Project Status

**Completed — Working Prototype**

The application successfully captures GPS coordinates, stores location history, validates GPS data, calculates travel distance and speed, and displays current and historical locations on interactive maps.

---

## 👩‍💻 Portfolio Project

This project was developed as a practical application of **Python, Flask, JavaScript, GPS technology, geospatial data processing, and interactive data visualization**.

It demonstrates the ability to build a complete application involving:

**Frontend → Backend → Data Storage → Data Processing → Visualization**

---