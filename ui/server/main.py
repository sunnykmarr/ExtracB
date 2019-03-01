from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/")
def hello():
    msg = request.args.get("msg")
    return "Received: " + msg


if __name__ == "__main__":
    app.run()
