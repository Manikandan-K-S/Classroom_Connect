const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    // This line uses the final, correctly substituted MONGO_URI from the process environment
    const conn = await mongoose.connect(process.env.MONGO_URI);
    console.log(`MongoDB Connected: ${conn.connection.host} 🚀`);
  } catch (error) {
    console.error(`Error connecting to MongoDB Atlas: ${error.message}`);
    // Exit process with failure
    process.exit(1);
  }
};

module.exports = connectDB;
