const CACHE_NAME = 'expense-calendar-cache-v1';
// オフライン時に表示したいファイルを指定
const urlsToCache = [
  '/',
  '/carcheck.html',
  '/favicon2.png',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png'
];

// Service Workerのインストール時にキャッシュを作成
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache opened');
        return cache.addAll(urlsToCache);
      })
  );
});

// リクエストがあった際にキャッシュから返す
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // キャッシュにあればそれを返し、なければネットワークから取得
        return response || fetch(event.request);
      })
  );
});
