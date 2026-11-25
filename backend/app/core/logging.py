"""Structured logging configuration for AirGuard AI with health privacy redaction."""

import logging
import re
import sys


class PrivacyFilter(logging.Filter):
    """Filter that scrubs personal health preferences and sensitive message payloads from log records."""

    REDACTION_PATTERNS = [
        # JSON and key-value formats for sensitivity profiles
        (re.compile(r'(["\']?(?:optional_)?sensitivity_profile["\']?\s*[:=]\s*["\']?)([^"\',}\s]+)(["\']?)', re.IGNORECASE), r'\1[REDACTED_HEALTH]\3'),
        # JSON and key-value formats for passwords
        (re.compile(r'(["\']?password["\']?\s*[:=]\s*["\']?)([^"\',}\s]+)(["\']?)', re.IGNORECASE), r'\1[REDACTED_SECRET]\3'),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern, repl in self.REDACTION_PATTERNS:
                record.msg = pattern.sub(repl, record.msg)
        return True


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("airguard")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        handler.addFilter(PrivacyFilter())
        logger.addHandler(handler)
    return logger


logger = setup_logging()
