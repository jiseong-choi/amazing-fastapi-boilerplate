"""OpenAPI-schema"""
import os
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from app.config.base import BaseSettings

OPENAPI_API_NAME = os.environ.get("OPENAPI_API_NAME", "HumanBeing")
OPENAPI_API_VERSION = os.environ.get("OPENAPI_API_VERSION", "0.0.1 beta")
OPENAPI_API_DESCRIPTION = os.environ.get("OPENAPI_API_DESCRIPTION", "HumanBeing API")

print(OPENAPI_API_NAME, OPENAPI_API_VERSION, OPENAPI_API_DESCRIPTION)


class OpenAPISettings(BaseSettings):
    name: str
    version: str
    description: str

    @classmethod
    def generate(cls):
        return OpenAPISettings(
            name=OPENAPI_API_NAME,
            version=OPENAPI_API_VERSION,
            description=OPENAPI_API_DESCRIPTION,
        )
