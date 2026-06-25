from flask import Flask, request, Response
import requests
import json

app = Flask(__name__)

BASE_URL = "https://zeldyapiiiplakaaa.pythonanywhere.com/plaka"


def pretty(data):
    return Response(
        json.dumps(data, indent=4, ensure_ascii=False),
        mimetype="application/json"
    )


@app.route("/plaka")
def plaka():
    plaka = request.args.get("plaka")
    adi = request.args.get("adi")
    soyadi = request.args.get("soyadi")

    try:
        if plaka:
            r = requests.get(BASE_URL, params={"plaka": plaka}, timeout=20)
            return pretty(r.json())

        elif adi and soyadi:
            r = requests.get(BASE_URL, params={"adi": adi, "soyadi": soyadi}, timeout=20)
            return pretty(r.json())

        return pretty({"hata": "eksik parametre"})

    except Exception as e:
        return pretty({"hata": str(e)})


@app.route("/")
def home():
    return pretty({
        "status": "online",
        "endpoints": {
            "plaka": "/plaka?plaka=12ABC12",
            "ad_soyad": "/plaka?adi=Mehmet&soyadi=Yeter"
        }
    })


if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
