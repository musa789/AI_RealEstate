import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import folium

# read the data
data = pd.read_csv("zameen_data.csv")

# convert "Area" column to numerical format
data["area"] = data["area"].apply(lambda x: int(float(x.replace(",", "").split()[0]) * 9) if "Marla" in x else int(float(x.replace(",", "").split()[0]) * 225))


# create X and y arrays
X = data.iloc[:, :-1].values
y = data.iloc[:, -1].values

# encode categorical variables and standardize numerical variables
ct = ColumnTransformer(transformers=[("encoder", OneHotEncoder(), [0, 1, 2, 3]), ("scaler", StandardScaler(), [4, 5, 6])])
X = np.array(ct.fit_transform(X), dtype=np.float)

# split the data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# train a random forest regressor on the data
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# get user inputs for property type, bedrooms, location, and expected return period
while True:
    property_type = input("Enter the property type (Flat, House, Farm House): ").strip().title()
    if property_type in ["Flat", "House", "Farm House"]:
        break
    else:
        print("Invalid property type. Please try again.")

while True:
    bedrooms = input("Enter the number of bedrooms (1-10): ").strip()
    if bedrooms.isdigit() and 1 <= int(bedrooms) <= 10:
        break
    else:
        print("Invalid number of bedrooms. Please try again.")

while True:
    location = input("Enter the location (e.g. DHA, Bahria Town, Gulberg): ").strip().title()
    if location in ["Dha", "Bahria Town", "Gulberg"]:
        break
    else:
        print("Invalid location. Please try again.")

while True:
    expected_return_period = input("Enter the expected return period in months (12-120): ").strip()
    if expected_return_period.isdigit() and 12 <= int(expected_return_period) <= 120:
        break
    else:
        print("Invalid expected return period. Please try again.")

# create an input array for the user inputs
input_data = [[property_type, bedrooms, location, expected_return_period, 0, 0, 0]]

# encode and scale the input data
input_data = ct.transform(input_data)

# make a prediction on the input data
predicted_return = rf.predict(input_data)[0]

# get the latitude and longitude of the property with the highest predicted return
max_return_idx = np.argmax(rf.predict(X_test))
predicted_lat = data.loc[X_test[max_return_idx], "Latitude"]
predicted_lon = data.loc[X_test[max_return_idx], "Longitude"]

# create a map and add a marker for the predicted location
m = folium.Map(location=[predicted_lat, predicted_lon], zoom_start=15)
marker = folium.Marker(location=[predicted_lat, predicted_lon], popup=f"Latitude: {predicted_lat}, Longitude: {predicted_lon}, Predicted Return: {predicted_return}")
marker.add_to(m)
m.save("map.html")
