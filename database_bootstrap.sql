-- Database Bootstrap Script for Mazak Machine Observability
-- Based on the Mermaid ERD schema
-- Connection: 100.83.52.87:5432, database: mazak, user: tableplus

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types for better data integrity
CREATE TYPE machine_status_enum AS ENUM ('ACTIVE', 'INACTIVE', 'MAINTENANCE', 'OFFLINE');
CREATE TYPE component_type_enum AS ENUM ('LINEAR', 'ROTARY', 'CONTROLLER');
CREATE TYPE stream_type_enum AS ENUM ('CURRENT', 'SAMPLE');
CREATE TYPE sub_type_enum AS ENUM ('ACTUAL', 'COMMANDED');
CREATE TYPE event_type_enum AS ENUM ('PROGRAM', 'SAFETY', 'CONTROL', 'EXECUTION');
CREATE TYPE condition_state_enum AS ENUM ('NORMAL', 'WARNING', 'FAULT');
CREATE TYPE condition_category_enum AS ENUM ('TEMPERATURE', 'LOAD', 'VIBRATION', 'SPEED', 'POSITION');
CREATE TYPE alert_type_enum AS ENUM ('TEMPERATURE_HIGH', 'TEMPERATURE_LOW', 'LOAD_HIGH', 'LOAD_LOW', 'VIBRATION_HIGH', 'SPEED_ANOMALY', 'POSITION_ERROR');
CREATE TYPE alert_severity_enum AS ENUM ('INFO', 'WARNING', 'CRITICAL');

-- Core Entity Tables
CREATE TABLE machines (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    model VARCHAR(50),
    series VARCHAR(50),
    uuid VARCHAR(36) DEFAULT uuid_generate_v4(),
    asset_id VARCHAR(50),
    ip_address INET,
    port INTEGER,
    status machine_status_enum DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE components (
    id SERIAL PRIMARY KEY,
    machine_id INTEGER REFERENCES machines(id) ON DELETE CASCADE,
    component_id VARCHAR(50) NOT NULL,
    component_type component_type_enum,
    component_name VARCHAR(100),
    data_item_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(machine_id, component_id)
);

CREATE TABLE data_streams (
    id SERIAL PRIMARY KEY,
    machine_id INTEGER REFERENCES machines(id) ON DELETE CASCADE,
    stream_type stream_type_enum NOT NULL,
    instance_id VARCHAR(100),
    creation_time TIMESTAMP,
    next_sequence INTEGER DEFAULT 1,
    first_sequence INTEGER DEFAULT 1,
    last_sequence INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Time-Series Data Tables
CREATE TABLE samples (
    id SERIAL PRIMARY KEY,
    data_stream_id INTEGER REFERENCES data_streams(id) ON DELETE CASCADE,
    component_id INTEGER REFERENCES components(id) ON DELETE CASCADE,
    data_item_id VARCHAR(100),
    sample_name VARCHAR(50),
    timestamp TIMESTAMP NOT NULL,
    sequence INTEGER,
    value DECIMAL(15,6),
    sub_type sub_type_enum,
    composition_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    data_stream_id INTEGER REFERENCES data_streams(id) ON DELETE CASCADE,
    component_id INTEGER REFERENCES components(id) ON DELETE CASCADE,
    data_item_id VARCHAR(100),
    event_name VARCHAR(100),
    timestamp TIMESTAMP NOT NULL,
    sequence INTEGER,
    value TEXT,
    event_type event_type_enum,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conditions (
    id SERIAL PRIMARY KEY,
    data_stream_id INTEGER REFERENCES data_streams(id) ON DELETE CASCADE,
    component_id INTEGER REFERENCES components(id) ON DELETE CASCADE,
    data_item_id VARCHAR(100),
    condition_name VARCHAR(100),
    timestamp TIMESTAMP NOT NULL,
    sequence INTEGER,
    state condition_state_enum NOT NULL,
    category condition_category_enum,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analytics Tables
CREATE TABLE machine_status_summary (
    id SERIAL PRIMARY KEY,
    machine_id INTEGER REFERENCES machines(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    hour INTEGER CHECK (hour >= 0 AND hour <= 23),
    total_samples INTEGER DEFAULT 0,
    total_events INTEGER DEFAULT 0,
    total_conditions INTEGER DEFAULT 0,
    avg_temperature DECIMAL(8,2),
    avg_rpm DECIMAL(10,2),
    status machine_status_enum,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(machine_id, date, hour)
);

CREATE TABLE component_alerts (
    id SERIAL PRIMARY KEY,
    machine_id INTEGER REFERENCES machines(id) ON DELETE CASCADE,
    component_id INTEGER REFERENCES components(id) ON DELETE CASCADE,
    alert_type alert_type_enum NOT NULL,
    severity alert_severity_enum NOT NULL,
    message TEXT,
    threshold_value DECIMAL(15,6),
    actual_value DECIMAL(15,6),
    timestamp TIMESTAMP NOT NULL,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Archive Tables (for historical data management)
CREATE TABLE samples_archive (
    id SERIAL PRIMARY KEY,
    data_stream_id INTEGER,
    component_id INTEGER,
    data_item_id VARCHAR(100),
    sample_name VARCHAR(50),
    timestamp TIMESTAMP NOT NULL,
    sequence INTEGER,
    value DECIMAL(15,6),
    sub_type sub_type_enum,
    composition_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE events_archive (
    id SERIAL PRIMARY KEY,
    data_stream_id INTEGER,
    component_id INTEGER,
    data_item_id VARCHAR(100),
    event_name VARCHAR(100),
    timestamp TIMESTAMP NOT NULL,
    sequence INTEGER,
    value TEXT,
    event_type event_type_enum,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_machines_name ON machines(name);
CREATE INDEX idx_machines_ip_address ON machines(ip_address);
CREATE INDEX idx_components_machine_id ON components(machine_id);
CREATE INDEX idx_components_component_id ON components(component_id);
CREATE INDEX idx_data_streams_machine_id ON data_streams(machine_id);
CREATE INDEX idx_samples_timestamp ON samples(timestamp);
CREATE INDEX idx_samples_data_stream_id ON samples(data_stream_id);
CREATE INDEX idx_samples_component_id ON samples(component_id);
CREATE INDEX idx_samples_sample_name ON samples(sample_name);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_data_stream_id ON events(data_stream_id);
CREATE INDEX idx_events_component_id ON events(component_id);
CREATE INDEX idx_events_event_name ON events(event_name);
CREATE INDEX idx_conditions_timestamp ON conditions(timestamp);
CREATE INDEX idx_conditions_data_stream_id ON conditions(data_stream_id);
CREATE INDEX idx_conditions_component_id ON conditions(component_id);
CREATE INDEX idx_conditions_state ON conditions(state);
CREATE INDEX idx_machine_status_summary_machine_date ON machine_status_summary(machine_id, date);
CREATE INDEX idx_component_alerts_machine_id ON component_alerts(machine_id);
CREATE INDEX idx_component_alerts_component_id ON component_alerts(component_id);
CREATE INDEX idx_component_alerts_timestamp ON component_alerts(timestamp);
CREATE INDEX idx_component_alerts_acknowledged ON component_alerts(acknowledged);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for machines table
CREATE TRIGGER update_machines_updated_at BEFORE UPDATE ON machines
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create view for active machines with component count
CREATE VIEW active_machines_view AS
SELECT 
    m.id,
    m.name,
    m.model,
    m.series,
    m.ip_address,
    m.port,
    m.status,
    COUNT(c.id) as component_count,
    m.created_at,
    m.updated_at
FROM machines m
LEFT JOIN components c ON m.id = c.machine_id
WHERE m.status = 'ACTIVE'
GROUP BY m.id, m.name, m.model, m.series, m.ip_address, m.port, m.status, m.created_at, m.updated_at;

-- Create view for latest machine status
CREATE VIEW latest_machine_status AS
SELECT DISTINCT ON (m.id)
    m.id as machine_id,
    m.name as machine_name,
    s.timestamp as last_sample_time,
    s.value as last_rpm_value,
    c.timestamp as last_condition_time,
    c.state as last_condition_state
FROM machines m
LEFT JOIN data_streams ds ON m.id = ds.machine_id
LEFT JOIN samples s ON ds.id = s.data_stream_id AND s.sample_name = 'Srpm'
LEFT JOIN conditions c ON ds.id = c.data_stream_id
WHERE m.status = 'ACTIVE'
ORDER BY m.id, s.timestamp DESC NULLS LAST, c.timestamp DESC NULLS LAST;

-- Insert some sample data for testing
INSERT INTO machines (name, model, series, ip_address, port, status) VALUES
('VTC-200-001', 'VTC-200', 'VTC', '192.168.1.100', 7878, 'ACTIVE'),
('VTC-300-001', 'VTC-300', 'VTC', '192.168.1.101', 7878, 'ACTIVE'),
('350MSY-001', '350MSY', 'INTEGREX', '192.168.1.102', 7878, 'ACTIVE');

-- Insert sample components for VTC-200-001
INSERT INTO components (machine_id, component_id, component_type, component_name, data_item_id) VALUES
(1, 'x', 'LINEAR', 'X-Axis', 'x_pos'),
(1, 'y', 'LINEAR', 'Y-Axis', 'y_pos'),
(1, 'z', 'LINEAR', 'Z-Axis', 'z_pos'),
(1, 'spindle', 'ROTARY', 'Main Spindle', 'spindle_rpm');

-- Insert sample components for VTC-300-001
INSERT INTO components (machine_id, component_id, component_type, component_name, data_item_id) VALUES
(2, 'x', 'LINEAR', 'X-Axis', 'x_pos'),
(2, 'y', 'LINEAR', 'Y-Axis', 'y_pos'),
(2, 'z', 'LINEAR', 'Z-Axis', 'z_pos'),
(2, 'spindle', 'ROTARY', 'Main Spindle', 'spindle_rpm');

-- Insert sample components for 350MSY-001
INSERT INTO components (machine_id, component_id, component_type, component_name, data_item_id) VALUES
(3, 'x', 'LINEAR', 'X-Axis', 'x_pos'),
(3, 'y', 'LINEAR', 'Y-Axis', 'y_pos'),
(3, 'z', 'LINEAR', 'Z-Axis', 'z_pos'),
(3, 'spindle', 'ROTARY', 'Main Spindle', 'spindle_rpm'),
(3, 'sub_spindle', 'ROTARY', 'Sub Spindle', 'sub_spindle_rpm');

-- Create initial data streams for each machine
INSERT INTO data_streams (machine_id, stream_type, instance_id, creation_time, next_sequence, first_sequence, last_sequence) VALUES
(1, 'SAMPLE', 'sample_stream_1', CURRENT_TIMESTAMP, 1, 1, 0),
(1, 'CURRENT', 'current_stream_1', CURRENT_TIMESTAMP, 1, 1, 0),
(2, 'SAMPLE', 'sample_stream_2', CURRENT_TIMESTAMP, 1, 1, 0),
(2, 'CURRENT', 'current_stream_2', CURRENT_TIMESTAMP, 1, 1, 0),
(3, 'SAMPLE', 'sample_stream_3', CURRENT_TIMESTAMP, 1, 1, 0),
(3, 'CURRENT', 'current_stream_3', CURRENT_TIMESTAMP, 1, 1, 0);

-- Grant permissions (adjust as needed for your security requirements)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tableplus;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO tableplus;

COMMIT;


