# Aerial Threat Intelligence & Detection System

## Overview
This project is an advanced **DBMS-based Threat Intelligence System** designed to simulate real-time telemetry processing, threat classification, and alert handling for aerial objects. Built around relational database paradigms, it relies heavily on event-driven SQL architecture (Triggers, Condition Logic) to process raw data and cascade actionable intelligence to a tactical radar dashboard.

---

## System Architecture

The core of the system follows a classic Model-View-Controller (MVC) structure, heavily offloading business logic directly to the database layer to strictly enforce data integrity and rapid processing.
- **Backend Frame:** Python 3.x with Flask to handle routing and database interactions.
- **Data Persistence Strategy:** SQLite3, utilizing dynamic DDL execution for self-healing schema creation.
- **Frontend / View:** Jinja2 templating rendering a custom 8-bit military interface. Pure vanilla CSS ensures minimal overhead, utilizing inline SVGs and mathematical pseudo-random animations to mimic physical radar hardware.

---

## Getting Started (Run Locally)

Follow these steps to deploy the application instance in a local sandbox environment.

### 1. Prerequisites
Ensure you have **Python 3.x** installed. You can download it from [python.org](https://www.python.org/).

### 2. Setup & Installation
Open your terminal/command prompt in the `drone-bombing` directory and run:

```bash
# Optional: Create a localized virtual environment
python -m venv venv
venv\Scripts\activate   # For Windows
# source venv/bin/activate # For Mac/Linux

# Install server framework dependencies
pip install flask
```

### 3. Deploy the System
Start the application server natively:

```bash
python app.py
```

### 4. Access the Dashboard
Open your web browser and navigate directly to the application boot sequence:
**http://127.0.0.1:5000/**
*(You will be securely routed through the `/` bootnode directly into the `/defencepage/login` authorization portal).*

---

## Relational Entity Architecture

The database is fully normalized and automatically provisioned on startup via `db/setup.sql`.

### 1. `Aerial_Objects` (Telemetry Fact Table)
Stores incoming physical radar data mimicking live object acquisition.
- `object_id` (PK): Unique auto-incrementing identifier.
- `type`: Equipment classification (`Missile`, `Aircraft`, `Drone`).
- `speed`: Target velocity in km/h.
- `altitude`: Z-axis metric tracking in meters.
- `detected_at`: Automatic UTC insertion tracking.

### 2. `Threat_Assessment` (Derived Dimension Table)
Stores analytical data processed exclusively against `Aerial_Objects` telemetry thresholds.
- `assessment_id` (PK)
- `object_id` (FK): Links 1:1 with the telemetry table.
- `threat_level`: Categorical urgency (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- `priority_score`: Calculated integer metric (0-100) determining UI progress-bar load and indexing order.

### 3. `Alerts` (Notification Aggregation)
Action queues strictly populated based on highly dangerous shifts in the `Threat_Assessment` table.
- `alert_id` (PK)
- `object_id` (FK)
- `message`: Encrypted strings alerting operators of immediate dangers.

---

## Core SQL Mechanics & Triggers

To simulate real-time processing without requiring heavy backend polling, the system runs on **SQL Triggers**. These triggers catch telemetry inserts and instantly execute cascaded logic tables.

### Trigger 1: `auto_assess_threat` (`AFTER INSERT ON Aerial_Objects`)
As soon as telemetry hits the database, a mathematical matrix classifies it:
- **`CRITICAL` (Score 100):** If `Type == Missile` AND `Speed > 900`.
- **`HIGH` (Score 80):** If `Speed > 800` AND `Altitude < 2000` (Low-flying, fast objects indicating strike approach).
- **`MEDIUM` (Score 50):** If target exceeds standard atmospheric speed `> 400`.
- **`LOW` (Score 20):** Baseline objects monitoring structure.

### Trigger 2: `threat_alert_trigger` (`AFTER INSERT ON Threat_Assessment`)
Immediately queues alerts in a secondary workflow if the aforementioned table detects `CRITICAL` or `HIGH` anomalies. Promotes system decoupling by keeping threat mathematics separated from notification distribution.

---

## Application Workflows & Features

1. **Bootnode Routing (`/`)**: Intercepts initial requests, supplying a 7-second Terminal CSS boot sequence masking system "loading" before establishing a dynamic redirect to the login authorization portal.
2. **Authorization Portal (`/defencepage/login`)**: A secure authentication layer requiring Operative ID, Passcode, and Clearance Level (Analyst, Commander, General) before granting access to the tactical dashboard.
3. **Dashboard Overview (`/defencepage`)**: Employs Python string formatting (`%04d` ID padding) and dynamic Jinja loops to iterate over reverse-chronological SQL cursors. Employs mathematically scaled, color-shifting healthbars derived directly from the SQL `priority_score`.
4. **Target Deployment (`/defencepage/add`)**: Provides front-facing forms interfacing securely with POST routes to inject data directly into `Aerial_Objects`, igniting the SQL trigger chain.
5. **Data Manipulation (`/defencepage/edit/<id>`)**: Fetches singletons against the PK and loads them into a targeted `edit.html` interface. Running custom Python recalculations to mimic SQL conditions, forcefully syncing the `Threat_Assessment` table state back into alignment before updating.
6. **Entity Deletion (`/defencepage/delete/<id>`)**: Enforces manual referential drop procedures, cleansing the `Aerial_Objects`, `Threat_Assessment`, and `Alerts` tables simultaneously per primary key, managing storage state and preventing ghost alerts.

---

## Technical Learnings
- **Trigger-Driven Logic Offloading:** Bypassing standard Python validation scripts to let database-level computational matrices handle security assessment securely natively.
- **RESTful Routing Architecture:** Safely sandboxing the application in a `/defencepage/` sub-structure avoiding index collision with the system loader. 
- **Vanilla CSS Emulation:** Developing non-blocking, JS-free animations (e.g. infinite looping `%3A` SVG Data-URL pixel camo textures, scanlines, and timed `step-end` pseudo-random CSS blinking).
