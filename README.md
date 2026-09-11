# 📱 Phone GPS Tracker

## Real-Time Location Tracking System

A Python Flask-based GPS tracking application that captures the user's current location, stores GPS coordinates, calculates travel distance, and displays the current and historical route on interactive maps.

## 🚀 Features

- 📍 Real-time GPS location tracking
- 🌐 Browser-based location detection
- 🗺️ Interactive map using Leaflet
- 🛣️ Historical GPS route visualization
- 💾 GPS location history stored in CSV
- 📏 Automatic distance calculation
- 📌 Ignores movements smaller than 10 meters
- 🛡️ Filters unrealistic GPS jumps
- 📊 Displays today's distance and GPS point count
- 🏙️ Converts GPS coordinates into city and country names
- ▶️ Start and stop tracking controls

## 🛠️ Technologies Used

- **Python**
- **Flask**
- **HTML**
- **CSS**
- **JavaScript**
- **Leaflet.js**
- **Folium**
- **GeoPy**
- **OpenStreetMap**
- **CSV**

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
└── venv/
```

## ⚙️ How It Works

1. The user opens the GPS Tracker webpage.
2. The browser requests permission to access the device's location.
3. JavaScript obtains the latitude and longitude.
4. The coordinates are sent to the Flask server.
5. Flask validates the GPS coordinates.
6. Movements smaller than 10 meters are ignored.
7. Valid locations are stored in `location_history.csv`.
8. GeoPy is used to identify the city and country.
9. GPS statistics such as today's distance are calculated.
10. Leaflet displays the current location on an interactive map.
11. A historical map displays previously recorded GPS locations and the route.

## ▶️ How to Run

### 1. Open the project folder

Open the project in VS Code.

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

When the browser asks for permission to access your location, select **Allow**.

### 6. Start tracking

Click:

**▶ Start Tracking**

The application will begin collecting GPS locations.

## 📊 GPS Data

GPS history is stored in:

```text
location_history.csv
```

Each record contains:

```text
Timestamp, Latitude, Longitude, City, Country
```

## 🗺️ Maps

The project provides two map views:

### Current Location Map

Displays the user's current GPS position.

### History Map

Displays previously recorded locations and the route traveled.

Click:

**🗺️ View History Map**

to open the historical route.

## 🔐 Location Privacy

This application uses browser-provided location data. Location access requires explicit permission from the user.

GPS history is stored locally in the project's CSV file.

## 🔮 Future Improvements

Possible future enhancements include:

- User login and authentication
- Database storage using SQLite/MySQL
- Live route tracking
- Speed calculation
- Distance reports by date
- Location history filtering
- Mobile-friendly interface
- Export GPS data to Excel
- Data visualization dashboard
- Deployment to a cloud server
- Multiple-user tracking

## 👩‍💻 Project Status

**Completed — Working Prototype**

The application successfully captures GPS coordinates, stores location history, calculates travel distance, and displays current and historical locations on interactive maps.