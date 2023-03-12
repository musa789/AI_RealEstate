from flask import Flask, render_template, request
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import folium
import webbrowser
import tempfile

app = Flask(__name__)

def filter_data(data, budget, city, property_type):
    filtered_data = data.loc[(data['city'] == city) & (data['property_type'] == property_type) & (data['price'] <= budget)]
    return filtered_data

def predict_price(filtered_data, period):
    features = ['beds', 'baths']
    X = filtered_data[features]
    y = filtered_data['price']

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    predicted_price = model.predict([[3, 2], [4, 3], [3, 2], [4, 3]])
    predicted_price_period = predicted_price[int(period)-1]
    return predicted_price_period

def predict_location(data, budget, city, property_type, period):
    filtered_data = filter_data(data, budget, city, property_type)

    predicted_price_period = predict_price(filtered_data, period)
    # Create map centered on the first property in filtered_data
    center_lat = filtered_data.iloc[0]['latitude']
    center_lon = filtered_data.iloc[0]['longitude']
    map_location = [center_lat, center_lon]
    m = folium.Map(location=map_location, zoom_start=15)
    # Add markers to the map for each property in filtered_data
    for index, row in filtered_data.iterrows():
        price = row['price']
        lat = row['latitude']
        lon = row['longitude']
        tooltip = f"Price: {price} PKR"
        folium.Marker([lat, lon], tooltip=tooltip).add_to(m)
        # Add marker for predicted location
        predicted_lat = filtered_data.iloc[0]['latitude'] + 0.001
        predicted_lon = filtered_data.iloc[0]['longitude'] + 0.001
        predicted_tooltip = f"Predicted Price: {predicted_price_period:.2f} PKR"
        folium.Marker([predicted_lat, predicted_lon], tooltip=predicted_tooltip, icon=folium.Icon(color='green')).add_to(m)
    # Save map to temporary HTML file
    temp_file = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
    temp_file.close()
    m.save(temp_file.name)

    # Open map in browser and display predicted price
    webbrowser.open('file://' + temp_file.name, new=2)
    return f"The predicted price for a {property_type.lower()} in {city} with a period of {period} months is approximately {predicted_price_period:.2f} PKR."


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = pd.read_csv('zameen_data.csv')
    budget = int(request.form['budget'])
    city = request.form['city']
    property_type = request.form['property_type']
    period = request.form['period']
    result = predict_location(data, budget, city, property_type, period)
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
