import requests
import json
import urllib.parse
import turfpy.measurement as turf
def predict_location(data, budget, city, property_type, period, access_token):
    filtered_data = filter_data(data, budget, city, property_type)

    predicted_price_period = predict_price(filtered_data, period)
    # Create map centered on the first property in filtered_data
    center_lat = filtered_data.iloc[0]['latitude']
    center_lon = filtered_data.iloc[0]['longitude']
    map_location = [center_lat, center_lon]
    m = folium.Map(location=map_location, zoom_start=15, tiles='https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', attr='Mapbox', id='mapbox/streets-v11')
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
    mapbox_url = 'https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/{lon},{lat},{zoom}/{width}x{height}?access_token={access_token}'
    map_url = mapbox_url.format(lon=center_lon, lat=center_lat, zoom=15, width=600, height=400, access_token=access_token)
    return render_template('predict.html', result=f"The predicted price for a {property_type.lower()} in {city} with a period of {period} months is approximately {predicted_price_period:.2f} PKR.", map_url=map_url)
