const CACHE_NAME = "sprach-tts-v8";
const STATIC_ASSETS = [
  "/",
  "/static/css/app.css",
  "/static/js/app.js",
  "/static/js/quick_tts.js",
  "/static/js/audiobook.js",
  "/static/js/voice_studio.js",
  "/static/icons/icon.png",
  "/static/icons/icon-192.png",
  "/static/icons/icon-512.png",
  "/manifest.webmanifest"
];

// Install Event: cache app shell assets
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// Activate Event: cleanup old caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch Event: Stale-while-revalidate for static assets, Network-only for API and audio streams
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // Bypass cache for API calls, audio streaming, non-GET requests, and non-http schemes (e.g. chrome-extension)
  if (
    event.request.method !== "GET" ||
    !url.protocol.startsWith("http") ||
    url.pathname.startsWith("/api/") ||
    url.pathname.startsWith("/audio/")
  ) {
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      const fetchPromise = fetch(event.request).then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const responseClone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }
        return networkResponse;
      }).catch(() => {
        // Fallback for navigation
        if (event.request.mode === "navigate") {
          return caches.match("/");
        }
      });

      return cachedResponse || fetchPromise;
    })
  );
});
