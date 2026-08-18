/* Caching is intentionally disabled while Blip is under active development —
   every load fetches fresh from the network, no exceptions. This trades away
   offline support for now, in exchange for updates always showing up
   immediately without needing a manual "clear site data" reset every time.
   Once the app is more stable, this can go back to a real caching strategy. */

self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// No fetch handler at all — requests pass straight through to the network,
// exactly as if this service worker didn't exist for caching purposes.
