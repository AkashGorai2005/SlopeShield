# SlopeShield 🌿⛰️

> **AI-based landslide risk monitoring and decision-support system for Northeast India**

SlopeShield is a web-based platform designed to bring environmental, terrain, and historical landslide information together into one interface for landslide risk monitoring.

The project provides a dashboard for viewing risk conditions, exploring risk geographically, checking location-specific information, reviewing warnings, running what-if simulations, and generating reports.

---

## 👥 Team

### Team Name: **Hidden Variables**

| Team Member | Role |
|---|---|
| **Adrija Choudhury** | Frontend |
| **Akash Gorai** | Backend |
| **Pritam Nandi** | Backend |
| **Anindita Maji** | Database |
| **Pratima Shaw** | Machine Learning |
| **Abhishikta Mishra** | Machine Learning |

---

## 🎯 Project Objective

Landslides are influenced by multiple environmental and geographical factors. SlopeShield aims to make these factors easier to monitor by combining available data and model-generated risk information into a user-friendly web interface.

The system is intended to help users:

- Monitor landslide risk conditions
- Explore risk across locations
- View location-specific risk information
- Understand rainfall and environmental conditions
- Review early-warning information
- Run what-if scenarios
- View analytics and charts
- Generate and review reports
- Access important system information from a single dashboard

> **Note:** Risk values shown by the application are model-estimated indicators for monitoring and decision support. They should not be interpreted as a guarantee that a landslide will or will not occur.

---

## ✨ Main Features

### 🏠 Home
- Project introduction
- SlopeShield branding
- Quick navigation
- Risk overview
- Location-focused information

### 📊 Dashboard
- Overall risk overview
- Risk cards
- Monitoring information
- Rainfall/weather information
- Risk charts
- Recent changes
- Notifications and profile access

### 🗺️ Risk Map
- Geographic risk visualization
- Risk-based map information
- Map layer controls
- Location selection
- Location details

### ⚠️ Early Warnings
- Warning/alert information
- Risk-related notification indicators
- Alert cards for important conditions

### 🧪 What-If Simulation
- Interactive scenario testing
- Changes to selected environmental conditions
- Model-estimated risk comparison

### 📈 Analytics
- Risk-related charts and summaries
- Visual representation of project data

### 📄 Reports
- Report-oriented risk information
- Recent changes and monitoring summaries

### ℹ️ About
- Explanation of SlopeShield
- How the system works
- Team information

### 📱 Responsive UI
The interface is designed to work across desktop, tablet, and smaller-screen layouts.

---

## 🧩 System Overview

```text
                    ┌──────────────────────┐
                    │      SlopeShield     │
                    │     Web Frontend     │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        Risk Dashboard     Risk Map       What-If Simulation
              │                │                │
              └────────────────┼────────────────┘
                               │
                               ▼
                     Backend / API Layer
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
             Database      ML Service      Other Data
```

The frontend is responsible for presenting the application's monitoring and decision-support interface. Backend, database, and machine-learning components provide the supporting data and model functionality.

---

## 🛠️ Technology Stack

### Frontend
- React
- Vite
- JavaScript / JSX
- Tailwind CSS
- Lucide React
- React Router/navigation utilities

### Backend
- FastAPI
- Python

### Data / Database
- PostgreSQL

### Machine Learning
- Python-based ML components
- Landslide-risk estimation using environmental/geographical inputs

> The exact backend, database, and ML implementation may vary according to the project branch and team integration.

---

## 📁 Frontend Structure

```text
src/
├── components/
│   ├── AlertCard.jsx
│   ├── AppLayout.jsx
│   ├── DataStatusBanner.jsx
│   ├── EmptyState.jsx
│   ├── LayerControl.jsx
│   ├── LocationPanel.jsx
│   ├── Logo.jsx
│   ├── Navbar.jsx
│   ├── RiskCard.jsx
│   ├── RiskChart.jsx
│   ├── RiskLegend.jsx
│   ├── RiskMap.jsx
│   ├── RiskMapInner.jsx
│   ├── SearchBar.jsx
│   ├── Sidebar.jsx
│   ├── WhatIfSimulation.jsx
│   └── ...
├── context/
├── hooks/
├── pages/
│   ├── Home.jsx
│   └── ...
├── services/
├── utils/
├── App.jsx
├── main.jsx
└── styles.css
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_PROJECT_FOLDER>
```

### 2. Install frontend dependencies

```bash
npm install
```

### 3. Start the frontend

```bash
npm run dev
```

Vite will provide a local development URL, normally similar to:

```text
http://localhost:5173
```

### 4. Start the backend

From the project root, enter the backend directory:

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

The backend will normally be available at:

```text
http://127.0.0.1:8000
```

### 5. Build for production

From the project root:

```bash
npm run build
```

A successful build generates the production output in:

```text
dist/
```

---

## 🖥️ Screenshots

Recommended screenshots for the GitHub README are listed below.

Store them in:

```text
docs/
└── screenshots/
    ├── home.png
    ├── dashboard.png
    ├── risk-map.png
    ├── location-details.png
    ├── what-if-simulation.png
    ├── early-warnings.png
    ├── analytics.png
    ├── reports.png
    ├── about-team.png
    └── responsive.png
```

### Home

![SlopeShield Home](docs/screenshots/home.png)

### Dashboard

![SlopeShield Dashboard](docs/screenshots/dashboard.png)

### Risk Map

![SlopeShield Risk Map](docs/screenshots/risk-map.png)

### Location Details

![SlopeShield Location Details](docs/screenshots/location-details.png)

### What-If Simulation

![SlopeShield What-If Simulation](docs/screenshots/what-if-simulation.png)

### Early Warnings

![SlopeShield Early Warnings](docs/screenshots/early-warnings.png)

### Analytics

![SlopeShield Analytics](docs/screenshots/analytics.png)

### Reports

![SlopeShield Reports](docs/screenshots/reports.png)

### About & Team

![SlopeShield About Team](docs/screenshots/about-team.png)

### Responsive View

![SlopeShield Responsive View](docs/screenshots/responsive.png)

> If a screenshot is not available, remove its image section rather than leaving a broken image link.

---

## 🎥 Suggested Demo / Presentation Flow

For a project demonstration, the following order gives a clear overview:

1. **Home** — introduce SlopeShield
2. **Dashboard** — show the main monitoring view
3. **Risk Cards** — explain current risk information
4. **Risk Map** — demonstrate geographical risk visualization
5. **Location Details** — inspect a selected location
6. **Weather / Rainfall** — show environmental information
7. **Analytics** — demonstrate charts and trends
8. **What-If Simulation** — demonstrate scenario-based risk changes
9. **Early Warnings** — show alerts and warning information
10. **Reports** — demonstrate report/summary information
11. **About** — explain the system and introduce Hidden Variables

---

## 🔐 Important Project Boundaries

The project is divided between team members. Frontend work should remain separated from backend, database, and machine-learning implementation.

Frontend changes generally include:

- React components
- Pages
- Frontend styling
- Navigation
- Frontend layout
- Frontend state/UI behavior
- Frontend branding

Backend/API, database, and machine-learning files should be changed only by the responsible team members unless the team agrees otherwise.

---

## 🧪 Verification Checklist

Before submitting or demonstrating the project:

- [ ] Home page loads correctly
- [ ] Dashboard loads correctly
- [ ] Sidebar/navigation works
- [ ] Navbar search works
- [ ] Notifications work
- [ ] Profile/auth controls work
- [ ] Risk Map loads correctly
- [ ] Location selection works
- [ ] What-If Simulation works
- [ ] Early Warnings page works
- [ ] Analytics page works
- [ ] Reports page works
- [ ] About page loads
- [ ] Team information is visible
- [ ] Responsive layout works
- [ ] Backend connection works when backend is running
- [ ] Frontend handles backend/API errors without crashing
- [ ] `npm run build` completes successfully

---

## 📌 Project Status

**Status:** Frontend integration and demonstration ready, subject to final team integration and repository verification.

---

## 👨‍💻 Team

**Hidden Variables**

Built by:

- Adrija Choudhury — Frontend
- Akash Gorai — Backend
- Pritam Nandi — Backend
- Anindita Maji — Database
- Pratima Shaw — Machine Learning
- Abhishikta Mishra — Machine Learning

---

## 📜 License

Add the project's official license here if your team has selected one.

Example:

```text
MIT License
```

Do not add a license unless the team has agreed to use it.
