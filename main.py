from flask import Flask, request, Response
import requests
import json

app = Flask(__name__)

BASE_URL = "https://zeldyapiiiplakaaa.pythonanywhere.com/plaka"


def pretty_json(data):
    return Response(
        json.dumps(data, indent=4, ensure_ascii=False),
        mimetype="application/json"
    )


@app.route("/plaka")
def plaka_router():
    plaka = request.args.get("plaka")
    adi = request.args.get("adi")
    soyadi = request.args.get("soyadi")

    try:
        # PLAKA SORGUSU
        if plaka:
            r = requests.get(BASE_URL, params={"plaka": plaka}, timeout=20)
            data = r.json()
            return pretty_json({
                "status": "success",
                "type": "plaka_sorgu",
                "data": data
            })

        # AD SOYAD SORGUSU
        elif adi and soyadi:
            r = requests.get(BASE_URL, params={"adi": adi, "soyadi": soyadi}, timeout=20)
            data = r.json()
            return pretty_json({
                "status": "success",
                "type": "ad_soyad_sorgu",
                "data": data
            })

        return pretty_json({
            "status": "error",
            "message": "plaka veya adi+soyadi gir"
        })

    except Exception as e:
        return pretty_json({
            "status": "error",
            "message": "api hata verdi",
            "error": str(e)
        })


@app.route("/")
def home():
    return pretty_json({
        "status": "online",
        "support": "active",
        "endpoints": {
            "plaka": "/plaka?plaka=12ABC12",
            "ad_soyad": "/plaka?adi=Mehmet&soyadi=Yeter"
        }
    })


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
