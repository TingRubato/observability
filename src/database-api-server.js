#!/usr/bin/env node
/**
 * Database API Server for Observable Framework
 * 
 * This server provides REST API endpoints to access PostgreSQL database
 * data for the Observable dashboards, since direct database connections
 * aren't supported in the browser environment.
 * 
 * Usage:
 *   node database-api-server.js
 * 
 * Environment Variables:
 *   - PGHOST: PostgreSQL host (default: 100.83.52.87)
 *   - PGPORT: PostgreSQL port (default: 5432)
 *   - PGDATABASE: Database name (default: mazak)
 *   - PGUSER: Database username (default: tableplus)
 *   - PGPASSWORD: Database password
 *   - API_PORT: API server port (default: 3001)
 */

import express from 'express';
import cors from 'cors';
import { Pool } from 'pg';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Get __dirname equivalent in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.API_PORT || 3001;

// Database connection configuration
const dbConfig = {
  host: process.env.PGHOST || '100.83.52.87',
  port: parseInt(process.env.PGPORT) || 5432,
  database: process.env.PGDATABASE || 'mazak',
  user: process.env.PGUSER || 'tableplus',
  password: process.env.PGPASSWORD || 'tableplus',
  ssl: process.env.PGSSL === 'true' ? { rejectUnauthorized: false } : false,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
};

// Create database connection pool
const pool = new Pool(dbConfig);

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../dist')));

// Database connection test
pool.on('connect', () => {
  console.log('🔗 Connected to PostgreSQL database');
});

pool.on('error', (err) => {
  console.error('❌ Database connection error:', err);
});

// Health check endpoint
app.get('/health', async (req, res) => {
  try {
    const client = await pool.connect();
    await client.query('SELECT 1');
    client.release();
    res.json({ status: 'healthy', database: 'connected' });
  } catch (error) {
    res.status(500).json({ status: 'unhealthy', error: error.message });
  }
});

// Generic query endpoint
app.post('/api/query', async (req, res) => {
  try {
    const { sql, params = [] } = req.body;
    
    if (!sql) {
      return res.status(400).json({ error: 'SQL query is required' });
    }
    
    const client = await pool.connect();
    const result = await client.query(sql, params);
    client.release();
    
    res.json({ 
      success: true, 
      data: result.rows,
      rowCount: result.rowCount 
    });
  } catch (error) {
    console.error('Query error:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// Get all machines
app.get('/api/machines', async (req, res) => {
  try {
    const sql = `
      SELECT 
        m.id as machine_id,
        m.name,
        m.model,
        m.series,
        m.ip_address,
        m.uuid,
        COALESCE(m.asset_id, 'Unknown') as location,
        m.created_at as installation_date,
        COALESCE(m.model, 'Unknown') as manufacturer,
        m.asset_id,
        (m.status = 'ACTIVE') as is_active,
        m.created_at,
        m.updated_at,
        COUNT(DISTINCT mc.component_id) as total_components,
        0 as components_with_conditions,
        0 as components_with_samples,
        0 as components_with_events
      FROM machines m
      LEFT JOIN components mc ON m.id = mc.machine_id
      WHERE m.status = 'ACTIVE'
      GROUP BY m.id, m.name, m.model, m.series,
               m.uuid, m.ip_address, m.asset_id, m.created_at,
               m.updated_at, m.status
      ORDER BY m.name
    `;
    
    const result = await pool.query(sql);
    res.json(result.rows);
  } catch (error) {
    console.error('Machines query error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get machine summary
app.get('/api/machines/summary', async (req, res) => {
  try {
    const sql = `
      SELECT 
        m.id as machine_id,
        m.name,
        m.model,
        m.ip_address,
        COALESCE(m.asset_id, 'Unknown') as location,
        COUNT(DISTINCT mc.component_id) as total_components,
        0 as components_with_conditions,
        0 as components_with_samples,
        0 as components_with_events,
        COALESCE(MAX(mc.updated_at), m.created_at) as last_activity,
        CASE 
          WHEN COALESCE(MAX(mc.updated_at), m.created_at) > NOW() - INTERVAL '1 hour' THEN 'online'
          WHEN COALESCE(MAX(mc.updated_at), m.created_at) > NOW() - INTERVAL '24 hours' THEN 'idle'
          ELSE 'offline'
        END as status
      FROM machines m
      LEFT JOIN components mc ON m.id = mc.machine_id
      WHERE m.status = 'ACTIVE'
      GROUP BY m.id, m.name, m.model, m.ip_address, m.asset_id, m.created_at
      ORDER BY m.name
    `;
    
    const result = await pool.query(sql);
    res.json(result.rows);
  } catch (error) {
    console.error('Machine summary query error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get recent conditions
app.get('/api/conditions/recent', async (req, res) => {
  try {
    const hours = parseInt(req.query.hours) || 1;
    const machineId = req.query.machine_id;
    
    let sql = `
      SELECT 
        mc.condition_id,
        mc.machine_id,
        m.name,
        mc.component_id,
        comp.component_name,
        mc.condition_name,
        mc.timestamp,
        mc.sequence_number,
        mc.state,
        mc.category
      FROM conditions mc
      JOIN data_streams ds ON mc.data_stream_id = ds.id
      JOIN machines m ON ds.machine_id = m.id
      JOIN components comp ON mc.component_id = comp.id
      WHERE mc.timestamp > NOW() - INTERVAL '${hours} hours'
    `;
    
    const params = [];
    if (machineId) {
      sql += ` AND mc.data_stream_id IN (SELECT id FROM data_streams WHERE machine_id = $1)`;
      params.push(machineId);
    }
    
    sql += ` ORDER BY mc.timestamp DESC LIMIT 1000`;
    
    const result = await pool.query(sql, params);
    res.json(result.rows);
  } catch (error) {
    console.error('Recent conditions query error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get recent events
app.get('/api/events/recent', async (req, res) => {
  try {
    const hours = parseInt(req.query.hours) || 1;
    const machineId = req.query.machine_id;
    
    let sql = `
      SELECT 
        me.event_id,
        me.machine_id,
        m.name,
        me.component_id,
        comp.component_name,
        me.event_name,
        me.timestamp,
        me.sequence_number,
        me.value,
        me.event_type,
        me.severity
      FROM events me
      JOIN data_streams ds ON me.data_stream_id = ds.id
      JOIN machines m ON ds.machine_id = m.id
      JOIN components comp ON me.component_id = comp.id
      WHERE me.timestamp > NOW() - INTERVAL '${hours} hours'
    `;
    
    const params = [];
    if (machineId) {
      sql += ` AND me.machine_id = $1`;
      params.push(machineId);
    }
    
    sql += ` ORDER BY me.timestamp DESC LIMIT 1000`;
    
    const result = await pool.query(sql, params);
    res.json(result.rows);
  } catch (error) {
    console.error('Recent events query error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get recent samples
app.get('/api/samples/recent', async (req, res) => {
  try {
    const hours = parseInt(req.query.hours) || 1;
    const machineId = req.query.machine_id;
    
    let sql = `
      SELECT 
        ms.sample_id,
        ms.machine_id,
        m.name,
        ms.component_id,
        comp.component_name,
        ms.sample_name,
        ms.timestamp,
        ms.sequence_number,
        ms.value,
        ms.sub_type,
        ms.unit
      FROM samples ms
      JOIN data_streams ds ON ms.data_stream_id = ds.id
      JOIN machines m ON ds.machine_id = m.id
      JOIN components comp ON ms.component_id = comp.id
      WHERE ms.timestamp > NOW() - INTERVAL '${hours} hours'
    `;
    
    const params = [];
    if (machineId) {
      sql += ` AND ms.machine_id = $1`;
      params.push(machineId);
    }
    
    sql += ` ORDER BY ms.timestamp DESC LIMIT 1000`;
    
    const result = await pool.query(sql, params);
    res.json(result.rows);
  } catch (error) {
    console.error('Recent samples query error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get time series data for a specific machine
app.get('/api/machines/:machineId/timeseries', async (req, res) => {
  try {
    const { machineId } = req.params;
    const hours = parseInt(req.query.hours) || 24;
    const componentId = req.query.component_id;
    
    let sql = `
      SELECT 
        'sample' as data_type,
        ms.sample_name as name,
        ms.timestamp,
        ms.value as value,
        ms.sub_type,
        ms.unit,
        comp.component_name
      FROM samples ms
      JOIN data_streams ds ON ms.data_stream_id = ds.id
      JOIN components comp ON ms.component_id = comp.id
      WHERE ds.machine_id = $1 
        AND ms.timestamp > NOW() - INTERVAL '${hours} hours'
        ${componentId ? 'AND ms.component_id = $2' : ''}
      
      UNION ALL
      
      SELECT 
        'condition' as data_type,
        mc.condition_name as name,
        mc.timestamp,
        mc.state as value,
        mc.category as sub_type,
        NULL as unit,
        comp.component_name
      FROM conditions mc
      JOIN data_streams ds ON mc.data_stream_id = ds.id
      JOIN components comp ON mc.component_id = comp.id
      WHERE ds.machine_id = $1 
        AND mc.timestamp > NOW() - INTERVAL '${hours} hours'
        ${componentId ? 'AND mc.component_id = $2' : ''}
      
      ORDER BY timestamp DESC
      LIMIT 5000
    `;
    
    const params = componentId ? [machineId, componentId] : [machineId];
    const result = await pool.query(sql, params);
    res.json(result.rows);
  } catch (error) {
    console.error('Time series query error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get machine components
app.get('/api/machines/:machineId/components', async (req, res) => {
  try {
    const { machineId } = req.params;
    
    const sql = `
      SELECT
        id as component_id,
        component_id,
        component_name,
        false as has_conditions,
        false as has_samples,
        false as has_events,
        0 as conditions_count,
        0 as samples_count,
        0 as events_count,
        is_active
      FROM components
      WHERE machine_id = $1
      ORDER BY component_name
    `;
    
    const result = await pool.query(sql, [machineId]);
    res.json(result.rows);
  } catch (error) {
    console.error('Machine components query error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Serve static files (Observable dashboards)
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../dist/index.html'));
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Server error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

// Graceful shutdown
let isShuttingDown = false;

const gracefulShutdown = async (signal) => {
  console.log(`\n🛑 Received ${signal}. Starting graceful shutdown...`);

  if (isShuttingDown) {
    console.log('⚠️  Shutdown already in progress, forcing exit...');
    process.exit(1);
  }

  isShuttingDown = true;

  // Stop accepting new connections
  server.close(async () => {
    console.log('✅ HTTP server closed');

    try {
      // Close database pool
      await pool.end();
      console.log('✅ Database pool closed');
    } catch (error) {
      console.error('❌ Error closing database pool:', error);
    }

    console.log('✅ Graceful shutdown complete');
    process.exit(0);
  });

  // Force exit after 10 seconds if graceful shutdown fails
  setTimeout(() => {
    console.error('❌ Could not close connections in time, forcefully shutting down');
    process.exit(1);
  }, 10000);
};

process.on('SIGINT', () => gracefulShutdown('SIGINT'));
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));

// Start server
const server = app.listen(PORT, () => {
  console.log(`🚀 Database API server running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`🔗 API base: http://localhost:${PORT}/api`);
  console.log(`📈 Dashboards: http://localhost:${PORT}`);
});

export default app;
