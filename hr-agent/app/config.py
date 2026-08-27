import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    """Application settings with environment variable defaults."""
    # GCP & GenAI Settings
    project_id: str = os.getenv("GOOGLE_CLOUD_PROJECT", "project-elevate")
    location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    model_name: str = os.getenv("MODEL_NAME", "gemini-3.6-flash")
    vertex_base_url: str = os.getenv("VERTEX_BASE_URL", "https://aiplatform.googleapis.com")

    # SaaS MCP & REST Server Settings
    mcp_token: str = (
        os.getenv("MCP_TOKEN")
        or os.getenv("MOCK_SAAS_API_TOKEN")
        or os.getenv("X_MCP_TOKEN")
        or "mcp_olHWiuDEGP_tw5X_DU3eidmL9aS1pFJLDgFMySwmOqs"
    )
    base_url: str = os.getenv(
        "MOCK_SAAS_BASE_URL",
        "https://mock-saas.aishprabhat.demo.altostrat.com"
    ).rstrip("/")

    # Sub-application MCP URLs
    workweek_mcp_url: str = os.getenv(
        "WORKWEEK_MCP_URL",
        f"{os.getenv('MOCK_SAAS_BASE_URL', 'https://mock-saas.aishprabhat.demo.altostrat.com').rstrip('/')}/work-week/mcp/"
    )
    service_mcp_url: str = os.getenv(
        "SERVICEIMMEDIATELY_MCP_URL",
        f"{os.getenv('MOCK_SAAS_BASE_URL', 'https://mock-saas.aishprabhat.demo.altostrat.com').rstrip('/')}/service-immediately/mcp/"
    )

    # Timeouts & Retries
    client_timeout_seconds: float = float(os.getenv("CLIENT_TIMEOUT_SECONDS", "4.0"))
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))

    # Default Context
    default_employee_id: str = os.getenv("DEFAULT_EMPLOYEE_ID", "WW-10928")
    default_user_email: str = os.getenv("DEFAULT_USER_EMAIL", "alex.rivera@example.com")


settings = Settings()
