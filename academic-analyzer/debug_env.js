require('dotenv').config();
console.log('Environment variables:');
console.log('DB_USERNAME:', process.env.DB_USERNAME);
console.log('DB_PASSWORD:', process.env.DB_PASSWORD);
console.log('DB_CLUSTER_URL:', process.env.DB_CLUSTER_URL);
console.log('DB_NAME:', process.env.DB_NAME);
console.log('MONGO_URI:', process.env.MONGO_URI);