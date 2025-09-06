// Tyler Training Hub Service Worker
const CACHE_NAME = 'tyler-training-v1.0.0';
const STATIC_CACHE = 'tyler-static-v1.0.0';
const DYNAMIC_CACHE = 'tyler-dynamic-v1.0.0';

// Resources to cache immediately
const STATIC_ASSETS = [
  '/',
  '/static/mobile_app_enhancements.css',
  '/static/manifest.json',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css',
  'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js'
];

// API endpoints to cache with strategies
const API_CACHE_PATTERNS = [
  '/api/weather',
  '/api/real-time-stats',
  '/api/rankings',
  '/api/competitor-analysis'
];

// Install event - cache static assets
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
      .catch(err => console.error('Service Worker: Cache failed', err))
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log('Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache with fallback strategies
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Handle different request types with appropriate strategies
  if (request.method === 'GET') {
    event.respondWith(handleGetRequest(request, url));
  }
});

async function handleGetRequest(request, url) {
  try {
    // Static assets - Cache First
    if (STATIC_ASSETS.some(asset => url.pathname.includes(asset))) {
      return await cacheFirst(request);
    }
    
    // API endpoints - Network First with cache fallback
    if (API_CACHE_PATTERNS.some(pattern => url.pathname.includes(pattern))) {
      return await networkFirst(request);
    }
    
    // Weather API - Stale While Revalidate
    if (url.pathname.includes('/api/weather')) {
      return await staleWhileRevalidate(request);
    }
    
    // HTML pages - Network First
    if (request.headers.get('accept').includes('text/html')) {
      return await networkFirst(request);
    }
    
    // Everything else - Network First
    return await networkFirst(request);
    
  } catch (error) {
    console.error('Service Worker: Fetch failed', error);
    return offlineResponse(request);
  }
}

// Cache Strategies
async function cacheFirst(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  const networkResponse = await fetch(request);
  await cacheResponse(request, networkResponse.clone(), STATIC_CACHE);
  return networkResponse;
}

async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse.status === 200) {
      await cacheResponse(request, networkResponse.clone(), DYNAMIC_CACHE);
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Service Worker: Network failed, trying cache');
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    throw error;
  }
}

async function staleWhileRevalidate(request) {
  const cachedResponse = await caches.match(request);
  
  // Fetch fresh data in background
  const networkResponsePromise = fetch(request).then(response => {
    if (response.status === 200) {
      cacheResponse(request, response.clone(), DYNAMIC_CACHE);
    }
    return response;
  });
  
  // Return cached version immediately if available
  if (cachedResponse) {
    return cachedResponse;
  }
  
  // Wait for network if no cache
  return await networkResponsePromise;
}

async function cacheResponse(request, response, cacheName) {
  const cache = await caches.open(cacheName);
  await cache.put(request, response);
}

function offlineResponse(request) {
  // Return appropriate offline responses
  if (request.headers.get('accept').includes('text/html')) {
    return new Response(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Tyler Training - Offline</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
            color: white;
            text-align: center;
            padding: 20px;
          }
          .icon { font-size: 4rem; margin-bottom: 20px; }
          h1 { margin: 0 0 10px 0; }
          p { opacity: 0.9; margin: 0 0 20px 0; }
          .btn {
            background: white;
            color: #007bff;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
          }
        </style>
      </head>
      <body>
        <div class="icon">🏃‍♂️</div>
        <h1>You're Offline</h1>
        <p>Tyler Training is currently offline. Check your connection and try again.</p>
        <button class="btn" onclick="window.location.reload()">Try Again</button>
        <script>
          // Auto-retry when online
          window.addEventListener('online', () => {
            window.location.reload();
          });
        </script>
      </body>
      </html>
    `, {
      headers: { 'Content-Type': 'text/html' }
    });
  }
  
  if (request.url.includes('/api/')) {
    return new Response(JSON.stringify({
      error: 'Offline',
      message: 'No internet connection',
      offline: true
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  return new Response('Offline', { status: 503 });
}

// Background sync for workout logging
self.addEventListener('sync', event => {
  if (event.tag === 'workout-sync') {
    event.waitUntil(syncWorkouts());
  }
});

async function syncWorkouts() {
  try {
    // Sync any pending workout data when back online
    const pendingData = await getStoredData('pending-workouts');
    if (pendingData && pendingData.length > 0) {
      for (const workout of pendingData) {
        await fetch('/api/sync-workout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(workout)
        });
      }
      await clearStoredData('pending-workouts');
      console.log('Service Worker: Workouts synced successfully');
    }
  } catch (error) {
    console.error('Service Worker: Sync failed', error);
  }
}

// IndexedDB helpers for offline data
async function getStoredData(key) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('TylerTraining', 1);
    request.onsuccess = () => {
      const db = request.result;
      const transaction = db.transaction(['offline'], 'readonly');
      const store = transaction.objectStore('offline');
      const getRequest = store.get(key);
      getRequest.onsuccess = () => resolve(getRequest.result?.data);
      getRequest.onerror = () => reject(getRequest.error);
    };
  });
}

async function clearStoredData(key) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('TylerTraining', 1);
    request.onsuccess = () => {
      const db = request.result;
      const transaction = db.transaction(['offline'], 'readwrite');
      const store = transaction.objectStore('offline');
      const deleteRequest = store.delete(key);
      deleteRequest.onsuccess = () => resolve();
      deleteRequest.onerror = () => reject(deleteRequest.error);
    };
  });
}

// Push notification handling
self.addEventListener('push', event => {
  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.body || 'New training update available!',
      icon: '/static/icon-192.png',
      badge: '/static/icon-96.png',
      data: data.url || '/',
      actions: [
        { action: 'view', title: 'View' },
        { action: 'dismiss', title: 'Dismiss' }
      ],
      requireInteraction: true,
      tag: 'tyler-training'
    };
    
    event.waitUntil(
      self.registration.showNotification(data.title || 'Tyler Training', options)
    );
  }
});

// Notification click handling
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow(event.notification.data || '/')
    );
  }
});

console.log('Service Worker: Tyler Training Hub SW loaded successfully');