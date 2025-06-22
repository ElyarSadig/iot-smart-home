import os
import glob
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_squared_error

# Paths and settings
DATA_ROOT = "data"
MODEL_OUTPUT_DIR = "models"
COMFORT_DATA_CSV = os.path.join(DATA_ROOT, "comfort_temperature", "room_temperature_dataset.csv")
ROOM_DIRS = {
    "A": "datasets-location_A",
    "B": "datasets-location_B",
    "C": "datasets-location_C",
}
FEATURES = ["RelH", "L1", "L2", "Occ", "Act", "Door", "Win"]
TARGET = "Temp"

def ensure_directories():
    os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)

def load_and_prepare_data(folder_path: str) -> pd.DataFrame:
    """Load and combine CSV files in a folder."""
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    data_frames = []

    for file in csv_files:
        df = pd.read_csv(
            file,
            header=None,
            names=["EID", "AbsT", "RelT", "NID", "Temp", "RelH", "L1", "L2", "Occ", "Act", "Door", "Win"]
        )
        data_frames.append(df)

    if not data_frames:
        return pd.DataFrame()

    combined_df = pd.concat(data_frames, ignore_index=True)
    return combined_df.dropna(subset=FEATURES + [TARGET])

def train_knn_model(df: pd.DataFrame) -> KNeighborsRegressor:
    """Train KNN model on the given dataset."""
    X = df[FEATURES]
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = KNeighborsRegressor(n_neighbors=5)
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    print(f"KNN R² score: {score:.3f}")
    return model

def train_random_forest_model_per_room(csv_path: str):
    """Train and save one Random Forest model per room."""
    df = pd.read_csv(csv_path, parse_dates=['created_at'])
    df['hour'] = df['created_at'].dt.hour
    df['minute'] = df['created_at'].dt.minute
    df['dayofweek'] = df['created_at'].dt.dayofweek

    for room in ROOM_DIRS.keys():
        df_room = df[df['room'] == room]

        if df_room.empty:
            print(f"No data available for Room {room}. Skipping.")
            continue

        X = df_room[['hour', 'minute', 'dayofweek']]
        y = df_room['temperature']

        preprocessor = ColumnTransformer([
            ('num', 'passthrough', ['hour', 'minute', 'dayofweek'])
        ])

        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
        ])

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        rmse = mean_squared_error(y_test, y_pred) ** 0.5
        print(f"Room {room} - Random Forest RMSE: {rmse:.3f}")

        model_path = os.path.join(MODEL_OUTPUT_DIR, f"random_forest_model_room_{room}.pkl")
        joblib.dump(pipeline, model_path)
        print(f"Saved Random Forest model to {model_path}\n")

def main():
    ensure_directories()

    print("Training KNN models for each room:")
    for room, subdir in ROOM_DIRS.items():
        folder_path = os.path.join(DATA_ROOT, subdir)
        print(f"Processing Room {room} | Data folder: {folder_path}")
        df = load_and_prepare_data(folder_path)

        if df.empty:
            print(f"No data found or after cleaning for room {room}. Skipping.")
            continue

        model = train_knn_model(df)
        model_path = os.path.join(MODEL_OUTPUT_DIR, f"knn_model_room_{room}.pkl")
        joblib.dump(model, model_path)
        print(f"Saved KNN model to {model_path}\n")

    print("Training global Random Forest model for comfort temperature prediction:")
    train_random_forest_model_per_room(COMFORT_DATA_CSV)

if __name__ == "__main__":
    main()
