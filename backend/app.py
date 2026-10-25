"""Flask app factory. Owner: Rodrigo."""
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

load_dotenv()


def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:5173"])

    from routes import api
    from services.customer_profile import CustomerNotFound

    app.register_blueprint(api, url_prefix="/api")

    # Open the LLM connection in the background so the first request is fast (NM-13, Jose)
    from services.llm import warm_up
    warm_up()

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    @app.errorhandler(CustomerNotFound)
    def handle_customer_not_found(error):
        return jsonify(error="customer not found"), 404

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify(error=error.description), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unexpected error")
        return jsonify(error="Something went wrong on our side"), 500

    return app


app = create_app()