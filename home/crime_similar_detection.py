import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
df = pd.read_csv('crime_data.csv')

# Drop unnecessary columns
columns_to_drop = [
    'DR_NO', 'Date Rptd', 'DATE OCC', 'LOCATION',
    'Cross Street', 'AREA NAME', 'Mocodes', 'Crm Cd 1', 'Crm Cd 2', 'Crm Cd 3', 'Crm Cd 4'
]
df = df.drop(columns=columns_to_drop)

# Handle missing values
df['Vict Sex'] = df['Vict Sex'].fillna('U')
df['Vict Descent'] = df['Vict Descent'].fillna('Unknown')
df['Premis Desc'] = df['Premis Desc'].fillna('Unknown')
df['Weapon Desc'] = df['Weapon Desc'].fillna('No Weapon')

# Visualize the crime type distribution
plt.figure(figsize=(12, 6))
sns.countplot(y='Crm Cd Desc', data=df, order=df['Crm Cd Desc'].value_counts().index, palette='viridis')
plt.title("Top Crime Types")
plt.xlabel("Count")
plt.ylabel("Crime Type")
plt.show()

# Visualize the distribution of victim age
plt.figure(figsize=(12, 6))
sns.histplot(df['Vict Age'], bins=30, kde=True, color='blue')
plt.title("Victim Age Distribution")
plt.xlabel("Age")
plt.ylabel("Frequency")
plt.show()

# Visualize crime distribution by area
plt.figure(figsize=(12, 6))
sns.countplot(x='AREA', data=df, palette='coolwarm')
plt.title("Distribution of Crimes by Area")
plt.xlabel("Area")
plt.ylabel("Count")
plt.show()

# Visualize the geographic locations of crimes (LAT vs LON)
plt.figure(figsize=(12, 6))
sns.scatterplot(x='LAT', y='LON', data=df, hue='Crm Cd Desc', palette='tab10', legend=None)
plt.title("Geographic Distribution of Crimes")
plt.xlabel("Latitude")
plt.ylabel("Longitude")
plt.show()



