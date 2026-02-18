const CACHE_NAME = 'alphascope-v1';
const ASSETS = [
  './alphascope.html',
  './manifest.json'
];

// Install — cache core assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate — clean old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

// Fetch — network-first with cache fallback
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Only handle same-origin requests for cached assets
  if (url.origin === self.location.origin) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Cache successful responses for our assets
          if (response.ok && ASSETS.some(a => url.pathname.endsWith(a.replace('./', '')))) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          }
          return response;
        })
        .catch(() => {
          // Offline — serve from cache
          return caches.match(event.request).then(cached => {
            if (cached) return cached;
            // Fallback to alphascope.html for navigation requests
            if (event.request.mode === 'navigate') {
              return caches.match('./alphascope.html');
            }
            return new Response('Offline', { status: 503, statusText: 'Offline' });
          });
        })
    );
  }
});
