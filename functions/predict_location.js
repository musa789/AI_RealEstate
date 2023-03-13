const axios = require('axios');
const qs = require('qs');
const { sk.eyJ1IjoibXVzYTc4OSIsImEiOiJjbGY1ZDBzbzgwdHF5M3dvY3F4dGx4a210In0.l-i8jiaS8LWPyXj1ocQiCg } = process.env;

exports.handler = async function(event) {
  const params = qs.stringify({
    access_token: sk.eyJ1IjoibXVzYTc4OSIsImEiOiJjbGY1ZDBzbzgwdHF5M3dvY3F4dGx4a210In0.l-i8jiaS8LWPyXj1ocQiCg,
    query: event.queryStringParameters.address,
    autocomplete: true,
    limit: 1,
  });

  try {
    const response = await axios.get(`https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(event.queryStringParameters.address)}.json?${params}`);
    const data = response.data;

    if (data.features.length === 0) {
      return {
        statusCode: 404,
        body: JSON.stringify({ message: 'No results found for this location' }),
      };
    }

    const result = data.features[0];
    const { center, place_name } = result;

    return {
      statusCode: 200,
      body: JSON.stringify({ longitude: center[0], latitude: center[1], location: place_name }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ message: error.message || 'Something went wrong' }),
    };
  }
};
