"""Tiny subset of FastAPI for offline testing."""

from __future__ import annotations

from dataclasses import dataclass
import inspect
from typing import Any, Callable, Dict, List, Optional

from . import status


class HTTPException(Exception):
    """Lightweight HTTP exception used by the stub router."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class Depends:
    """Declare a callable dependency."""

    def __init__(self, dependency: Callable[..., Any]) -> None:
        self.dependency = dependency


@dataclass
class Route:
    path: str
    methods: List[str]
    endpoint: Callable[..., Any]
    status_code: int

    def match(self, request_path: str) -> Optional[Dict[str, str]]:
        template_parts = [part for part in self.path.strip("/").split("/") if part]
        request_parts = [part for part in request_path.strip("/").split("/") if part]
        if len(template_parts) != len(request_parts):
            return None
        params: Dict[str, str] = {}
        for template, actual in zip(template_parts, request_parts):
            if template.startswith("{") and template.endswith("}"):
                params[template.strip("{}")] = actual
            elif template != actual:
                return None
        if not template_parts and not request_parts:
            return {}
        return params


class RouterBase:
    """Collects route definitions."""

    def __init__(self, prefix: str = "") -> None:
        self.prefix = prefix.rstrip("/")
        self.routes: List[Route] = []

    def _add_route(self, path: str, endpoint: Callable[..., Any], methods: List[str], status_code: int) -> None:
        full_path = f"{self.prefix}{path}" if self.prefix else path
        if not full_path.startswith("/"):
            full_path = f"/{full_path}" if full_path else "/"
        self.routes.append(Route(full_path or "/", methods, endpoint, status_code))

    def _register(self, path: str, methods: List[str], status_code: int) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self._add_route(path, func, methods, status_code)
            return func

        return decorator

    def get(
        self,
        path: str,
        *,
        status_code: int = status.HTTP_200_OK,
        **_: Any,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self._register(path, ["GET"], status_code)

    def post(
        self,
        path: str,
        *,
        status_code: int = status.HTTP_200_OK,
        **_: Any,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self._register(path, ["POST"], status_code)

    def put(
        self,
        path: str,
        *,
        status_code: int = status.HTTP_200_OK,
        **_: Any,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self._register(path, ["PUT"], status_code)

    def delete(
        self,
        path: str,
        *,
        status_code: int = status.HTTP_204_NO_CONTENT,
        **_: Any,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self._register(path, ["DELETE"], status_code)


class APIRouter(RouterBase):
    """Router grouping related endpoints."""

    def __init__(self, prefix: str = "", tags: Optional[List[str]] = None) -> None:
        super().__init__(prefix)
        self.tags = tags or []


class FastAPI(RouterBase):
    """Minimal application object that reuses the router implementation."""

    def __init__(self, title: str = "FastAPI Stub") -> None:
        super().__init__(prefix="")
        self.title = title

    def include_router(self, router: APIRouter) -> None:
        self.routes.extend(router.routes)

    def _resolve(self, method: str, path: str) -> tuple[Optional[Route], Dict[str, str]]:
        for route in self.routes:
            if method not in route.methods:
                continue
            params = route.match(path)
            if params is not None:
                return route, params
        return None, {}

    def handle_request(self, method: str, path: str, body: Dict[str, Any]) -> tuple[int, Any]:
        route, params = self._resolve(method, path)
        if route is None:
            return status.HTTP_404_NOT_FOUND, {"detail": "Not Found"}
        try:
            result = self._call_endpoint(route.endpoint, params, body)
        except HTTPException as exc:  # pragma: no cover - defensive
            return exc.status_code, {"detail": exc.detail}
        payload = self._serialize(result)
        if route.status_code == status.HTTP_204_NO_CONTENT:
            payload = None
        return route.status_code, payload

    def _call_endpoint(self, endpoint: Callable[..., Any], path_params: Dict[str, str], body: Dict[str, Any]) -> Any:
        signature = inspect.signature(endpoint)
        kwargs: Dict[str, Any] = {}
        hints = _get_type_hints(endpoint)
        for name, parameter in signature.parameters.items():
            if parameter.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            if parameter.default is not inspect._empty and isinstance(parameter.default, Depends):
                kwargs[name] = parameter.default.dependency()
                continue
            if name in path_params:
                kwargs[name] = path_params[name]
                continue
            annotation = hints.get(name)
            if annotation and _is_pydantic_model(annotation):
                kwargs[name] = annotation(**body)
            else:
                kwargs[name] = body
        return endpoint(**kwargs)

    def _serialize(self, result: Any) -> Any:
        if result is None:
            return None
        if _is_pydantic_instance(result):
            return result.model_dump()
        if isinstance(result, list):
            return [self._serialize(item) for item in result]
        if isinstance(result, dict):
            return {key: self._serialize(value) for key, value in result.items()}
        return result


def _is_pydantic_instance(value: Any) -> bool:
    try:
        from pydantic import BaseModel  # type: ignore
    except ModuleNotFoundError:  # pragma: no cover
        return False
    return isinstance(value, BaseModel)


def _is_pydantic_model(value: Any) -> bool:
    try:
        from pydantic import BaseModel  # type: ignore
    except ModuleNotFoundError:  # pragma: no cover
        return False
    return isinstance(value, type) and issubclass(value, BaseModel)


def _get_type_hints(func: Callable[..., Any]) -> Dict[str, Any]:
    try:
        from typing import get_type_hints

        return get_type_hints(func)
    except Exception:  # pragma: no cover - fallback
        return {}


from .testclient import TestClient  # noqa: E402

__all__ = [
    "APIRouter",
    "Depends",
    "FastAPI",
    "HTTPException",
    "TestClient",
    "status",
]
