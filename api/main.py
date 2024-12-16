from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask
from app import app

# Flaskサーバーの初期化
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/", methods=["POST"])
def slack_events():
    return handler.handle(request)


if __name__ == "__main__":
    # 5000番ポートでリッスン
    flask_app.run(port=5000)
