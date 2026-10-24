"""API routes. Owner: Rodrigo. Contract: docs/contract.md"""
from flask import Blueprint, jsonify

api = Blueprint("api", __name__)

# NM-8:  GET  /personas
# NM-8:  GET  /customers/<id>/dashboard
# NM-12: POST /customers/<id>/recommendations  → engine.recommend.recommend() + services.llm.explain_all()
