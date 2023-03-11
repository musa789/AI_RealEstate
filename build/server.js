const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

mongoose.connect('mongodb://127.0.0.1:27017/ai-realestate-friend', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

const connection = mongoose.connection;
connection.once('open', () => {
  console.log('MongoDB database connection established successfully');
});

const listingSchema = new mongoose.Schema({
  title: String,
  description: String,
  address: String,
  city: String,
  state: String,
  zip: String,
  price: Number,
  image: String,
});

// Define a new Mongoose model based on the listing schema
const Listing = mongoose.models.Listing || mongoose.model('Listing', listingSchema);

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'client/build', 'index.html'));
});

// Route to get all listings
app.get('/api', async (req, res) => {
  try {
    const listings = await Listing.find();
    res.json(listings);
  } catch (error) {
    console.error(error);
    res.status(500).send('Server error');
  }
});

// Route to create a new listing
app.post('/api', async (req, res) => {
  try {
    const listing = new Listing(req.body);
    await listing.save();
    res.json(listing);
  } catch (error) {
    console.error(error);
    res.status(500).send('Server error');
  }
});

const listingRoutes = require('./routes/listing');
app.use('/api/listings', listingRoutes);

app.use(express.static(path.join(__dirname, 'client/build')));

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'client/build', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server is running on port: ${PORT}`);
});
