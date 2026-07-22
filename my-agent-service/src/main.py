import os
import uvicorn
from src.config.settings import settings


def main() -> None:
    """
    Main ASGI entry point. Parses CLI env parameters and runs Uvicorn.
    Defers logging configuration to app lifecycle setups by passing log_config=None.
    """
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")

    # Run Uvicorn loop
    uvicorn.run(
        "src.app:app",
        host=host,
        port=port,
        reload=(settings.ENVIRONMENT == "development"),
        workers=1,
        log_config=None,  # Defer logging control to settings.py / logging_cfg.py
    )


if __name__ == "__main__":
    main()
