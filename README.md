# Aerial Threat Detection (DBMS Project)
# Threat Intelligence System 

## Overview
This project is a **DBMS-based Threat Intelligence System** designed to simulate how aerial threats are detected, analyzed, and handled.

It stores aerial object data, classifies threat levels, and generates alerts to support decision-making.

---

## Database Structure

### Tables
1. **Aerial_Objects**
   - Stores detected aerial objects

2. **Sensor_Data**
   - Stores sensor readings (speed, altitude, etc.)

3. **Threat_Assessment**
   - Stores calculated threat levels

4. **Alerts**
   - Stores generated alerts

---

## Relationships
- One object → many sensor records (**1:N**)
- One object → one threat assessment (**1:1**)
- One threat → many alerts (**1:N**)

---

## Workflow
1. Aerial object is detected  
2. Sensor data is recorded  
3. Stored procedure evaluates threat  
4. Threat level is saved  
5. Trigger generates alert automatically  

---

## Features

✔️ **Stored Procedure**
- Automatically classifies threat level  

✔️ **Trigger**
- Generates alerts when threat is updated  

✔️ **SQL Queries**
- Retrieve threat insights and alerts  

✔️ **Optional UI**
- Basic interface for visualization  

---

## Threat Classification Logic

| Condition        | Threat Level |
|----------------|-------------|
| Missile        | CRITICAL    |
| High Speed     | HIGH        |
| Medium Speed   | MEDIUM      |
| Otherwise      | LOW         |

---

## Learning Outcomes

- Database design (PK, FK relationships)
- SQL procedures and triggers
- Real-world system modeling
- Decision-support systems using DBMS

---

## Conclusion

This project demonstrates how a **simplified defense-inspired system** can be built using DBMS to:
- Organize structured data  
- Automate threat analysis  
- Support decision-making through alerts  

---
