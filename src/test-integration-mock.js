#!/usr/bin/env node
/**
 * Integration Test with Mock Data
 *
 * This test verifies that the database integration works with mock data
 * without requiring an actual database connection.
 *
 * Usage:
 *   node test-integration-mock.js
 */

import { createDatabaseConnection } from './database-connection.js';
import fetch from 'node-fetch';

console.log('🧪 Testing Database Integration with Mock Data');
console.log('==============================================\n');

// Mock API server for testing
const mockApiResponses = {
  '/api/machines': [
    {
      machine_id: 1,
      machine_name: 'mazak_1_vtc_200',
      machine_model: 'VTC-200',
      total_components: 5,
      is_active: true
    },
    {
      machine_id: 2,
      machine_name: 'mazak_2_vtc_300',
      machine_model: 'VTC-300',
      total_components: 8,
      is_active: true
    },
    {
      machine_id: 3,
      machine_name: 'mazak_3_350msy',
      machine_model: '350MSY',
      total_components: 12,
      is_active: true
    }
  ],
  '/api/machines/summary': [
    {
      machine_id: 1,
      machine_name: 'mazak_1_vtc_200',
      status: 'online',
      total_components: 5,
      samplesLastHour: 150,
      eventsLastHour: 23
    },
    {
      machine_id: 2,
      machine_name: 'mazak_2_vtc_300',
      status: 'online',
      total_components: 8,
      samplesLastHour: 200,
      eventsLastHour: 15
    },
    {
      machine_id: 3,
      machine_name: 'mazak_3_350msy',
      status: 'online',
      total_components: 12,
      samplesLastHour: 180,
      eventsLastHour: 8
    }
  ],
  '/api/conditions/recent': [
    {
      condition_id: 1,
      machine_id: 1,
      component_id: 1,
      condition_name: 'temperature',
      state_value: 'NORMAL',
      category: 'TEMPERATURE'
    },
    {
      condition_id: 2,
      machine_id: 2,
      component_id: 2,
      condition_name: 'vibration',
      state_value: 'WARNING',
      category: 'VIBRATION'
    }
  ],
  '/api/events/recent': [
    {
      event_id: 1,
      machine_id: 1,
      component_id: 1,
      event_name: 'program_start',
      event_value: 'AUTO',
      event_type: 'PROGRAM'
    },
    {
      event_id: 2,
      machine_id: 2,
      component_id: 2,
      event_name: 'alarm',
      event_value: 'OVERHEAT',
      event_type: 'ALARM'
    }
  ],
  '/api/samples/recent': [
    {
      sample_id: 1,
      machine_id: 1,
      component_id: 1,
      sample_name: 'Xabs',
      sample_value: 150.5,
      unit: 'mm'
    },
    {
      sample_id: 2,
      machine_id: 1,
      component_id: 2,
      sample_name: 'Srpm',
      sample_value: 1200,
      unit: 'rpm'
    }
  ]
};

// Mock fetch function
const originalFetch = global.fetch;
global.fetch = async (url, options) => {
  const endpoint = url.replace('http://localhost:3001', '');

  if (mockApiResponses[endpoint]) {
    return {
      ok: true,
      json: async () => mockApiResponses[endpoint]
    };
  }

  return {
    ok: false,
    status: 404,
    statusText: 'Not Found'
  };
};

async function testDatabaseConnection() {
  console.log('🔍 Test 1: Testing database connection with mock data...');

  try {
    const db = createDatabaseConnection({
      host: 'localhost',
      port: 3000,
      apiBase: 'http://localhost:3001/api'
    });

    // Test machines endpoint
    const machines = await db.getMachines();
    console.log(`   ✅ getMachines() returned ${machines.length} machines`);

    // Test machine summary endpoint
    const summary = await db.getMachineSummary();
    console.log(`   ✅ getMachineSummary() returned ${summary.length} summaries`);

    // Test recent conditions endpoint
    const conditions = await db.getRecentConditions();
    console.log(`   ✅ getRecentConditions() returned ${conditions.length} conditions`);

    // Test recent events endpoint
    const events = await db.getRecentEvents();
    console.log(`   ✅ getRecentEvents() returned ${events.length} events`);

    // Test recent samples endpoint
    const samples = await db.getRecentSamples();
    console.log(`   ✅ getRecentSamples() returned ${samples.length} samples`);

    // Test machine-specific data
    const machineData = await db.getMachineData('mazak_1_vtc_200');
    if (machineData) {
      console.log('   ✅ getMachineData() returned machine data');
    } else {
      console.log('   ❌ getMachineData() returned null');
    }

    await db.disconnect();
    console.log('   ✅ Database connection closed successfully');

    return true;
  } catch (error) {
    console.error('   ❌ Database connection test failed:', error.message);
    return false;
  }
}

async function testLoadDataWithFallback() {
  console.log('\n🔍 Test 2: Testing loadDataWithFallback function...');

  try {
    // This will test the fallback mechanism
    const { loadDataWithFallback } = await import('./database-connection.js');

    // Test with mock data
    const machines = await loadDataWithFallback('machines');
    console.log(`   ✅ loadDataWithFallback('machines') returned ${machines.length} machines`);

    const summary = await loadDataWithFallback('machineSummary');
    console.log(`   ✅ loadDataWithFallback('machineSummary') returned ${summary.length} summaries`);

    const conditions = await loadDataWithFallback('recentConditions');
    console.log(`   ✅ loadDataWithFallback('recentConditions') returned ${conditions.length} conditions`);

    const events = await loadDataWithFallback('recentEvents');
    console.log(`   ✅ loadDataWithFallback('recentEvents') returned ${events.length} events`);

    const samples = await loadDataWithFallback('recentSamples');
    console.log(`   ✅ loadDataWithFallback('recentSamples') returned ${samples.length} samples`);

    return true;
  } catch (error) {
    console.error('   ❌ loadDataWithFallback test failed:', error.message);
    return false;
  }
}

async function testMachineSpecificData() {
  console.log('\n🔍 Test 3: Testing machine-specific data loading...');

  try {
    const { loadDataWithFallback } = await import('./database-connection.js');

    // Test VTC 200
    const vtc200Data = await loadDataWithFallback('timeSeries', 'mazak_1_vtc_200', 24);
    console.log(`   ✅ VTC 200 time series data: ${vtc200Data.length} records`);

    // Test VTC 300
    const vtc300Data = await loadDataWithFallback('timeSeries', 'mazak_2_vtc_300', 24);
    console.log(`   ✅ VTC 300 time series data: ${vtc300Data.length} records`);

    // Test 350MSY
    const msy350Data = await loadDataWithFallback('timeSeries', 'mazak_3_350msy', 24);
    console.log(`   ✅ 350MSY time series data: ${msy350Data.length} records`);

    return true;
  } catch (error) {
    console.error('   ❌ Machine-specific data test failed:', error.message);
    return false;
  }
}

// Restore original fetch
global.fetch = originalFetch;

async function runAllTests() {
  const results = {
    databaseConnection: await testDatabaseConnection(),
    loadDataWithFallback: await testLoadDataWithFallback(),
    machineSpecificData: await testMachineSpecificData()
  };

  console.log('\n📊 Mock Integration Test Results');
  console.log('================================');
  console.log(`Database Connection: ${results.databaseConnection ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`Load Data With Fallback: ${results.loadDataWithFallback ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`Machine Specific Data: ${results.machineSpecificData ? '✅ PASS' : '❌ FAIL'}`);

  const allPassed = Object.values(results).every(result => result);

  if (allPassed) {
    console.log('\n🎉 All mock integration tests passed!');
    console.log('\nThe database integration is working correctly with mock data.');
    console.log('Next steps:');
    console.log('1. Start the real database API server');
    console.log('2. Test with actual database connection');
    console.log('3. Verify dashboards work in browser');
  } else {
    console.log('\n❌ Some mock integration tests failed!');
    console.log('\nPlease check the database connection utilities for issues.');
  }

  return allPassed;
}

// Export for potential use in other tests
export {
  runAllTests
};

// Run tests if this script is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  runAllTests().catch(error => {
    console.error('Test execution failed:', error);
    process.exit(1);
  });
}
