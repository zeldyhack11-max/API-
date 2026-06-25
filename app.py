from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BASE_URL = "https://zeldyapiiiplakaaa.pythonanywhere.com/plaka"

@app.route("/plaka")
def plaka_router():
    plaka = request.args.get("plaka")
    adi = request.args.get("adi")
    soyadi = request.args.get("soyadi")

    try:
        # 1) PLAKA SORGUSU
        if plaka:
            r = requests.get(BASE_URL, params={"plaka": plaka}, timeout=20)
            return jsonify(r.json())

        # 2) AD SOYAD SORGUSU
        elif adi and soyadi:
            r = requests.get(BASE_URL, params={"adi": adi, "soyadi": soyadi}, timeout=20)
            return jsonify(r.json())

        else:
            return jsonify({
                "hata": "plaka veya ad-soyad gir"
            })

    except Exception as e:
        return jsonify({
            "hata": "api hatasi",
            "detay": str(e)
        })


@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "endpoints": {
            "plaka": "/plaka?plaka=12ABC12",
            "ad_soyad": "/plaka?adi=Mehmet&soyadi=Yeter"
        }
    })


if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
