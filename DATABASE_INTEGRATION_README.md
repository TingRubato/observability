# Database Integration for Observable Framework

This document explains how to integrate PostgreSQL database connectivity with the Observable Framework dashboards, replacing file-based data loading with real-time database queries.

## Overview

The integration provides:
- **Database API Server**: REST API endpoints for database access
- **Database Connection Utilities**: JavaScript modules for Observable dashboards
- **Fallback Mechanism**: Automatic fallback to file-based data if database is unavailable
- **Live Data Polling**: Real-time data updates without page refreshes

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Observable    │    │   Database API   │    │   PostgreSQL    │
│   Dashboards    │◄──►│     Server       │◄──►│    Database     │
│                 │    │   (Port 3000)    │    │   (Port 5432)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Quick Start

### 1. Prerequisites

- Node.js 16+ installed
- PostgreSQL database with Mazak manufacturing data
- Environment variables configured (see Configuration section)

### 2. Start the Database API Server

```bash
# Make the startup script executable
chmod +x start-database-api.sh

# Start the server
./start-database-api.sh
```

The server will be available at:
- **API Base**: http://localhost:3000/api
- **Health Check**: http://localhost:3000/health
- **Dashboards**: http://localhost:3000

### 3. Update Dashboard Files

The dashboard files have been updated to use database connections:

```javascript
// Import database utilities
import { createDatabaseConnection, loadDataWithFallback } from "./database-connection.js";

// Load data from database with fallback to files
const machines = await loadDataWithFallback('machines');
const machineSummary = await loadDataWithFallback('machineSummary');
```

## Configuration

### Environment Variables

Create a `.env` file or set these environment variables:

```bash
# Database Configuration
PGHOST=localhost
PGPORT=5432
PGDATABASE=mazak_manufacturing
PGUSER=postgres
PGPASSWORD=your_password
PGSSL=false

# API Server Configuration
API_PORT=3000
```

### Database Schema

The integration expects the following database schema (based on the existing Mazak manufacturing database):

#### Core Tables
- `machines` - Machine information and configuration
- `machine_components` - Machine components (axes, spindle, etc.)
- `machine_conditions` - Condition data (temperature, load, etc.)
- `machine_samples` - Sample data (position, speed, etc.)
- `machine_events` - Event data (alarms, program changes, etc.)

#### Key Relationships
- Machines → Components (1:many)
- Components → Conditions/Samples/Events (1:many)

## API Endpoints

### Health Check
```
GET /health
```
Returns server and database status.

### Generic Query
```
POST /api/query
Content-Type: application/json

{
  "sql": "SELECT * FROM machines WHERE is_active = true",
  "params": []
}
```

### Machine Data
```
GET /api/machines                    # All machines
GET /api/machines/summary           # Machine summary with status
GET /api/machines/:id/components    # Machine components
GET /api/machines/:id/timeseries    # Time series data
```

### Recent Data
```
GET /api/conditions/recent?hours=1&machine_id=123
GET /api/events/recent?hours=1&machine_id=123
GET /api/samples/recent?hours=1&machine_id=123
```

## Database Connection Utilities

### Basic Usage

```javascript
import { createDatabaseConnection, loadDataWithFallback } from "./database-connection.js";

// Create connection
const db = createDatabaseConnection({
  host: 'localhost',
  port: 3000,
  database: 'mazak_manufacturing'
});

// Load data with fallback
const machines = await loadDataWithFallback('machines');
```

### Live Data Polling

```javascript
import { DatabaseLivePoller } from "./database-connection.js";

// Create live poller
const livePoller = new DatabaseLivePoller({
  host: 'localhost',
  port: 3000,
  interval: 30000 // 30 seconds
});

// Start polling
await livePoller.start();

// Listen for updates
livePoller.addEventListener((data) => {
  console.log('New data received:', data);
});
```

## Updated Dashboard Files

The following dashboard files have been updated to use database connections:

### Live Dashboards
- `src/live-dashboard.md` - Basic live dashboard
- `src/merged-live-dashboard.md` - Enhanced live dashboard with polling
- `src/realtime-dashboard.md` - Real-time monitoring dashboard

### Machine-Specific Dashboards
- `src/mazak-vtc300-enhanced.md` - VTC 300 machine dashboard
- `src/mazak-vtc200.md` - VTC 200 machine dashboard
- `src/mazak-350msy.md` - 350MSY machine dashboard

### Example Dashboard Updates

**Before (File-based):**
```javascript
const machines = FileAttachment("data/loaders/machines.json").json();
const machineSummary = FileAttachment("data/loaders/machine-summary.json").json();
```

**After (Database-based):**
```javascript
import { loadDataWithFallback } from "./database-connection.js";

const machines = await loadDataWithFallback('machines');
const machineSummary = await loadDataWithFallback('machineSummary');
```

## Fallback Mechanism

The integration includes automatic fallback to file-based data if the database is unavailable:

1. **Primary**: Attempts to load data from PostgreSQL database
2. **Fallback**: If database fails, loads data from JSON files
3. **Error Handling**: Graceful degradation with user notifications

## Performance Considerations

### Database Optimization
- Indexes on timestamp columns for time-series queries
- Connection pooling for concurrent requests
- Query result caching for frequently accessed data

### API Server Optimization
- Express.js with connection pooling
- CORS enabled for cross-origin requests
- Error handling and logging

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```
   Error: Database connection failed: connection refused
   ```
   - Check PostgreSQL is running
   - Verify connection parameters
   - Check firewall settings

2. **API Server Won't Start**
   ```
   Error: Port 3000 already in use
   ```
   - Change API_PORT environment variable
   - Kill existing process on port 3000

3. **Dashboard Shows "Loading..." Forever**
   - Check API server is running
   - Verify database connectivity
   - Check browser console for errors

### Debug Mode

Enable debug logging:
```bash
DEBUG=* node database-api-server.js
```

### Health Check

Test the API server:
```bash
curl http://localhost:3000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

## Development

### Adding New Endpoints

1. Add route to `database-api-server.js`
2. Update `database-connection.js` with new methods
3. Test with Observable dashboard

### Custom Queries

```javascript
// Custom database query
const customData = await db.query(`
  SELECT machine_name, COUNT(*) as event_count
  FROM machine_events 
  WHERE timestamp > NOW() - INTERVAL '1 hour'
  GROUP BY machine_name
`);
```

## Security Considerations

- Database credentials stored in environment variables
- API server runs on localhost by default
- No authentication implemented (add if needed for production)
- SSL/TLS support available for database connections

## Production Deployment

For production deployment:

1. **Environment Variables**: Use secure secret management
2. **SSL/TLS**: Enable for database connections
3. **Authentication**: Add API authentication
4. **Monitoring**: Add logging and monitoring
5. **Scaling**: Consider load balancing for multiple API servers

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API server logs
3. Test database connectivity independently
4. Verify environment variables are set correctly
