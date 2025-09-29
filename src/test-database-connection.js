#!/usr/bin/env node
/**
 * Test Database Connection for Observable Framework
 * 
 * This script tests the database connection and API endpoints
 * to ensure everything is working correctly.
 * 
 * Usage:
 *   node test-database-connection.js
 */

import pkg from 'pg';
const { Pool } = pkg;
import fetch from 'node-fetch';
import dotenv from 'dotenv';

dotenv.config();

// Database configuration
const dbConfig = {
  host: process.env.PGHOST || 'localhost',
  port: parseInt(process.env.PGPORT) || 5432,
  database: process.env.PGDATABASE || 'mazak_manufacturing',
  user: process.env.PGUSER || 'postgres',
  password: process.env.PGPASSWORD || '',
  ssl: process.env.PGSSL === 'true' ? { rejectUnauthorized: false } : false,
};

const API_BASE = 'http://localhost:3001';

async function testDatabaseConnection() {
  console.log('🔍 Testing database connection...');
  console.log(`   Host: ${dbConfig.host}:${dbConfig.port}`);
  console.log(`   Database: ${dbConfig.database}`);
  console.log(`   User: ${dbConfig.user}`);
  
  try {
    const pool = new Pool(dbConfig);
    const client = await pool.connect();
    
    // Test basic connection
    const result = await client.query('SELECT 1 as test');
    console.log('✅ Database connection successful');
    
    // Test table existence
    const tablesResult = await client.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      AND table_name IN ('machines', 'components', 'conditions', 'samples', 'events')
      ORDER BY table_name
    `);
    
    console.log(`📊 Found ${tablesResult.rows.length} required tables:`);
    tablesResult.rows.forEach(row => {
      console.log(`   - ${row.table_name}`);
    });
    
    // Test data counts
    const counts = await Promise.all([
      client.query('SELECT COUNT(*) as count FROM machines WHERE is_active = true'),
      client.query('SELECT COUNT(*) as count FROM components'),
      client.query('SELECT COUNT(*) as count FROM conditions WHERE timestamp > NOW() - INTERVAL \'24 hours\''),
      client.query('SELECT COUNT(*) as count FROM samples WHERE timestamp > NOW() - INTERVAL \'24 hours\''),
      client.query('SELECT COUNT(*) as count FROM events WHERE timestamp > NOW() - INTERVAL \'24 hours\'')
    ]);
    
    console.log('📈 Data counts (last 24 hours):');
    console.log(`   - Active machines: ${counts[0].rows[0].count}`);
    console.log(`   - Active components: ${counts[1].rows[0].count}`);
    console.log(`   - Conditions: ${counts[2].rows[0].count}`);
    console.log(`   - Samples: ${counts[3].rows[0].count}`);
    console.log(`   - Events: ${counts[4].rows[0].count}`);
    
    client.release();
    await pool.end();
    
    return true;
  } catch (error) {
    console.error('❌ Database connection failed:', error.message);
    return false;
  }
}

async function testAPIServer() {
  console.log('\n🔍 Testing API server...');
  
  try {
    // Test health endpoint
    const healthResponse = await fetch(`${API_BASE}/health`);
    if (!healthResponse.ok) {
      throw new Error(`Health check failed: ${healthResponse.status}`);
    }
    const healthData = await healthResponse.json();
    console.log('✅ API server health check passed');
    console.log(`   Status: ${healthData.status}`);
    console.log(`   Database: ${healthData.database}`);
    
    // Test machines endpoint
    const machinesResponse = await fetch(`${API_BASE}/api/machines`);
    if (!machinesResponse.ok) {
      throw new Error(`Machines endpoint failed: ${machinesResponse.status}`);
    }
    const machines = await machinesResponse.json();
    console.log(`✅ Machines endpoint working (${machines.length} machines)`);
    
    // Test machine summary endpoint
    const summaryResponse = await fetch(`${API_BASE}/api/machines/summary`);
    if (!summaryResponse.ok) {
      throw new Error(`Machine summary endpoint failed: ${summaryResponse.status}`);
    }
    const summary = await summaryResponse.json();
    console.log(`✅ Machine summary endpoint working (${summary.length} machines)`);
    
    // Test recent data endpoints
    const conditionsResponse = await fetch(`${API_BASE}/api/conditions/recent?hours=1`);
    if (!conditionsResponse.ok) {
      throw new Error(`Recent conditions endpoint failed: ${conditionsResponse.status}`);
    }
    const conditions = await conditionsResponse.json();
    console.log(`✅ Recent conditions endpoint working (${conditions.length} records)`);
    
    return true;
  } catch (error) {
    console.error('❌ API server test failed:', error.message);
    console.log('   Make sure the API server is running: ./start-database-api.sh');
    return false;
  }
}

async function testDashboardIntegration() {
  console.log('\n🔍 Testing dashboard integration...');
  
  try {
    // Test database connection utilities
    const { createDatabaseConnection, loadDataWithFallback } = require('./database-connection.js');
    
    console.log('✅ Database connection utilities loaded');
    
    // Test connection creation
    const db = createDatabaseConnection({
      host: 'localhost',
      port: 3000,
      database: 'mazak_manufacturing'
    });
    
    console.log('✅ Database connection object created');
    
    return true;
  } catch (error) {
    console.error('❌ Dashboard integration test failed:', error.message);
    return false;
  }
}

async function runAllTests() {
  console.log('🧪 Running Database Integration Tests');
  console.log('=====================================\n');
  
  const results = {
    database: await testDatabaseConnection(),
    api: await testAPIServer(),
    dashboard: await testDashboardIntegration()
  };
  
  console.log('\n📊 Test Results Summary');
  console.log('========================');
  console.log(`Database Connection: ${results.database ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`API Server: ${results.api ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`Dashboard Integration: ${results.dashboard ? '✅ PASS' : '❌ FAIL'}`);
  
  const allPassed = Object.values(results).every(result => result);
  
  if (allPassed) {
    console.log('\n🎉 All tests passed! Database integration is ready.');
    console.log('\nNext steps:');
    console.log('1. Start the API server: ./start-database-api.sh');
    console.log('2. Open dashboards: http://localhost:3000 (frontend) and http://localhost:3001/api (backend)');
    console.log('3. Check individual dashboard files in src/ directory');
  } else {
    console.log('\n❌ Some tests failed. Please check the errors above.');
    console.log('\nTroubleshooting:');
    console.log('1. Verify database is running and accessible');
    console.log('2. Check environment variables are set correctly');
    console.log('3. Ensure required tables exist in the database');
    console.log('4. Start the API server if it\'s not running');
  }
  
  process.exit(allPassed ? 0 : 1);
}

// Run tests if this script is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  runAllTests().catch(error => {
    console.error('Test execution failed:', error);
    process.exit(1);
  });
}

export {
  testDatabaseConnection,
  testAPIServer,
  testDashboardIntegration,
  runAllTests
};
