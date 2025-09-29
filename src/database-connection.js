// Database Connection Utility for Observable Framework
// Provides database connectivity and data loading functions

class DatabaseConnection {
  constructor(config = {}) {
    this.config = {
      host: config.host || 'localhost',
      port: config.port || 5432,
      database: config.database || 'mazak_manufacturing',
      username: config.username || 'postgres',
      password: config.password || '',
      ssl: config.ssl || false,
      ...config
    };
    this.connection = null;
  }

  async connect() {
    try {
      // For Observable Framework, we'll use a REST API approach
      // since direct database connections aren't supported in the browser
      this.apiBase = this.config.apiBase || `http://${this.config.host}:${this.config.port || 3000}/api`;
      console.log(`🔗 Database connection configured for API: ${this.apiBase}`);
      return true;
    } catch (error) {
      console.error('Database connection failed:', error);
      throw error;
    }
  }

  async query(sql, params = []) {
    try {
      const url = `${this.apiBase}/query`;
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sql, params })
      });

      if (!response.ok) {
        throw new Error(`Database query failed: ${response.statusText}`);
      }

      const result = await response.json();
      return result.data;
    } catch (error) {
      console.error('Database query error:', error);
      throw error;
    }
  }

  async getMachines() {
    const sql = `
      SELECT 
        m.machine_id,
        m.name,
        m.machine_model,
        m.machine_series,
        m.device_name,
        m.device_uuid,
        m.location,
        m.installation_date,
        m.manufacturer,
        m.asset_id,
        m.is_active,
        m.created_at,
        m.updated_at,
        COUNT(DISTINCT mc.component_id) as total_components,
        COUNT(DISTINCT CASE WHEN mc.has_conditions THEN mc.component_id END) as components_with_conditions,
        COUNT(DISTINCT CASE WHEN mc.has_samples THEN mc.component_id END) as components_with_samples,
        COUNT(DISTINCT CASE WHEN mc.has_events THEN mc.component_id END) as components_with_events
      FROM machines m
      LEFT JOIN machine_components mc ON m.machine_id = mc.machine_id
      WHERE m.is_active = true
      GROUP BY m.machine_id, m.machine_name, m.machine_model, m.machine_series, 
               m.device_name, m.device_uuid, m.location, m.installation_date, 
               m.manufacturer, m.asset_id, m.is_active, m.created_at, m.updated_at
      ORDER BY m.machine_name
    `;
    return await this.query(sql);
  }

  async getMachineSummary() {
    const sql = `
      SELECT 
        m.machine_id,
        m.name,
        m.machine_model,
        m.device_name,
        m.location,
        COUNT(DISTINCT mc.component_id) as total_components,
        COUNT(DISTINCT CASE WHEN mc.has_conditions THEN mc.component_id END) as components_with_conditions,
        COUNT(DISTINCT CASE WHEN mc.has_samples THEN mc.component_id END) as components_with_samples,
        COUNT(DISTINCT CASE WHEN mc.has_events THEN mc.component_id END) as components_with_events,
        COALESCE(MAX(mc.updated_at), m.created_at) as last_activity,
        CASE 
          WHEN COALESCE(MAX(mc.updated_at), m.created_at) > NOW() - INTERVAL '1 hour' THEN 'online'
          WHEN COALESCE(MAX(mc.updated_at), m.created_at) > NOW() - INTERVAL '24 hours' THEN 'idle'
          ELSE 'offline'
        END as status
      FROM machines m
      LEFT JOIN machine_components mc ON m.machine_id = mc.machine_id
      WHERE m.is_active = true
      GROUP BY m.machine_id, m.machine_name, m.machine_model, m.device_name, m.location, m.created_at
      ORDER BY m.machine_name
    `;
    return await this.query(sql);
  }

  async getRecentConditions(machineId = null, hours = 1) {
    let sql = `
      SELECT 
        mc.condition_id,
        ds.machine_id,
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
    
    if (machineId) {
      sql += ` AND ds.machine_id = $1`;
      return await this.query(sql, [machineId]);
    }
    
    return await this.query(sql);
  }

  async getRecentEvents(machineId = null, hours = 1) {
    let sql = `
      SELECT 
        me.event_id,
        ds.machine_id,
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
    
    if (machineId) {
      sql += ` AND ds.machine_id = $1`;
      return await this.query(sql, [machineId]);
    }
    
    return await this.query(sql);
  }

  async getRecentSamples(machineId = null, hours = 1) {
    let sql = `
      SELECT 
        ms.sample_id,
        ds.machine_id,
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
    
    if (machineId) {
      sql += ` AND ds.machine_id = $1`;
      return await this.query(sql, [machineId]);
    }
    
    return await this.query(sql);
  }

  async getMachineData(machineName) {
    const sql = `
      SELECT
        m.id as machine_id,
        m.name,
        m.model,
        m.ip_address,
        COALESCE(m.asset_id, 'Unknown') as location,
        COUNT(DISTINCT mc.id) as total_components
      FROM machines m
      LEFT JOIN components mc ON m.id = mc.machine_id
      WHERE m.name = $1 AND m.status = 'ACTIVE'
      GROUP BY m.id, m.name, m.model, m.ip_address, m.asset_id
    `;
    
    const result = await this.query(sql, [machineName]);
    return result[0] || null;
  }

  async getMachineComponents(machineId) {
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
        true as is_active
      FROM components
      WHERE machine_id = $1
      ORDER BY component_name
    `;
    
    return await this.query(sql, [machineId]);
  }

  async getTimeSeriesData(machineId, componentId = null, hours = 24) {
    const sql = `
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
    `;
    
    const params = componentId ? [machineId, componentId] : [machineId];
    return await this.query(sql, params);
  }

  async disconnect() {
    // For API-based connections, no explicit disconnect needed
    console.log('🔌 Database connection closed');
  }
}

// Factory function to create database connection
export function createDatabaseConnection(config = {}) {
  return new DatabaseConnection(config);
}

// Default database configuration
export const defaultDbConfig = {
  host: 'localhost',
  port: 3001,
  database: 'mazak',
  apiBase: 'http://localhost:3001/api'
};

// Utility function to load data with fallback to files
export async function loadDataWithFallback(dataType, machineName = null, config = {}) {
  try {
    const db = createDatabaseConnection({ ...defaultDbConfig, ...config });
    await db.connect();
    
    let data;
    switch (dataType) {
      case 'machines':
        data = await db.getMachines();
        break;
      case 'machineSummary':
        data = await db.getMachineSummary();
        break;
      case 'recentConditions':
        data = await db.getRecentConditions(machineName);
        break;
      case 'recentEvents':
        data = await db.getRecentEvents(machineName);
        break;
      case 'recentSamples':
        data = await db.getRecentSamples(machineName);
        break;
      case 'timeSeries':
        data = await db.getTimeSeriesData(machineName);
        break;
      default:
        throw new Error(`Unknown data type: ${dataType}`);
    }
    
    await db.disconnect();
    return data;
  } catch (error) {
    console.warn(`Database loading failed for ${dataType}, falling back to files:`, error);
    
    // Fallback to file loading (only works in Observable Framework)
    const fallbackFiles = {
      machines: 'data/loaders/machines.json',
      machineSummary: 'data/loaders/machine-summary.json',
      recentConditions: 'data/loaders/recent-conditions.json',
      recentEvents: 'data/loaders/recent-events.json',
      recentSamples: 'data/loaders/recent-samples.json'
    };

    const filePath = fallbackFiles[dataType];
    if (filePath && typeof FileAttachment !== 'undefined') {
      return FileAttachment(filePath).json();
    }

    // If FileAttachment is not available (Node.js environment), return mock data
    if (dataType === 'machines') {
      return [
        { machine_id: 1, machine_name: 'mazak_1_vtc_200', machine_model: 'VTC-200', total_components: 5, is_active: true },
        { machine_id: 2, machine_name: 'mazak_2_vtc_300', machine_model: 'VTC-300', total_components: 8, is_active: true },
        { machine_id: 3, machine_name: 'mazak_3_350msy', machine_model: '350MSY', total_components: 12, is_active: true }
      ];
    }
    
    throw error;
  }
}

// Live data polling with database integration
export class DatabaseLivePoller {
  constructor(config = {}) {
    this.config = { ...defaultDbConfig, ...config };
    this.db = createDatabaseConnection(this.config);
    this.interval = config.interval || 30000;
    this.isPolling = false;
    this.pollTimer = null;
    this.listeners = new Set();
  }

  async start() {
    if (this.isPolling) return;
    
    this.isPolling = true;
    await this.db.connect();
    
    // Initial data fetch
    await this.fetchData();
    
    // Set up polling
    this.pollTimer = setInterval(async () => {
      if (document.visibilityState === 'visible') {
        await this.fetchData();
      }
    }, this.interval);
  }

  async stop() {
    if (!this.isPolling) return;
    
    this.isPolling = false;
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
    await this.db.disconnect();
  }

  async fetchData() {
    try {
      const [machines, summary, conditions, events] = await Promise.all([
        this.db.getMachines(),
        this.db.getMachineSummary(),
        this.db.getRecentConditions(),
        this.db.getRecentEvents()
      ]);
      
      const data = {
        machines,
        summary,
        conditions,
        events,
        timestamp: new Date().toISOString()
      };
      
      this.notifyListeners(data);
      return data;
    } catch (error) {
      console.error('Database polling error:', error);
      throw error;
    }
  }

  addEventListener(callback) {
    this.listeners.add(callback);
  }

  removeEventListener(callback) {
    this.listeners.delete(callback);
  }

  notifyListeners(data) {
    this.listeners.forEach(callback => callback(data));
  }
}

// Note: DatabaseLivePoller is already exported as a class above
// Additional exports can be added here if needed
