from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    service_host: str = "0.0.0.0"
    service_port: int = 8095

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    service_auth_token: str = "dev-service-token"

    llm_provider: str = "stub"
    llm_model: str = "bluecore-ai-v1"
    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = ""

    default_threat_policy_id: str = "default-officer-safety"
    audit_retention_days: int = 2555
    prompts_dir: str = "/app/prompts"
    cors_origins: str = "http://localhost:3000,http://localhost:3001,http://localhost:3002"


settings = Settings()
