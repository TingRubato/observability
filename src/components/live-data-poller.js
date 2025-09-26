// Live Data Polling Component for Observable Framework
export class LiveDataPoller {
  constructor(endpoint, interval = 30000) {
    this.endpoint = endpoint;
    this.interval = interval;
    this.data = null;
    this.listeners = new Set();
    this.isPolling = false;
    this.pollTimer = null;
  }

  // Add event listener for data updates
  addEventListener(callback) {
    this.listeners.add(callback);
  }

  // Remove event listener
  removeEventListener(callback) {
    this.listeners.delete(callback);
  }

  // Notify all listeners of data update
  notifyListeners(data) {
    this.listeners.forEach(callback => callback(data));
  }

  // Fetch data from endpoint
  async fetchData() {
    try {
      const response = await fetch(this.endpoint);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      this.data = data;
      this.notifyListeners(data);
      return data;
    } catch (error) {
      console.error(`Error fetching data from ${this.endpoint}:`, error);
      throw error;
    }
  }

  // Start polling
  async start() {
    if (this.isPolling) return;
    
    this.isPolling = true;
    console.log(`🔄 Starting live data polling for ${this.endpoint} every ${this.interval}ms`);
    
    // Initial fetch
    try {
      await this.fetchData();
    } catch (error) {
      console.error('Initial data fetch failed:', error);
    }

    // Set up polling interval
    this.pollTimer = setInterval(async () => {
      if (document.visibilityState === 'visible') {
        try {
          await this.fetchData();
        } catch (error) {
          console.error('Polling fetch failed:', error);
        }
      }
    }, this.interval);
  }

  // Stop polling
  stop() {
    if (!this.isPolling) return;
    
    this.isPolling = false;
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
    console.log(`⏹️ Stopped live data polling for ${this.endpoint}`);
  }

  // Get current data
  getData() {
    return this.data;
  }
}

// Factory function to create pollers for different endpoints
export function createDataPoller(endpoint, interval) {
  return new LiveDataPoller(endpoint, interval);
}

// Utility function to create a reactive Observable cell that updates with polling data
export function createLiveData(endpoint, interval = 30000) {
  const poller = createDataPoller(endpoint, interval);
  
  // Create a reactive cell
  let data = null;
  const observers = new Set();
  
  // Observable-like interface
  const observable = {
    get value() { return data; },
    subscribe(callback) {
      observers.add(callback);
      poller.addEventListener((newData) => {
        data = newData;
        observers.forEach(cb => cb(newData));
      });
      return () => observers.delete(callback);
    }
  };
  
  // Start polling
  poller.start();
  
  // Clean up on page unload
  window.addEventListener('beforeunload', () => poller.stop());
  
  return observable;
}
