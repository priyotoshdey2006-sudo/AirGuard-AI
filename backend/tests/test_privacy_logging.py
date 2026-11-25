"""Dedicated tests for structured privacy logging and sensitive health data redaction.

Verifies:
1. Redaction of `sensitivity_profile` in JSON, key-value, and unquoted formats.
2. Redaction of `optional_sensitivity_profile`.
3. Redaction of `password` in login and registration payloads.
4. Non-sensitive log messages pass through unchanged.
5. End-to-end logger output scrubbing via PrivacyFilter.
"""

import io
import logging
import pytest
from app.core.logging import PrivacyFilter, setup_logging


def test_privacy_filter_direct_redactions():
    """Verify that PrivacyFilter.filter() redacts sensitivity profile and passwords."""
    filter_instance = PrivacyFilter()

    # Test cases: (input_message, expected_substring, forbidden_substring)
    test_cases = [
        # JSON formatted sensitivity profile
        (
            'Received payload: {"sensitivity_profile": "ASTHMATIC", "city": "Delhi"}',
            '"sensitivity_profile": "[REDACTED_HEALTH]"',
            'ASTHMATIC',
        ),
        # Unquoted / key-value format
        (
            'User settings updated: sensitivity_profile=ELDERLY, notify=True',
            'sensitivity_profile=[REDACTED_HEALTH]',
            'ELDERLY',
        ),
        # Optional sensitivity profile
        (
            'Query params: optional_sensitivity_profile: "PREGNANT"',
            'optional_sensitivity_profile: "[REDACTED_HEALTH]"',
            'PREGNANT',
        ),
        # JSON password in auth request
        (
            'Auth attempt: {"username": "user1", "password": "supersecretpassword123"}',
            '"password": "[REDACTED_SECRET]"',
            'supersecretpassword123',
        ),
        # Key-value password
        (
            'Connection param: password=my_db_pass_xyz',
            'password=[REDACTED_SECRET]',
            'my_db_pass_xyz',
        ),
    ]

    for raw_msg, expected_sub, forbidden_sub in test_cases:
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname=__file__,
            lineno=42,
            msg=raw_msg,
            args=(),
            exc_info=None,
        )
        filter_instance.filter(record)
        assert expected_sub in record.msg, f"Expected '{expected_sub}' in '{record.msg}'"
        assert forbidden_sub not in record.msg, f"Forbidden '{forbidden_sub}' leaked in '{record.msg}'"


def test_privacy_filter_preserves_standard_messages():
    """Verify that normal environmental and application log messages are unchanged."""
    filter_instance = PrivacyFilter()
    normal_msg = "Serving AQI for grid (28.6139, 77.2090) from cache. PM2.5 = 90.0 ug/m3."
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg=normal_msg,
        args=(),
        exc_info=None,
    )
    filter_instance.filter(record)
    assert record.msg == normal_msg


def test_privacy_logger_integration_stream():
    """Verify that an attached StreamHandler emits only redacted strings."""
    stream = io.StringIO()
    test_logger = logging.getLogger("test_privacy_stream")
    test_logger.setLevel(logging.INFO)
    test_logger.handlers.clear()

    handler = logging.StreamHandler(stream)
    handler.addFilter(PrivacyFilter())
    test_logger.addHandler(handler)

    test_logger.info("Registering user with password='plain_secret_text' and sensitivity_profile='CARDIOVASCULAR'")

    output = stream.getvalue()
    assert "[REDACTED_SECRET]" in output
    assert "[REDACTED_HEALTH]" in output
    assert "plain_secret_text" not in output
    assert "CARDIOVASCULAR" not in output
