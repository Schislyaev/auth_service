from pydantic import BaseSettings


class TestSettings(BaseSettings):
    service_url: str = '127.0.0.1'
    service_port: int = 5000

    class Config:
        env_file = '../.env.test'
        env_file_encoding = 'utf-8'


test_settings = TestSettings()
