import os
import logging
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        # Database
        self.database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:1006@localhost:5432/rapid-ai")

        # Security
        self.secret_key = os.getenv("SECRET_KEY", "your-super-secret-key-here-change-in-production")
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

        # Server
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        self.debug = os.getenv("DEBUG", "True").lower() == "true"

        # CORS - simple string parsing
        origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
        self.allowed_origins = [origin.strip() for origin in origins_str.split(",") if origin.strip()]

        # Flux API Configuration
        self.flux_api_key = os.getenv("FLUX_API_KEY", "")
        # Based on the documentation, this is the correct MCP server endpoint
        self.flux_base_url = os.getenv("FLUX_BASE_URL", "https://server.smithery.ai/@falahgs/flux-imagegen-mcp-server/mcp")

# Create settings instance
settings = Settings()

# Validate critical settings
if not settings.secret_key or settings.secret_key == "your-super-secret-key-here-change-in-production":
    raise ValueError("SECRET_KEY must be set in environment variables")

if not settings.database_url:
    raise ValueError("DATABASE_URL must be set in environment variables")

if not settings.flux_api_key:
    logging.warning("FLUX_API_KEY not set - image generation will use fallback methods")
else:
    logging.info(f"Flux API configured with base URL: {settings.flux_base_url}")
