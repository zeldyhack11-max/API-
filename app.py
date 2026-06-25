from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BASE_URL = "https://zeldyapiiiplakaaa.pythonanywhere.com/plaka"


def api_response(success, status, message, data=None, error=None, req_type=None):
    return jsonify({
        "success": success,
        "status": status,
        "message": message,
        "data": {
            "result": data,
            "type": req_type
        } if data else None,
        "error": error,
        "meta": {
            "source": "zeldy-api",
            "version": "1.0"
        }
    })


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

            return api_response(
                True,
                200,
                "ok",
                data,
                None,
                "plaka_sorgu"
            )

        # AD SOYAD SORGUSU
        elif adi and soyadi:
            r = requests.get(BASE_URL, params={"adi": adi, "soyadi": soyadi}, timeout=20)
            data = r.json()

            return api_response(
                True,
                200,
                "ok",
                data,
                None,
                "ad_soyad_sorgu"
            )

        return api_response(
            False,
            400,
            "plaka veya ad-soyad girilmedi"
        )

    except Exception as e:
        return api_response(
            False,
            500,
            "external api error",
            None,
            str(e)
        )


@app.route("/")
def home():
    return api_response(
        True,
        200,
        "online",
        {
            "plaka": "/plaka?plaka=12ABC12",
            "ad_soyad": "/plaka?adi=Mehmet&soyadi=Yeter"
        },
        None,
        "home"
    )


if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
