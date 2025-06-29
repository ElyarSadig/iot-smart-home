# 🏡 Room Comfort Optimization System

A smart, predictive indoor comfort management system built using modern Python tooling, combining **machine learning**, **FastAPI**, **HTMX**, and **async database operations** to monitor and optimize environmental conditions for multiple rooms in real-time.

---

## 📘 Project Overview

This project helps manage room comfort by:
- Accepting real-time sensor inputs via a web dashboard.
- Predicting current room temperatures using a **K-Nearest Neighbors (KNN)** model.
- Estimating user-preferred comfort temperature using a **Random Forest Regressor**.
- Allowing manual entry and tracking of user preferences.
- Automatically optimizing comfort through scheduled predictions.

It is modular, scalable, and includes persistent storage, ML model training, and prediction pipelines.

---

## 🧰 Technologies Used

| Category       | Technology                |
|----------------|---------------------------|
| **Backend**    | FastAPI, Python 3.10+     |
| **Frontend**   | HTMX, TailwindCSS, Jinja2 |
| **Database**   | SQLite with SQLAlchemy ORM |
| **ML Models**  | Scikit-learn (KNN, RF)    |
| **Scheduler**  | asyncio tasks             |
| **Utilities**  | pandas, numpy, joblib     |

---

## 🔧 Features

- 🔄 **Sensor input and real-time updates**
- 📈 **Temperature prediction** via KNN
- 💚 **Comfort preference estimation** via Random Forest
- 🧠 **Model training scripts** for each room
- ⏱️ **Async scheduled tasks** for periodic updates
- 🗃️ **Persistent storage** with async DB access

---

## 🧠 System Logic

### Sensor Data Management

Sensor inputs:
- `RelH`: Relative Humidity
- `L1`, `L2`: Light wavelengths
- `Occ`: Occupants (0-2)
- `Act`: Activity (0=n/a, 1=read, 2=stand, etc.)
- `Door`, `Win`: Binary door/window state

> `Temp` is predicted — **not manually input**.

---

### Temperature Prediction (KNN)

- Each room (`A`, `B`, `C`) has its own KNN model.
- Models are trained from CSV datasets in:
  ```
  data/
    ├── datasets-location_A/
    ├── datasets-location_B/
    └── datasets-location_C/
  ```

- Trained models saved to:
  ```
  models/
    ├── knn_model_A.joblib
    ├── knn_model_B.joblib
    └── knn_model_C.joblib
  ```

---

### Comfort Temperature Prediction (Random Forest)

- A single **Random Forest Regressor** trained on historical user preferences.
- Data sourced from either CSV (`comfort_temperature/room_temperature_dataset.csv`) or DB table `comfort_preference`.
- Predicts the **target comfort temperature** from environmental features.

---

### Background Prediction Scheduler

A looped async task that:
1. Pulls the latest sensor data from the DB for each room.
2. Predicts temperature using the relevant KNN model.
3. Updates the `Temp` field for that sensor row.

---

## 📂 Project Structure

```
project-root/
│
├── app/
│   ├── main.py
│   ├── routers/
│   │   ├── home.py
│   │   └── room.py
│   ├── database/
│   │   ├── models.py
│   │   └── session.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── room.html
│   │   └── _*.html
│   └── static/
│
├── models/
│   ├── knn_model_A.joblib
│   ├── knn_model_B.joblib
│   ├── knn_model_C.joblib
│   └── comfort_rf_model.joblib
│
├── data/
│   ├── comfort_temperature/
│   │   └── room_temperature_dataset.csv
│   ├── datasets-location_A/
│   ├── datasets-location_B/
│   └── datasets-location_C/
│
├── scripts/
│   ├── train_knn_models.py
│   └── train_comfort_model.py
│
└── README.md
```

---

## 🧪 API Overview

| Method | Endpoint                        | Purpose                              |
|--------|----------------------------------|--------------------------------------|
| GET    | `/`                              | Dashboard homepage                   |
| GET    | `/room/{room_id}`               | Room control view                    |
| GET    | `/room/{room_id}/sensors`       | Load sensor inputs form              |
| POST   | `/room/{room_id}/sensors`       | Submit updated sensor data           |
| GET    | `/room/{room_id}/predict`       | Get predicted temperature            |
| GET    | `/room/{room_id}/preference`    | Load comfort preference              |
| POST   | `/room/{room_id}/preference`    | Submit new preference                |

---

## 🚀 Getting Started

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Train models
```bash
python scripts/train_knn_models.py
python scripts/train_comfort_model.py
```

### 3. Run the app
```bash
uvicorn app.main:app --reload
```
