import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.neighbors import NearestNeighbors
import joblib

# Global variables
label_encoders = {}
scaler = None
nn_model = None

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv('crime_data.csv')
    df = df.sample(n=100000, random_state=42)
    
    columns_to_drop = [
        'DR_NO', 'Date Rptd', 'DATE OCC', 'LOCATION',
        'Cross Street', 'AREA NAME', 'Mocodes', 'Crm Cd 1', 'Crm Cd 2', 'Crm Cd 3', 'Crm Cd 4'
    ]
    df = df.drop(columns=columns_to_drop)
    
    # Fill missing values
    df['Vict Sex'] = df['Vict Sex'].fillna('U')
    df['Vict Descent'] = df['Vict Descent'].fillna('Unknown')
    df['Premis Desc'] = df['Premis Desc'].fillna('Unknown')
    df['Weapon Desc'] = df['Weapon Desc'].fillna('No Weapon')
    
    # Reduce number of unique crime types
    top_10_crime_types = df['Crm Cd Desc'].value_counts().nlargest(10).index
    df['Crm Cd Desc'] = df['Crm Cd Desc'].apply(lambda x: x if x in top_10_crime_types else 'Others')
    
    return df

# Preprocess data
def preprocess_data(df):
    global label_encoders, scaler
    
    # Encode categorical features
    categorical_columns = ['Crm Cd Desc', 'Vict Sex', 'Vict Descent', 'Premis Desc', 'Weapon Desc']
    label_encoders = {}
    
    for col in categorical_columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le
    
    # Fill missing values
    df['Vict Age'] = df['Vict Age'].fillna(-1)
    df['Premis Cd'] = df['Premis Cd'].fillna(-1)
    df['Weapon Used Cd'] = df['Weapon Used Cd'].fillna(-1)
    df['LAT'] = df['LAT'].fillna(0)
    df['LON'] = df['LON'].fillna(0)
    
    # Scale numeric data
    features = ['TIME OCC', 'AREA', 'Rpt Dist No', 'Vict Age', 'Premis Cd', 'Weapon Used Cd', 'LAT', 'LON']
    X = df[features]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return df, X_scaled

# Save model
def save_model(nn_model, scaler, label_encoders):
    joblib.dump(nn_model, 'nn_model.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    joblib.dump(label_encoders, 'label_encoders.pkl')

# Load model
def load_model():
    nn_model = joblib.load('nn_model.pkl')
    scaler = joblib.load('scaler.pkl')
    label_encoders = joblib.load('label_encoders.pkl')
    return nn_model, scaler, label_encoders

# Main App
st.title("Crime Data KNN Prediction")

# Tabs
tab1, tab2, tab3 = st.tabs(["Train Model", "Predict", "Load Model"])

# Tab 1: Train Model
with tab1:
    st.header("Train KNN Model")
    
    df = load_data()
    df, X_scaled = preprocess_data(df)
    
    if st.button("Train Model"):
        nn_model = NearestNeighbors(n_neighbors=5, metric='euclidean')
        nn_model.fit(X_scaled)
        save_model(nn_model, scaler, label_encoders)
        st.success("Model trained and saved successfully!")

# Tab 2: Predict
with tab2:
    st.header("Predict Similar Crimes")
    
    # Load dataset for dropdown values
    df = load_data()
    preprocess_data(df)
    
    # Dropdown inputs
    time_occ = st.selectbox("Time Occurred", sorted(df['TIME OCC'].unique()))
    area = st.selectbox("Area", sorted(df['AREA'].unique()))
    rpt_dist_no = st.selectbox("Report District Number", sorted(df['Rpt Dist No'].unique()))
    vict_age = st.selectbox("Victim Age", sorted(df['Vict Age'].unique()))
    premis_cd = st.selectbox("Premises Code", sorted(df['Premis Cd'].unique()))
    weapon_used_cd = st.selectbox("Weapon Used Code", sorted(df['Weapon Used Cd'].unique()))
    lat = st.number_input("Latitude", value=34.0)
    lon = st.number_input("Longitude", value=-118.0)
    
    if st.button("Find Similar Crimes"):
        nn_model, scaler, label_encoders = load_model()
        
        # Prepare input
        new_crime = {
            'TIME OCC': time_occ,
            'AREA': area,
            'Rpt Dist No': rpt_dist_no,
            'Vict Age': vict_age,
            'Premis Cd': premis_cd,
            'Weapon Used Cd': weapon_used_cd,
            'LAT': lat,
            'LON': lon
        }
        new_crime_df = pd.DataFrame([new_crime])
        new_crime_scaled = scaler.transform(new_crime_df)
        
        # Predict
        distances, indices = nn_model.kneighbors(new_crime_scaled)
        similar_crimes = df.iloc[indices[0]]
        
        # Decode categorical columns
        similar_crimes['Crm Cd Desc'] = label_encoders['Crm Cd Desc'].inverse_transform(similar_crimes['Crm Cd Desc'])
        st.write("Similar Crimes:")
        st.dataframe(similar_crimes)

# Tab 3: Load Model
with tab3:
    st.header("Load Saved Model")
    
    if st.button("Load Model"):
        nn_model, scaler, label_encoders = load_model()
        st.success("Model loaded successfully!")
