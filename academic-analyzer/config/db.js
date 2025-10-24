const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    // Debug output to see what we're working with
    console.log('DEBUG - Environment Variables:');
    console.log('MONGO_URI:', process.env.MONGO_URI);
    console.log('DB_USERNAME:', process.env.DB_USERNAME);
    console.log('DB_PASSWORD:', process.env.DB_PASSWORD);
    console.log('DB_CLUSTER_URL:', process.env.DB_CLUSTER_URL);
    console.log('DB_NAME:', process.env.DB_NAME);

    // Use hardcoded connection string as a fallback
    let mongoUri = 'mongodb+srv://mani:admin@cluster0.ln2b121.mongodb.net/academic_analyzer?retryWrites=true&w=majority';

    // If we have all the individual parts, construct the URI
    const DB_USERNAME = process.env.DB_USERNAME;
    const DB_PASSWORD = process.env.DB_PASSWORD;
    const DB_CLUSTER_URL = process.env.DB_CLUSTER_URL;
    const DB_NAME = process.env.DB_NAME;

    if (DB_USERNAME && DB_PASSWORD && DB_CLUSTER_URL && DB_NAME) {
      mongoUri = `mongodb+srv://${DB_USERNAME}:${encodeURIComponent(DB_PASSWORD)}@${DB_CLUSTER_URL}/${DB_NAME}?retryWrites=true&w=majority`;
      console.info('Constructed MONGO_URI from DB_USERNAME, DB_PASSWORD, DB_CLUSTER_URL and DB_NAME.');
    }

    const conn = await mongoose.connect(mongoUri, {
      // Use recommended options; depending on mongoose version these may be no-ops
      // but including them keeps compatibility with older setups.
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });

    console.log(`MongoDB Connected: ${conn.connection.host} 🚀`);
  } catch (error) {
    // Logs the specific error message (e.g., connection issue, bad credentials)
    console.error(`Error connecting to MongoDB Atlas: ${error.message}`);

    // If the error is a DNS SRV lookup for an unexpanded placeholder, provide targeted advice
    if (error && /_mongodb\._tcp\.|ENOTFOUND|EAI_AGAIN|EBADNAME/i.test(error.message)) {
      console.error('It looks like the connection string contains an unresolved SRV host (for example a literal ${DB_CLUSTER_URL}).');
      console.error('Double-check your .env — ensure you do NOT wrap the MONGO_URI in quotes that prevent variable expansion in your environment, or set MONGO_URI to the fully expanded connection string.');
      console.error('Alternatively, set DB_USERNAME, DB_PASSWORD, DB_CLUSTER_URL and DB_NAME so the connector can build the URI automatically.');
    }

    // Exit the application if the database connection cannot be established
    process.exit(1);
  }
};

module.exports = connectDB;
