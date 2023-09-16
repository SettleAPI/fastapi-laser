from google.auth.transport import requests
from google.oauth2 import id_token

from app import app_config


def get_id_token(audience: str) -> str:
    if app_config.environment in ("local", "test"):
        return ""

    return id_token.fetch_id_token(requests.Request(), audience)
