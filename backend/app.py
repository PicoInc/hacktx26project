"""Flask app factory. Owner: Rodrigo."""
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

load_dotenv()


def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:5173"])

    from routes import api
    app.register_blueprint(api, url_prefix="/api")

    # Open the LLM connection in the background so the first request is fast (NM-13, Jose)
    from services.llm import warm_up
    warm_up()

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    return app


app = create_app()
