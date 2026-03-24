"""라우터 자동 등록 모듈"""
import importlib
import inspect
import pkgutil
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, APIRouter
from loguru import logger


class RouterConfig:
    """라우터 설정 클래스"""
    def __init__(
        self,
        router: APIRouter,
        prefix: str = "",
        tags: Optional[List[str]] = None,
        dependencies: Optional[List[Any]] = None,
        responses: Optional[Dict[int, Any]] = None,
    ):
        self.router = router
        self.prefix = prefix
        self.tags = tags or []
        self.dependencies = dependencies or []
        self.responses = responses or {}


def auto_discover_routers(
    package_path: str = "app.routers",
    base_prefix: str = "",
) -> List[RouterConfig]:
    """
    패키지 내 모든 라우터를 자동으로 발견합니다.
    
    Args:
        package_path: 라우터 패키지 경로
        base_prefix: 기본 접두사
        
    Returns:
        발견된 라우터 설정 리스트
    """
    routers = []
    
    try:
        # 패키지 가져오기
        package = importlib.import_module(package_path)
        package_dir = getattr(package, "__path__", None)
        
        if not package_dir:
            logger.warning(f"패키지 경로를 찾을 수 없습니다: {package_path}")
            return routers
        
        # 패키지 내 모듈 순회
        for _, module_name, is_pkg in pkgutil.iter_modules(package_dir):
            if module_name == "__init__":
                continue
                
            try:
                # 모듈 가져오기
                module = importlib.import_module(f"{package_path}.{module_name}")
                
                # 모듈 내 APIRouter 인스턴스 찾기
                for name, obj in inspect.getmembers(module):
                    if isinstance(obj, APIRouter):
                        # 라우터 설정 구성
                        # 기본 prefix: 라우터에 설정된 prefix가 있으면 사용, 없으면 모듈명 사용
                        router_prefix = getattr(obj, "prefix", "")
                        if not router_prefix:
                            router_prefix = f"/{module_name}"
                        
                        # 모듈별 prefix 매핑 (필요시 추가)
                        module_prefix_map = {
                            "agent": "/v1/agent",
                            "hello": "",
                        }
                        if module_name in module_prefix_map:
                            router_prefix = module_prefix_map[module_name]
                        
                        # 최종 prefix: base_prefix + router_prefix
                        final_prefix = f"{base_prefix}{router_prefix}"
                        
                        tags = getattr(obj, "tags", [module_name])
                        
                        # 디버깅 정보
                        logger.debug(f"모듈: {module_name}, 라우터 이름: {name}, prefix: {final_prefix}, tags: {tags}")
                        
                        router_config = RouterConfig(
                            router=obj,
                            prefix=final_prefix,
                            tags=tags,
                        )
                        routers.append(router_config)
                        logger.debug(f"라우터 발견: {module_name} -> {final_prefix}")
                        
            except Exception as e:
                logger.error(f"모듈 로드 실패: {module_name}, 오류: {e}")
                
    except Exception as e:
        logger.error(f"라우터 자동 발견 실패: {e}")
    
    logger.info(f"총 {len(routers)}개의 라우터를 발견했습니다.")
    return routers


def setup_routers(app: FastAPI) -> None:
    """
    앱에 라우터를 자동으로 등록합니다.
    
    Args:
        app: FastAPI 앱 인스턴스
    """
    # 기존 라우터 등록 (app.core.routers)
    try:
        from app.core import routers as core_routers
        from inspect import getmembers
        from app.core.utils.api import TypedAPIRouter
        
        routers_list = [o[1] for o in getmembers(core_routers) if isinstance(o[1], TypedAPIRouter)]
        
        for router_config in routers_list:
            app.include_router(
                router_config.router,
                prefix=router_config.prefix,
                tags=router_config.tags,
                responses=router_config.responses,
            )
            logger.debug(f"기존 라우터 등록: {router_config.prefix}")
            
    except ImportError as e:
        logger.warning(f"기존 라우터를 로드할 수 없습니다: {e}")
    
    # 새로운 라우터 자동 발견 및 등록
    discovered_routers = auto_discover_routers()
    
    for router_config in discovered_routers:
        app.include_router(
            router_config.router,
            prefix=router_config.prefix,
            tags=router_config.tags,
            dependencies=router_config.dependencies,
            responses=router_config.responses,
        )
        logger.debug(f"새 라우터 등록: {router_config.prefix}")
    
    logger.success(f"라우터 설정이 완료되었습니다. 총 {len(discovered_routers)}개의 새 라우터 등록됨.")