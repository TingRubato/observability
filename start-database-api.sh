#!/bin/bash

# Start Database API Server for Observable Framework
# This script sets up and starts the database API server

echo "🚀 Starting Database API Server for Observable Framework"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "src/database-api-server.js" ]; then
    echo "❌ Error: database-api-server.js not found. Please run this script from the project root."
    exit 1
fi

# Load environment variables
echo "📋 Loading environment variables..."
if [ -f "load-env.sh" ]; then
    source load-env.sh
    echo "✅ Environment variables loaded"
else
    echo "⚠️  Warning: load-env.sh not found. Using default environment variables."
    echo "   Make sure to set PGHOST, PGDATABASE, PGUSER, PGPASSWORD"
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed. Please install npm first."
    exit 1
fi

# Install dependencies if needed
if [ ! -d "src/node_modules" ]; then
    echo "📦 Installing dependencies..."
    cd src
    npm install
    cd ..
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

# Check database connection
echo "🔍 Testing database connection..."
cd src
node -e "
import { Pool } from 'pg';
const pool = new Pool({
  host: process.env.PGHOST || 'localhost',
  port: parseInt(process.env.PGPORT) || 5432,
  database: process.env.PGDATABASE || 'mazak',
  user: process.env.PGUSER || 'tableplus',
  password: process.env.PGPASSWORD || 'tableplus',
  ssl: process.env.PGSSL === 'true' ? { rejectUnauthorized: false } : false
});

pool.query('SELECT 1')
  .then(() => {
    console.log('✅ Database connection successful');
    process.exit(0);
  })
  .catch(err => {
    console.error('❌ Database connection failed:', err.message);
    process.exit(1);
  });
"
cd ..

if [ $? -eq 0 ]; then
    echo "✅ Database connection test passed"
else
    echo "❌ Database connection test failed"
    echo "   Please check your database configuration and try again."
    exit 1
fi

# Set API port (default 3001 to avoid conflict with frontend on 3000)
export API_PORT=3001

# Start the API server
API_PORT=${API_PORT:-3001}
echo "🚀 Starting API server..."
echo "   API will be available at: http://localhost:$API_PORT"
echo "   Health check: http://localhost:$API_PORT/health"
echo "   Dashboards: http://localhost:$API_PORT"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd src
node database-api-server.js
