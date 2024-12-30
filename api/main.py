from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask
from waitress import serve
from app import app

# Flaskサーバーの初期化
# flask_app = Flask(__name__)
# handler = SlackRequestHandler(app)


# @flask_app.route("/", methods=["POST"])
# def slack_events():
#     return handler.handle(request)


if __name__ == "__main__":
    # 5000番ポートでリッスン
    # serve(flask_app, host="0.0.0.0", port=5000, threads=6)
    app.start(port=5000)
