import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.neighbors import NearestNeighbors
import joblib
from django.conf import settings
import os

# Load dataset
def load_data():
    print("Loading dataset...")
    df = pd.read_csv('crime_data.csv')
    print("Dataset loaded successfully.")
    df = df.sample(n=100000, random_state=42)
    columns_to_drop = [
        'DR_NO', 'Date Rptd', 'DATE OCC', 'LOCATION',
        'Cross Street', 'AREA NAME', 'Mocodes', 'Crm Cd 1', 'Crm Cd 2', 'Crm Cd 3', 'Crm Cd 4'
    ]
    df = df.drop(columns=columns_to_drop)
    print("Unnecessary columns dropped.")

    df['Vict Sex'] = df['Vict Sex'].fillna('U')
    df['Vict Descent'] = df['Vict Descent'].fillna('Unknown')
    df['Premis Desc'] = df['Premis Desc'].fillna('Unknown')
    df['Weapon Desc'] = df['Weapon Desc'].fillna('No Weapon')
    print("Missing values filled.")

    top_10_crime_types = df['Crm Cd Desc'].value_counts().nlargest(10).index
    df['Crm Cd Desc'] = df['Crm Cd Desc'].apply(lambda x: x if x in top_10_crime_types else 'Others')
    print("Crime categories standardized.")
    
    return df

# Preprocess data
def preprocess_data(df):
    print("Starting preprocessing...")
    label_encoders = {}
    categorical_columns = ['Crm Cd Desc', 'Vict Sex', 'Vict Descent', 'Premis Desc', 'Weapon Desc']
    for col in categorical_columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le
    print("Categorical data encoded.")

    df['Vict Age'] = df['Vict Age'].fillna(-1)
    df['Premis Cd'] = df['Premis Cd'].fillna(-1)
    df['Weapon Used Cd'] = df['Weapon Used Cd'].fillna(-1)
    df['LAT'] = df['LAT'].fillna(0)
    df['LON'] = df['LON'].fillna(0)
    print("Numerical missing values handled.")

    features = ['TIME OCC', 'AREA', 'Rpt Dist No', 'Vict Age', 'Premis Cd', 'Weapon Used Cd', 'LAT', 'LON']
    X = df[features]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    print("Data scaling complete.")
    return df, X_scaled, scaler, label_encoders

# Train and save the model
def train_model(X_scaled):
    print("Training Nearest Neighbors model...")
    nn_model = NearestNeighbors(n_neighbors=5, metric='euclidean')
    nn_model.fit(X_scaled)
    print("Model training complete.")
    return nn_model

# Save the model and encoders
def save_model(nn_model, scaler, label_encoders):
    print("Saving model...")
    media_path = settings.MEDIA_ROOT
    models_path = os.path.join(media_path, 'models')
    os.makedirs(models_path, exist_ok=True)
    joblib.dump(nn_model, os.path.join(models_path, 'nn_model.pkl'))
    joblib.dump(scaler, os.path.join(models_path, 'scaler.pkl'))
    joblib.dump(label_encoders, os.path.join(models_path, 'label_encoders.pkl'))
    print("Model, scaler, and label encoders saved successfully.")

# Predict similar crimes
def predict_and_decode_similar_crimes(new_crime, df, nn_model, scaler, label_encoders):
    print("Processing new crime for similarity search...")
    features = ['TIME OCC', 'AREA', 'Rpt Dist No', 'Vict Age', 'Premis Cd', 'Weapon Used Cd', 'LAT', 'LON']
    new_crime_df = pd.DataFrame([new_crime])
    new_crime_df=new_crime_df[features]
    new_crime_scaled = scaler.transform(new_crime_df)
    print("New crime data scaled.")

    distances, indices = nn_model.kneighbors(new_crime_scaled)
    print("Nearest neighbors found.")

    similar_crimes = df.iloc[indices[0]].copy()
    categorical_columns = ['Crm Cd Desc', 'Vict Sex', 'Vict Descent', 'Premis Desc', 'Weapon Desc']
    for col in categorical_columns:
        similar_crimes[col] = label_encoders[col].inverse_transform(similar_crimes[col])
    print("Similar crimes decoded and ready.")
    return similar_crimes

# Load saved model
def load_saved_model():
    try:
        print("Loading saved model...")
        media_path = settings.MEDIA_ROOT
        models_path = os.path.join(media_path, 'models')
        nn_model = joblib.load(os.path.join(models_path, 'nn_model.pkl'))
        scaler = joblib.load(os.path.join(models_path, 'scaler.pkl'))
        label_encoders = joblib.load(os.path.join(models_path, 'label_encoders.pkl'))
        print("Model loaded successfully.")
        return nn_model, scaler, label_encoders
    except FileNotFoundError as e:
        print(f"Error loading model: {e}")
        return None, None, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None, None

import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns

def generate_graph(df, graph_type):
    plt.figure(figsize=(12, 6))

    if graph_type == 'crime_types':
        sns.countplot(y='Crm Cd Desc', data=df, order=df['Crm Cd Desc'].value_counts().index, palette='viridis')
        plt.title("Top Crime Types")
        plt.xlabel("Count")
        plt.ylabel("Crime Type")

    elif graph_type == 'victim_age':
        sns.histplot(df['Vict Age'], bins=30, kde=True, color='blue')
        plt.title("Victim Age Distribution")
        plt.xlabel("Age")
        plt.ylabel("Frequency")

    elif graph_type == 'crime_areas':
        sns.countplot(x='AREA', data=df, palette='coolwarm')
        plt.title("Distribution of Crimes by Area")
        plt.xlabel("Area")
        plt.ylabel("Count")

    else:
        plt.title("Default Graph")
        plt.plot([1, 2, 3, 4], [10, 20, 25, 30])

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graph_url = base64.b64encode(buffer.read()).decode('utf-8')
    return f"data:image/png;base64,{graph_url}"