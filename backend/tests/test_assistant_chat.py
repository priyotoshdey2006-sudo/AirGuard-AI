"""Direct unit tests for AI Copilot context consistency and zero-fabrication guarantees."""

import pytest
from app.schemas.assistant import ChatRequest, ContextData
from app.services.ai_engine import ai_engine


def test_copilot_generates_reply_matching_dashboard_aqi():
    """Verify that copilot uses the exact AQI and category supplied from the Dashboard."""
    context = ContextData(
        location="Delhi NCR",
        current_aqi=154,
        category="Unhealthy",
        dominant_pollutant="pm2_5",
        sensitivity_profile="ASTHMATIC",
        is_live_data_available=True,
    )

    # Test mask query
    mask_reply = ai_engine.expert.generate_chat_reply("Should I wear an N95 mask outside?", context)
    assert mask_reply.context_used.current_aqi == 154
    assert mask_reply.context_used.category == "Unhealthy"
    assert "154" in mask_reply.reply
    assert "Unhealthy" in mask_reply.reply
    assert "N95 or FFP2 respirator" in mask_reply.reply

    # Test jogging/exercise query
    jog_reply = ai_engine.expert.generate_chat_reply("Is it safe for an outdoor jog?", context)
    assert "not recommended" in jog_reply.reply.lower()
    assert "154" in jog_reply.reply

    # Test window ventilation query
    window_reply = ai_engine.expert.generate_chat_reply("When can I open my windows?", context)
    assert "closed" in window_reply.reply.lower()
    assert "154" in window_reply.reply


def test_copilot_never_fabricates_aqi_when_telemetry_unavailable():
    """Verify that when live telemetry is unavailable, copilot refuses to fabricate 75 or any number."""
    context = ContextData(
        location="Unknown Station",
        current_aqi=None,
        category="Unavailable",
        dominant_pollutant="unknown",
        sensitivity_profile="NORMAL",
        is_live_data_available=False,
    )

    reply = ai_engine.expert.generate_chat_reply("What is the air quality right now?", context)
    assert reply.context_used.current_aqi is None
    assert reply.context_used.is_live_data_available is False
    assert "unavailable" in reply.reply.lower()
    assert "75" not in reply.reply
    assert "Zero-Fabrication Policy" in reply.reply


def test_copilot_moderate_aqi_behavior():
    """Verify that for moderate AQI (e.g. 75), it gives appropriate moderate guidance."""
    context = ContextData(
        location="Mumbai Coastal",
        current_aqi=75,
        category="Moderate",
        dominant_pollutant="pm10",
        sensitivity_profile="NORMAL",
        is_live_data_available=True,
    )

    reply = ai_engine.expert.generate_chat_reply("Should I wear a mask?", context)
    assert "75" in reply.reply
    assert "Moderate" in reply.reply
    assert "does not strictly necessitate an N95 mask" in reply.reply
