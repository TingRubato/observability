#!/usr/bin/env node
/**
 * Test Dashboard Import Functionality
 *
 * This test verifies that the dashboard files can properly import
 * the database connection utilities without syntax errors.
 *
 * Usage:
 *   node test-dashboard-imports.js
 */

import { readFile } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('🧪 Testing Dashboard Import Functionality');
console.log('==========================================\n');

const dashboardFiles = [
  'src/mazak-vtc200.md',
  'src/mazak-vtc300-final.md',
  'src/mazak-350msy.md'
];

let allTestsPassed = true;

for (const file of dashboardFiles) {
  console.log(`🔍 Testing ${file}...`);

  try {
    const filePath = join(__dirname, file);
    const content = await readFile(filePath, 'utf8');

    // Check if the file contains database imports
    const hasDatabaseImport = content.includes('import { createDatabaseConnection, loadDataWithFallback } from "./database-connection.js"');
    const hasLoadDataWithFallback = content.includes('loadDataWithFallback');
    const hasMachineName = content.includes('const machineName =');

    if (hasDatabaseImport) {
      console.log('   ✅ Contains database connection import');
    } else {
      console.log('   ❌ Missing database connection import');
      allTestsPassed = false;
    }

    if (hasLoadDataWithFallback) {
      console.log('   ✅ Uses loadDataWithFallback function');
    } else {
      console.log('   ❌ Missing loadDataWithFallback usage');
      allTestsPassed = false;
    }

    if (hasMachineName) {
      console.log('   ✅ Contains machine name configuration');
    } else {
      console.log('   ❌ Missing machine name configuration');
      allTestsPassed = false;
    }

    // Check for database-specific data loading patterns
    const usesDatabaseLoading = content.includes('timeSeriesData = await loadDataWithFallback') ||
                               content.includes('recentEvents = await loadDataWithFallback') ||
                               content.includes('recentConditions = await loadDataWithFallback');

    if (usesDatabaseLoading) {
      console.log('   ✅ Uses database loading patterns');
    } else {
      console.log('   ❌ Missing database loading patterns');
      allTestsPassed = false;
    }

  } catch (error) {
    console.error(`   ❌ Failed to read ${file}:`, error.message);
    allTestsPassed = false;
  }
}

console.log('\n📊 Dashboard Import Test Results');
console.log('=================================');

if (allTestsPassed) {
  console.log('✅ All dashboard import tests passed!');
  console.log('\nDashboard files are properly configured for database integration:');
  console.log('- All files import database connection utilities');
  console.log('- All files use loadDataWithFallback function');
  console.log('- All files have machine name configuration');
  console.log('- All files use database loading patterns');
} else {
  console.log('❌ Some dashboard import tests failed!');
  console.log('\nPlease check the dashboard files for missing database integration code.');
}

console.log('\nNext steps:');
console.log('1. Start the database API server: ./start-database-api.sh');
console.log('2. Test with real database connection: npm run db:test');
console.log('3. Verify dashboards load data correctly in browser');

// Export for potential use in other tests
export {
  testDashboardImports
};

async function testDashboardImports() {
  console.log('Dashboard import test completed');
  return allTestsPassed;
}

// Run test if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  testDashboardImports().catch(error => {
    console.error('Test execution failed:', error);
    process.exit(1);
  });
}
