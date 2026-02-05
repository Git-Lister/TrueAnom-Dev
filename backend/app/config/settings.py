from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "True Anomaly"
    postgres_dsn: str = "postgresql://true_anomaly:true_anomaly@localhost:5432/true_anomaly"
    opensearch_url: str = "http://localhost:9200"
    neo4j_url: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    class Config:
        env_file = ".env"

settings = Settings()
