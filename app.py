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

    # Generate Mapbox access token
    px.set_mapbox_access_token(access_token)

    # Create a scatter plot of properties in the filtered data
    fig = px.scatter_mapbox(filtered_data,
                            lat='latitude',
                            lon='longitude',
                            size='price',
                            color='price',
                            hover_name='title',
                            hover_data=['price', 'beds', 'baths'],
                            zoom=12,
                            center=dict(lat=center_lat, lon=center_lon))

    # Add a marker for the predicted location
    predicted_lat = filtered_data.iloc[0]['latitude'] + 0.001
    predicted_lon = filtered_data.iloc[0]['longitude'] + 0.001
    predicted_price_str = f"Predicted Price: {predicted_price_period:.2f} PKR"
    fig.add_trace(
        go.Scattermapbox(
            lat=[predicted_lat],
            lon=[predicted_lon],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=10,
                color='green'
            ),
            text=predicted_price_str,
            hoverinfo='text'
        )
    )

    # Set the layout of the figure
    fig.update_layout(
        mapbox=dict(
            style='streets',
            center=dict(lat=center_lat, lon=center_lon),
            zoom=12,
        ),
        height=600,
    )

    # Save the map to a temporary HTML file
    temp_file = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
    temp_file.close()
    fig.write_html(temp_file.name)

    # Open the map in a new tab and display the predicted price
    return f"The predicted price for a {property_type.lower()} in {city} with a period of {period} months is approximately {predicted_price_period:.2f} PKR. <br> <a href='{temp_file.name}' target='_blank'>View Map</a>"
