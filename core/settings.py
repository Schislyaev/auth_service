from datetime import timedelta

from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str = 'postgresql://test:test@localhost/test'
    redis_url: str = 'redis'
    redis_port: str = '6379'
    flask_app_key: str = ''
    salt: str = ' '
    jwt_key: str = ''
    permission_cache_seconds: int = 2
    access_expires = timedelta(hours=1)
    refresh_expires = timedelta(hours=24)
    grpc_port: int = 50051
    grpc_max_workers: int = 10
    google_client_id = '723896286141-otgk2lus2ba7unjk5upre00evpv2sak9.apps.googleusercontent.com'
    google_client_secret = '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'
    tracer: bool = True

    class Config:
        env_file = '.env.example'
        env_file_encoding = 'utf-8'
        case_sensitive = False


settings = Settings()
