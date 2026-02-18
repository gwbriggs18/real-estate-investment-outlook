"""
Investment Outlook – Flask app.
Serves the frontend static files and mounts /api/stock routes.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, send_from_directory

from backend.routes.stock import stock_bp
from backend.routes.real_estate import real_estate_bp
from backend.routes.compare import compare_bp

app = Flask(__name__, static_folder="frontend", static_url_path="")
app.register_blueprint(stock_bp)
app.register_blueprint(real_estate_bp)
app.register_blueprint(compare_bp)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/health")
def health():
    return {"status": "ok", "service": "investment-outlook"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
