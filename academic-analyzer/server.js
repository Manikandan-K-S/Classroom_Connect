// academic-analyzer/server.js
const express = require('express');
const dotenv = require('dotenv');
const connectDB = require('./config/db');

// Load environment variables from .env file
// Try to expand nested variables (e.g. MONGO_URI referencing DB_USERNAME) if dotenv-expand is available.
const envResult = dotenv.config();
try {
    // require dotenv-expand only if it's installed; this keeps the repo dependency-free for now
    const dotenvExpand = require('dotenv-expand');
    dotenvExpand.expand(envResult);
    console.info('dotenv-expand is active: environment variable references in .env will be expanded.');
} catch (err) {
    // If dotenv-expand is not installed, that's fine — we just warn so the developer knows why ${VAR} won't expand.
    if (err.code !== 'MODULE_NOT_FOUND') {
        console.warn('Warning while trying to expand environment variables:', err.message);
    } else {
        console.info('dotenv-expand not installed: `.env` variable references like ${DB_CLUSTER_URL} will NOT be expanded automatically.');
    }
}

// Connect to database
connectDB();

const app = express();

// Middleware to parse JSON bodies
app.use(express.json());

// --- Define Routes (Will be populated in the next step) ---
const studentRoutes = require('./routes/studentRoutes');
const staffRoutes = require('./routes/staffRoutes');

// Mount Routes
app.use('/student', studentRoutes);
app.use('/staff', staffRoutes);

// Simple welcome route
app.get('/', (req, res) => {
    res.send('Academic Analyzer API is running...');
});

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => console.log(`Server running on port ${PORT} in development mode 🌟`));