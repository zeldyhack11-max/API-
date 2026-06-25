from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BASE_URL = "https://zeldyapiiiplakaaa.pythonanywhere.com/plaka"


def pretty_response(data, source):
    return jsonify({
        "status": "success",
        "source": source,
        "result": data
    })


@app.route("/plaka")
def plaka_router():
    plaka = request.args.get("plaka")
    adi = request.args.get("adi")
    soyadi = request.args.get("soyadi")

    try:
        # PLAKA
        if plaka:
            r = requests.get(BASE_URL, params={"plaka": plaka}, timeout=20)
            data = r.json()
            return pretty_response(data, "plaka_sorgu")

        # AD SOYAD
        elif adi and soyadi:
            r = requests.get(BASE_URL, params={"adi": adi, "soyadi": soyadi}, timeout=20)
            data = r.json()
            return pretty_response(data, "ad_soyad_sorgu")

        else:
            return jsonify({
                "status": "error",
                "message": "plaka veya adi+soyadi gir"
            })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "api hata verdi",
            "error": str(e)
        })


@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "support": "active",
        "endpoints": {
            "plaka": "/plaka?plaka=12ABC12",
            "ad_soyad": "/plaka?adi=Mehmet&soyadi=Yeter"
        }
    })


if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
