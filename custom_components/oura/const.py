"""Constants for the Oura Ring integration."""
from datetime import timedelta
from typing import Final

from homeassistant.helpers.entity import EntityCategory

DOMAIN: Final = "oura"
ATTRIBUTION: Final = "Data provided by Oura Ring"

# Configuration
CONF_UPDATE_INTERVAL: Final = "update_interval"
CONF_HISTORICAL_MONTHS: Final = "historical_months"
CONF_HISTORICAL_DATA_IMPORTED: Final = "historical_data_imported"

# OAuth2 Constants
OAUTH2_AUTHORIZE: Final = "https://cloud.ouraring.com/oauth/authorize"
OAUTH2_TOKEN: Final = "https://api.ouraring.com/oauth/token"
OAUTH2_SCOPES: Final = [
    "email",
    "personal",
    "daily",
    "heartrate",
    "workout",
    "session",
    "tag",
    "spo2",
    "ring_configuration",
    "stress",
    "heart_health",
]
API_BASE_URL: Final = "https://api.ouraring.com/v2/usercollection"

# Update interval
DEFAULT_UPDATE_INTERVAL: Final = 5  # minutes
MIN_UPDATE_INTERVAL: Final = 1  # minimum 1 minute to respect API rate limits
MAX_UPDATE_INTERVAL: Final = 60  # maximum 1 hour

# Historical data loading
DEFAULT_HISTORICAL_MONTHS: Final = 3  # Fetch 3 months by default (90 days)
MIN_HISTORICAL_MONTHS: Final = 1  # Minimum 1 month
MAX_HISTORICAL_MONTHS: Final = 48  # Maximum 48 months (4 years)

# Sensor types
SENSOR_TYPES: Final = {
    # Sleep sensors
    "sleep_score": {"name": "Sleep Score", "icon": "mdi:sleep", "unit": None, "device_class": None, "state_class": "measurement", "entity_category": None, "data_category": "sleep"},
    "total_sleep_duration": {"name": "Total Sleep Duration", "icon": "mdi:clock-outline", "unit": "h", "device_class": "duration", "state_class": "total", "entity_category": None, "data_category": "sleep_detail"},
    "deep_sleep_duration": {"name": "Deep Sleep Duration", "icon": "mdi:sleep", "unit": "h", "device_class": "duration", "state_class": "total", "entity_category": None, "data_category": "sleep_detail"},
    "rem_sleep_duration": {"name": "REM Sleep Duration", "icon": "mdi:sleep", "unit": "h", "device_class": "duration", "state_class": "total", "entity_category": None, "data_category": "sleep_detail"},
    "light_sleep_duration": {"name": "Light Sleep Duration", "icon": "mdi:sleep", "unit": "h", "device_class": "duration", "state_class": "total", "entity_category": None, "data_category": "sleep_detail"},
    "awake_time": {"name": "Awake Time", "icon": "mdi:eye", "unit": "h", "device_class": "duration", "state_class": "total", "entity_category": None, "data_category": "sleep_detail"},
    "sleep_efficiency": {"name": "Sleep Efficiency", "icon": "mdi:percent", "unit": "%", "device_class": None, "state_class": "measurement", "entity_category": None, "data_category": "sleep"},
    "restfulness": {"name": "Restfulness", "icon": "mdi:bed", "unit": "%", "device_class": None, "state_class": "measurement", "entity_category": None, "data_category": "sleep"},
    "sleep_latency": {"name": "Sleep Latency", "icon": "mdi:timer", "unit": "min", "device_class": "duration", "state_class": "measurement", "entity_category": None, "data_category": "sleep_detail"},
    "sleep_timing": {"name": "Sleep Timing", "icon": "mdi:clock-check", "unit": None, "device_class": None, "state_class": "measurement", "entity_category": None, "data_category": "sleep"},
    "deep_sleep_percentage": {"name": "Deep Sleep Percentage", "icon": "mdi:percent", "unit": "%", "device_class": None, "state_class": "measurement", "entity_category": EntityCategory.DIAGNOSTIC, "data_category": "sleep_detail"},
    "rem_sleep_percentage": {"name": "REM Sleep Percentage", "icon": "mdi:percent", "unit": "%", "device_class": None, "state_class": "measurement", "entity_category": EntityCategory.DIAGNOSTIC, "data_category": "sleep_detail"},
    "time_in_bed": {"name": "Time in Bed", "icon": "mdi:bed-clock", "unit": "h", "device_class": "duration", "state_class": "total", "entity_category": None, "data_category": "sleep_detail"},
    "bedtime_start": {"name": "Bedtime Start", "icon": "mdi:sleep", "unit": None, "device_class": "timestamp", "state_class": None, "entity_category": None, "data_category": "sleep_detail"},
    "bedtime_end": {"name": "Bedtime End", "icon": "mdi:sleep-off", "unit": None, "device_class": "timestamp", "state_class": None, "entity_category": None, "data_category": "sleep_detail"},
    "low_battery_alert": {"name": "Low Battery Alert", "icon": "mdi:battery-alert", "unit": None, "device_class": None, "state_class": None, "entity_category": EntityCategory.DIAGNOSTIC, "data_category": "sleep_detail"},
    "lowest_sleep_heart_rate": {"name": "Lowest Sleep Heart Rate", "icon": "mdi:heart-minus", "unit": "bpm", "device_class": None, "state_class": "measurement", "entity_category": None, "data_category": "sleep_detail"},
    "average_sleep_heart_rate": {"name": "Average Sleep Heart Rate", "icon": "mdi:heart", "unit": "bpm", "device_class": None, "state_class": "measurement", "entity_category": None, "data_category": "sleep_detail"},

    # Readiness sensors
    "readiness_score": {"name": "Readiness Score", "icon": "mdi:heart-pulse", "unit": None, "device_class": None, "state_class": "measurement", "entity_category": None, "data_category": "readiness"},
    "temperature_deviation": {"name": "Temperature Deviation", "icon": "mdi:thermometer", "unit": "°C", "device_class": "temperature", "state_class": "measurement", "entity_category": None, "data_category": "readiness"},
    "resting_heart_rate": {"name": "Resting Heart Rate Score", "icon": "mdi:heart", "unit": None, "device_class": None, "state_class": "measurement", "entity_category": None, "data_category": "readiness"},
    "hrv_balance": {"name": "HRV Balance Score", "icon": "mdi:heart-pulse", "unit": None, "device_class": None, "state_class": "measurement", "entity_category": None, "data_category": "readiness"},
    "sleep_regularity": {"name": "Sleep Regularity Score", "icon": "mdi:calendar-clock", "unit": None, "device_class": None, "state_class": "measurement", "entity_category": None, "data_category": "readiness"},

    # Activity sensors
    "activity_score": {"name": "Activity Score", "icon": "mdi:run", "unit": None, "device_class": None, "state_class": "measurement", "entity_category": None, "data_category": "activity"},
    "steps": {"name": "Steps", "icon": "mdi:walk", "unit": "steps", "device_class": None, "state_class": "total_increasing", "entity_category": None, "data_category": "activity"},
    "active_calories": {"name": "Active Calories", "icon": "mdi:fire", "unit": "kcal", "device_class": None, "state_class": "total", "entity_category": None, "data_category": "activity"},
    "total_calories": {"name": "Total Calories", "icon": "mdi:fire", "unit": "kcal", "device_class": None, "state_class": "total", "entity_category": None, "data_category": "activity"},
    "target_calories": {"name": "Target Calories", "icon": "mdi:bullseye", "unit": "kcal", "device_class": None, "state_class": "measurement", "entity_category": EntityCategory.DIAGNOSTIC, "data_category": "activity"},
    "met_min_high": {"name": "High Activity Time", "icon": "mdi:run-fast", "unit": "min", "device_class": "duration", "state_class": "total", "entity_category": None, "data_category": "activity"},
    "met_min_medium": {"name": "Medium Activity Time", "icon": "mdi:run", "unit": "min", "device_class": "duration", "state_class": "total", "entity_category": None, "data_category": "activity"},
    "met_min_low": {"name": "Low Activity Time", "icon": "mdi:walk", "unit": "min", "device_class": "duration", "state_class": "total", "entity_category": None, "data_category": "activity"},

    # Heart Rate sensors (from heartrate endpoint - more granular data)
    "current_heart_rate": {"name": "Current Heart Rate", "icon": "mdi:heart-pulse", "unit": "bpm", "device_class": None, "state_class": "measurement", "entity_category": None, "data_category": "heartrate"},
    "average_heart_rate": {"name": "Average Heart Rate", "icon": "mdi:heart", "unit": "bpm", "device_class": None, "state_class": "measurement", "entity_category": None, "data_category": "heartrate"},
    "min_heart_rate": {"name": "Minimum Heart Rate", "icon": "mdi:heart-minus", "unit": "bpm", "device_class": None, "state_class": "measurement", "entity_category": EntityCategory.DIAGNOSTIC, "data_category": "heartrate"},
    "max_heart_rate": {"name": "Maximum Heart Rate", "icon": "mdi:heart-plus", "unit": "bpm", "device_class": None, "state_class": "measurement", "entity_category": EntityCategory.DIAGNOSTIC, "data_category": "heartrate"},

    # HRV sensors (from detailed sleep endpoint)
    "average_sleep_hrv": {"name": "Average Sleep HRV", "icon": "mdi:heart-pulse", "unit": "ms", "device_class": None, "state_class": "measurement", "entity_category": None, "data_category": "sleep_detail"},

    # Stress sensors
    "stress_high_duration": {"name": "Stress High Duration", "icon": "mdi:account-question", "unit": "min", "device_class": "duration", "state_class": "total", "entity_category": None, "data_category": "stress"},
    "recovery_high_duration": {"name": "Recovery High Duration", "icon": "mdi:lungs", "unit": "min", "device_class": "duration", "state_class": "total", "entity_category": None, "data_category": "stress"},
    "stress_day_summary": {"name": "Stress Day Summary", "icon": "mdi:account-question", "unit": None, "device_class": None, "state_class": None, "entity_category": None, "data_category": "stress"},

    # Resilience sensors
    "resilience_level": {"name": "Resilience Level", "icon": "mdi:shield", "unit": None, "device_class": "enum", "state_class": None, "entity_category": None, "options": ["limited", "adequate", "solid", "strong", "exceptional"], "data_category": "resilience"},
    "sleep_recovery_score": {"name": "Sleep Recovery Score", "icon": "mdi:bed-clock", "unit": None, "device_class": None, "state_class": "measurement", "entity_category": None, "data_category": "resilience"},
    "daytime_recovery_score": {"name": "Daytime Recovery Score", "icon": "mdi:sun-clock", "unit": None, "device_class": None, "state_class": "measurement", "entity_category": None, "data_category": "resilience"},
    "stress_resilience_score": {"name": "Stress Resilience Score", "icon": "mdi:shield-account", "unit": None, "device_class": None, "state_class": "measurement", "entity_category": None, "data_category": "resilience"},

    # SpO2 sensors (Gen3 and Oura Ring 4 only)
    "spo2_average": {"name": "SpO2 Average", "icon": "mdi:lungs", "unit": "%", "device_class": None, "state_class": "measurement", "entity_category": None, "data_category": "spo2"},
    "breathing_disturbance_index": {"name": "Breathing Disturbance Index", "icon": "mdi:lungs", "unit": None, "device_class": None, "state_class": "measurement", "entity_category": EntityCategory.DIAGNOSTIC, "data_category": "spo2"},

    # Fitness sensors
    "vo2_max": {"name": "VO2 Max", "icon": "mdi:heart-pulse", "unit": "ml/kg/min", "device_class": None, "state_class": "measurement", "entity_category": None, "data_category": "vo2_max"},
    "cardiovascular_age": {"name": "Cardiovascular Age", "icon": "mdi:heart-pulse", "unit": "years", "device_class": None, "state_class": "measurement", "entity_category": None, "data_category": "cardiovascular_age"},

    # Sleep optimization sensors
    "optimal_bedtime_start": {"name": "Optimal Bedtime Start", "icon": "mdi:bed-clock", "unit": None, "device_class": "timestamp", "state_class": None, "entity_category": EntityCategory.DIAGNOSTIC, "data_category": "sleep_time"},
    "optimal_bedtime_end": {"name": "Optimal Bedtime End", "icon": "mdi:bed-clock", "unit": None, "device_class": "timestamp", "state_class": None, "entity_category": EntityCategory.DIAGNOSTIC, "data_category": "sleep_time"},
}
