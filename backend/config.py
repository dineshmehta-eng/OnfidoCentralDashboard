from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Onfido_SQL_Dashboard"
    APP_ENV: str = "production"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    SQL_SERVER: str
    SQL_DATABASE: str
    SQL_USERNAME: str
    SQL_PASSWORD: str
    SQL_DRIVER: str = "ODBC Driver 17 for SQL Server"
    SQL_TRUST_CERTIFICATE: str = "yes"
    SQL_ENCRYPT: str = "no"
    SQL_TRUSTED_CONNECTION: str = "no"
    SQL_POOL_SIZE: int = 20
    SQL_MAX_OVERFLOW: int = 40
    SQL_POOL_RECYCLE: int = 1800
    API_CORS_ORIGINS: str = "http://localhost:8000,http://127.0.0.1:8000"
    CACHE_TTL_SECONDS: int = 300
    LOG_LEVEL: str = "INFO"
    GOOGLE_SERVICE_ACCOUNT_FILE: str = "config/service_account.json"
    ETL_SYNC_INTERVAL_MINUTES: int = 60

    MOCK_DB: str = "false"
    API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
