# 🇮🇳 India Disaster Monitoring System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django&logoColor=white"/>
  <img src="https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white"/>
  <img src="https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white"/>
  <img src="https://img.shields.io/badge/REST_API-Django-red?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/License-MIT-success?style=for-the-badge"/>
</p>

<p align="center">
  <b>A Full-Stack Disaster Monitoring Platform for India</b><br>
  Real-time weather monitoring, earthquake tracking, flood alerts, cyclone advisory simulation, REST APIs, and interactive dashboards.
</p>

---

## 📖 Overview

The **India Disaster Monitoring System** is a full-stack disaster intelligence platform designed to monitor multiple natural hazards across India from a single dashboard.

The system automatically collects live environmental data, stores it in a centralized MySQL database, analyzes potential disaster conditions, and exposes the information through both a **Flask Dashboard** and a **Django REST API**.

Unlike simple dashboards, this project combines:

- 🌧 Live Rainfall Monitoring
- 🌊 Flood Alert Generation
- 🌍 Earthquake Tracking
- 🌪 Cyclone Advisory Monitoring
- 📊 Data Visualization
- 🔌 REST API
- 🗄 Centralized Database
- 📈 Automated Daily Reports

This project demonstrates backend development, API development, database design, automation, and frontend visualization in one integrated application.

---

# ✨ Features

## 🌧 Rainfall Monitoring

- Live rainfall data using OpenWeatherMap API
- Temperature monitoring
- Humidity monitoring
- Latitude & Longitude tracking
- Covers all Indian States & Union Territories

---

## 🌊 Flood Monitoring

- River water level monitoring
- Warning level detection
- Danger level detection
- Automatic flood alert generation
- Historical flood records

---

## 🌍 Earthquake Monitoring

- Live USGS Earthquake Feed
- Magnitude ≥ 5 filtering
- Last 30-day earthquake records
- Location tracking
- Magnitude analysis

---

## 🌪 Cyclone Advisory

- Seasonal cyclone monitoring
- IMD-style advisory simulation
- Warning generation
- Future integration ready for live APIs

---

## 📊 Analytics

Generate useful reports such as:

- Highest rainfall states
- Flood affected districts
- Earthquake history
- Rainfall trends
- Daily reports
- Disaster summaries

---

# 🏗 System Architecture

```text
                    +----------------------+
                    | OpenWeatherMap API   |
                    +----------+-----------+
                               |
                               |
                    +----------v-----------+
                    |  Python Collector    |
                    +----------+-----------+
                               |
          +--------------------+--------------------+
          |                                         |
+---------v---------+                     +----------v----------+
| USGS Earthquake   |                     | Cyclone Simulator   |
| Live API          |                     | Flood Simulator     |
+---------+---------+                     +----------+----------+
          |                                         |
          +--------------------+--------------------+
                               |
                    +----------v-----------+
                    |     MySQL Database   |
                    +----------+-----------+
                               |
             +-----------------+-----------------+
             |                                   |
+------------v------------+         +------------v------------+
| Django REST API         |         | Flask Dashboard         |
+------------+------------+         +------------+------------+
             |                                   |
             |                                   |
      +------v------+                    +-------v-------+
      | JavaScript  |                    | Interactive   |
      | Frontend    |                    | Web Dashboard |
      +-------------+                    +---------------+
```

---

# 📌 Key Highlights

✅ Live Weather Monitoring

✅ Real-Time Earthquake Tracking

✅ Automatic Flood Alerts

✅ Cyclone Advisory System

✅ Flask Dashboard

✅ Django REST API

✅ Interactive Maps

✅ Charts & Analytics

✅ MySQL Relational Database

✅ Automated Daily Reports

---

# 📂 Repository Structure

```text
India-Disaster-Monitoring-System/

│
├── india-disaster-monitoring/
│      Python Data Collection Engine
│      Flask Dashboard
│
├── disaster-api-django/
│      Django REST API
│
├── disaster-ui/
│      Standalone JavaScript Frontend
│
├── screenshots/
│      Dashboard Images
│
└── README.md
```

---

## 📸 Project Preview

> **Dashboard screenshots will be added here**

### Flask Dashboard

<img src="screenshots/flask-dashboard.png" width="900">

---

### Disaster Map

<img src="screenshots/map.png" width="900">

---

### Analytics Dashboard

<img src="screenshots/chart.png" width="900">

---
# ⚙️ Installation

## 📋 Prerequisites

Before running this project, make sure the following software is installed:

- Python **3.9+**
- MySQL **8.0+**
- Git
- pip
- Virtual Environment (Recommended)

---

# 🚀 Getting Started

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/India-Disaster-Monitoring-System.git

cd India-Disaster-Monitoring-System
```

---

## 2️⃣ Create a Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

Install dependencies for each component.

### Flask Backend

```bash
cd india-disaster-monitoring

pip install -r requirements.txt
```

### Django API

```bash
cd ../disaster-api-django

pip install -r requirements.txt
```

---

# 🗄 Database Setup

Create a MySQL database.

```sql
CREATE DATABASE disaster_monitoring;
```

Update your MySQL credentials inside the configuration file.

Example:

```python
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "your_password"
DB_NAME = "disaster_monitoring"
```

---

# ▶ Running the Project

## Step 1

Start the Flask data collector.

```bash
cd india-disaster-monitoring

python app.py
```

---

## Step 2

Run the scheduler (optional).

```bash
python scheduler.py
```

This will automatically collect disaster data and generate daily reports.

---

## Step 3

Start Django REST API.

```bash
cd disaster-api-django

python manage.py migrate

python manage.py runserver
```

API will be available at

```
http://127.0.0.1:8000/
```

---

## Step 4

Run the Frontend

Open

```
disaster-ui/index.html
```

or use

```bash
python -m http.server
```

---

# 🔌 REST API

## Rainfall

```
GET /api/rainfall/
```

Returns:

- Rainfall
- Temperature
- Humidity
- District
- State

---

## Flood Alerts

```
GET /api/flood-alerts/
```

Returns:

- River Name
- Water Level
- Warning Level
- Danger Level
- Alert Status

---

## Earthquakes

```
GET /api/earthquakes/
```

Returns

- Magnitude
- Location
- Latitude
- Longitude
- Event Time

---

## Cyclone Advisories

```
GET /api/cyclones/
```

Returns

- Advisory
- State
- Severity
- Status

---

# 📊 Database Design

The project uses a **normalized relational database** consisting of multiple interconnected tables.

Main tables include:

- States
- Districts
- Rainfall
- Rivers
- Water Levels
- Flood Alerts
- Earthquakes
- Cyclone Advisories
- Daily Reports

Relationship Overview

```
States
   │
Districts
   │
Rainfall

Rivers
   │
Water Levels
   │
Flood Alerts

Earthquakes

Cyclone Alerts

Daily Reports
```

---

# 📈 SQL Analysis

Example analytical queries supported by the project:

✅ Highest Rainfall State

✅ Highest Rainfall District

✅ Districts Under Flood Alert

✅ Recent Earthquakes

✅ River Water Levels

✅ Daily Disaster Summary

✅ 30-Day Rainfall Trends

---

# 🛠 Tech Stack

## Backend

- Python
- Flask
- Django
- Django REST Framework

## Database

- MySQL

## Frontend

- HTML5
- CSS3
- JavaScript
- Leaflet.js
- Chart.js

## Libraries

- pandas
- requests
- mysql-connector-python
- schedule

---

# 📂 Folder Structure

```
India-Disaster-Monitoring-System/

├── india-disaster-monitoring/
│   ├── collector.py
│   ├── scheduler.py
│   ├── app.py
│   ├── requirements.txt
│
├── disaster-api-django/
│   ├── manage.py
│   ├── api/
│   ├── requirements.txt
│
├── disaster-ui/
│   ├── css/
│   ├── js/
│   ├── index.html
│
├── screenshots/
│
└── README.md
```

---

# 💡 Project Use Cases

- Disaster Monitoring Centers
- Educational Projects
- Weather Analysis
- REST API Learning
- Data Visualization
- GIS Demonstration
- Backend Development Practice
- Full Stack Portfolio Project 

---

# 📸 Screenshots

Visual previews help visitors quickly understand your project.

## 🖥 Flask Dashboard

<p align="center">
<img src="screenshots/flask-dashboard.png" width="900">
</p>

---

## 🌍 Disaster Monitoring Map

<p align="center">
<img src="screenshots/disaster-map.png" width="900">
</p>

---

## 📊 Analytics Dashboard

<p align="center">
<img src="screenshots/analytics.png" width="900">
</p>

---

## 📱 Django REST API

<p align="center">
<img src="screenshots/api.png" width="900">
</p>

---

# 🎥 Demo

> Add a short demo GIF or screen recording here.

Example:

```
demo/demo.gif
```

or

```
https://youtu.be/your-demo-video
```

---

# 🌟 Project Highlights

✔ Full Stack Application

✔ Python Automation

✔ Django REST API

✔ Flask Dashboard

✔ Interactive Maps

✔ SQL Database Design

✔ Data Collection Automation

✔ Disaster Analytics

✔ Clean Project Architecture

✔ Recruiter Friendly Portfolio Project

---

# 🚀 Future Improvements

This project can be extended with several real-world features.

- [ ] Docker Support
- [ ] Kubernetes Deployment
- [ ] AWS Deployment
- [ ] SMS Alerts
- [ ] Email Notifications
- [ ] WhatsApp Alerts
- [ ] AI-based Disaster Prediction
- [ ] Machine Learning Risk Analysis
- [ ] Satellite Image Integration
- [ ] Mobile Application
- [ ] User Authentication
- [ ] Admin Dashboard
- [ ] Real IMD API Integration
- [ ] Real CWC API Integration

---

# 📊 Performance

Current implementation supports

- Multiple Disaster Types
- Modular Architecture
- REST API
- Scheduled Automation
- Centralized Database
- Interactive Visualization

---

# 🤝 Contributing

Contributions are welcome!

To contribute:

```bash
Fork this repository

Create a feature branch

git checkout -b feature-name

Commit your changes

git commit -m "Added new feature"

Push

git push origin feature-name

Open a Pull Request
```

Please make sure your code follows clean coding practices.

---

# 🐞 Reporting Issues

Found a bug?

Please open an issue with:

- Description
- Expected Behaviour
- Actual Behaviour
- Steps to Reproduce

---

# ⭐ Support

If you found this project useful,

please consider giving it a ⭐ on GitHub.

It really helps!

---

# 📚 Learning Outcomes

This project demonstrates practical experience with:

- Python Programming
- Flask Development
- Django REST Framework
- REST APIs
- MySQL
- SQL Queries
- Scheduled Automation
- Data Collection
- API Integration
- Leaflet Maps
- Chart.js
- Full Stack Development

---

# 🙏 Acknowledgements

Special thanks to the following public data providers:

- OpenWeatherMap
- USGS Earthquake Program

This project is built for educational and portfolio purposes.

---

# 📄 License

This project is licensed under the MIT License.

See the **LICENSE** file for details.

---

# 👨‍💻 Author

**Ibha Saini**

Computer Science Student

Passionate about

- Python
- Django
- Machine Learning
- Artificial Intelligence
- Data Science
- Full Stack Development

GitHub:
https://github.com/YOUR_USERNAME

LinkedIn:
https://linkedin.com/in/YOUR_PROFILE

---

<p align="center">

Made with ❤️ using Python, Django, Flask and MySQL

⭐ Star this repository if you found it useful!

</p>