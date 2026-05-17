import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings


def setup_logging() -> None:
    """
    Configures loguru for the entire application.
    Call this once at startup in main.py — all modules
    that import logger from loguru will automatically
    use this configuration.
    """

    # Remove the default loguru handler
    logger.remove()

    # Console handler — human-readable during development
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.log_level,
        colorize=True,
    )

    # File handler — structured logs for debugging and audit trails
    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        settings.log_file,
        format=log_format,
        level=settings.log_level,
        rotation="10 MB",   # new file after 10MB
        retention="30 days",
        compression="zip",
        colorize=False,
    )

    logger.info(f"Logging initialised | env={settings.app_env} | level={settings.log_level}")


# Re-export logger so other modules import from here
__all__ = ["logger", "setup_logging"]