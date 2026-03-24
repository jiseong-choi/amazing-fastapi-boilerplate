"""Config of application"""
from .openapi import OpenAPISettings
from .settings import settings

# 기존 호환성을 위해 유지
openapi_config = OpenAPISettings.generate()

# 새로운 통합 설정 내보내기
__all__ = ["settings", "openapi_config"]
