const pyodide = await loadPyodide({
  indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.18.1/full/',
});
await pyodide.loadPackage(['numpy', 'pandas', 'scikit-learn', 'folium']);
async function predictLocation(budget, city, propertyType) {
  const data = await fetch('zameen_data.csv').then((response) =>
    response.text()
  );
  const PyDataFrame = await pyodide.loadPackage('pandas');
  const df = await PyDataFrame.read_csv(
    new pyodide.globals.JSObject([data], ['UTF8Array']),
    { header: 0 }
  );

  const filteredData = df.loc[
    df.get('city').eq(city).and(df.get('property_type').eq(propertyType)).and(df.get('price').le(budget))
  ];
  const PyRandomForestRegressor = await pyodide.loadPackage(
    'sklearn.ensemble'
  );
  const model = await PyRandomForestRegressor.RandomForestRegressor({
    n_estimators: 100,
    random_state: 42,
  });
  const features = ['beds', 'baths'];
  const X = filteredData.get(features);
  const y = filteredData.get('price');
  await model.fit(X, y);

  const predictedPrice = await model.predict(
    new pyodide.globals.JSObject(
      [
        [3, 2],
        [4, 3],
        [3, 2],
        [4, 3],
      ],
      ['Int32Array', 'Int32Array']
    )
  );
  const period = prompt('Enter the period (in months): ');

  const centerLat = filteredData.get('latitude').get(0);
  const centerLon = filteredData.get('longitude').get(0);
  const mapLocation = [centerLat, centerLon];
  const PyFolium = await pyodide.loadPackage('folium');
  const m = await PyFolium.Map(mapLocation, { zoom_start: 15 });

  filteredData.iterrows().forEach(async function (row) {
      const price = row.get('price');
      const latitude = row.get('latitude');
      const longitude = row.get('longitude');
      const tooltip = `Price: ${price} PKR`;
      L.marker([latitude, longitude], {icon: icon}).addTo(map).bindTooltip(tooltip);
  });
  
  const submitBtn = document.getElementById('submit-btn');
  submitBtn.addEventListener('click', function () {
      const budgetInput = document.getElementById('budget-input');
      const budget = budgetInput.value;
  
      const cityInput = document.getElementById('city-input');
      const city = cityInput.value;
  
      const propertyTypeInput = document.getElementById('property-type-input');
      const propertyType = propertyTypeInput.value;
  
      const periodInput = document.getElementById('period-input');
      const period = periodInput.value;
  
      fetch(`/predict-location?budget=${budget}&city=${city}&property_type=${propertyType}&period=${period}`)
          .then(response => response.json())
          .then(data => {
              const predictedPrice = data.predicted_price_period;
              const predictedLocation = data.predicted_location;
  
              // Add marker for predicted location
              L.marker([predictedLocation[0], predictedLocation[1]], {icon: greenIcon})
                  .addTo(map)
                  .bindTooltip(`Predicted Price: ${predictedPrice.toFixed(2)} PKR`);
  
              // Show success message
              const successAlert = document.getElementById('success-alert');
              successAlert.style.display = 'block';
              successAlert.innerHTML = `The predicted price for a ${propertyType} in ${city} with a period of ${period} months is approximately ${predictedPrice.toFixed(2)} PKR.`;
          })
          .catch(error => {
              console.log(error);
              // Show error message
              const errorAlert = document.getElementById('error-alert');
              errorAlert.style.display = 'block';
              errorAlert.innerHTML = 'An error occurred while fetching the data. Please try again later.';
          });
  });
  