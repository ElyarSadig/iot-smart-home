import os
import glob
import pandas as pd
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split
import numpy as np
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_squared_error
import joblib

DATA_ROOT = "data"
ROOM_DIRS = {
    "A": "datasets-location_A",
    "B": "datasets-location_B",
    "C": "datasets-location_C",
}
MODEL_OUTPUT_DIR = "models"

FEATURES = ["RelH", "L1", "L2", "Occ", "Act", "Door", "Win"]
TARGET = "Temp"

def load_and_prepare_data(folder_path: str) -> pd.DataFrame:
    """Load and concatenate CSVs in the given folder"""
    all_csvs = glob.glob(os.path.join(folder_path, "*.csv"))
    frames = []

    for csv in all_csvs:
        df = pd.read_csv(
            csv,
            header=None,
            names=["EID", "AbsT", "RelT", "NID", "Temp", "RelH", "L1", "L2", "Occ", "Act", "Door", "Win"]
        )
        frames.append(df)

    full_df = pd.concat(frames, ignore_index=True)
    full_df = full_df.dropna(subset=FEATURES + [TARGET])
    return full_df

def train_knn(df: pd.DataFrame) -> KNeighborsRegressor:
    """Train and return a KNN regressor on the data"""
    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = KNeighborsRegressor(n_neighbors=5)
    model.fit(X_train, y_train)

    score = model.score(X_test, y_test)
    print(f"Model trained. R² score: {score:.3f}")
    return model

def train_room_temperature_model(csv_path="data/comfort_temperature/room_temperature_dataset.csv", model_path="models/room_temperature_model.pkl"):
    df = pd.read_csv(csv_path, parse_dates=['created_at'])

    df['hour'] = df['created_at'].dt.hour
    df['minute'] = df['created_at'].dt.minute
    df['dayofweek'] = df['created_at'].dt.dayofweek

    X = df[['room', 'hour', 'minute', 'dayofweek']]
    y = df['temperature']

    categorical_features = ['room']
    numeric_features = ['hour', 'minute', 'dayofweek']

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(), categorical_features),
            ('num', 'passthrough', numeric_features)
        ]
    )

    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model_pipeline.fit(X_train, y_train)

    y_pred = model_pipeline.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5
    print(f"RMSE: {rmse:.3f}")

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model_pipeline, model_path)
    print(f"Model saved to {model_path}")

def main():
    os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)

    for room, subdir in ROOM_DIRS.items():
        print(f"Processing Room {room}")
        folder_path = os.path.join(DATA_ROOT, subdir)
        df = load_and_prepare_data(folder_path)

        if df.empty:
            print(f"No data found for Room {room}. Skipping.")
            continue

        model = train_knn(df)
        model_path = os.path.join(MODEL_OUTPUT_DIR, f"knn_model_room_{room}.pkl")
        joblib.dump(model, model_path)
        print(f"Saved model for Room {room} to {model_path}\n")
    
    train_room_temperature_model()


if __name__ == "__main__":
    main()
