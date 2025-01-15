from flask import Flask
from .push_route import push_bp


def register_routes(app: Flask):
    app.register_blueprint(push_bp)
