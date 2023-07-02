from dataclasses import dataclass, field

import httpx

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


@dataclass
class OIDCConfig:
    userinfo_endpoint: str
    required_groups: list[str] = field(default_factory=list)
    exclude_paths: list[str] = field(default_factory=list)
    exclude_paths_prefix: list[str] = field(default_factory=list)


def add_oidc_middleware(app: FastAPI, config: OIDCConfig):
    @app.middleware("http")
    async def verify_oidc_auth(request: Request, call_next):
        # If path is in exclude_paths, skip OIDC verification
        if request.url.path in config.exclude_paths:
            return await call_next(request)

        # If path starts with any of the exclude_paths_prefix,
        # skip OIDC verification
        for prefix in config.exclude_paths_prefix:
            if request.url.path.startswith(prefix):
                return await call_next(request)

        # First verify that there is an Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "No Authorization header",
                },
            )

        # Then verify that it is a Bearer token
        auth_split = auth_header.split(" ")
        if len(auth_split) != 2:
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Invalid Authorization value",
                },
            )

        auth_type = auth_split[0]
        auth_token = auth_split[1]
        if not auth_type or auth_type.lower() != "bearer":
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Not a bearer token",
                },
            )

        # Then verify that the token is valid
        async with httpx.AsyncClient() as client:
            res = await client.get(
                config.userinfo_endpoint,
                headers={
                    "Authorization": f"Bearer {auth_token}",
                },
            )
            if res.status_code != 200:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid token"},
                )

            userinfo = res.json()
            if not userinfo:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid token"},
                )

            if config.required_groups:
                if not userinfo.get("groups"):
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "User does not have any groups"},
                    )

                required_groups = set(config.required_groups)
                has_group = any(
                    group in userinfo["groups"] for group in required_groups
                )
                if not has_group:
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "User not authorized"},
                    )

            request.state.userinfo = userinfo

        return await call_next(request)
