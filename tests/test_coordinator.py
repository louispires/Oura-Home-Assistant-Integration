"""Tests for the OuraCoordinator data processing methods."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "custom_components"))

from oura.coordinator import OuraDataUpdateCoordinator


class MockCoordinator:
    """Mock coordinator for testing data processing methods without HA framework."""

    data = None  # Simulates coordinator.data for carry-forward logic

    # Copy all the processing methods from the real coordinator
    _LAST_WORKOUT_KEYS = OuraDataUpdateCoordinator._LAST_WORKOUT_KEYS
    _process_data = OuraDataUpdateCoordinator._process_data
    _process_sleep_scores = OuraDataUpdateCoordinator._process_sleep_scores
    _process_sleep_details = OuraDataUpdateCoordinator._process_sleep_details
    _process_readiness = OuraDataUpdateCoordinator._process_readiness
    _process_activity = OuraDataUpdateCoordinator._process_activity
    _process_heart_rate = OuraDataUpdateCoordinator._process_heart_rate
    _process_stress = OuraDataUpdateCoordinator._process_stress
    _process_resilience = OuraDataUpdateCoordinator._process_resilience
    _process_spo2 = OuraDataUpdateCoordinator._process_spo2
    _process_vo2_max = OuraDataUpdateCoordinator._process_vo2_max
    _process_cardiovascular_age = OuraDataUpdateCoordinator._process_cardiovascular_age
    _process_sleep_time = OuraDataUpdateCoordinator._process_sleep_time
    _process_workout = OuraDataUpdateCoordinator._process_workout
    _process_session = OuraDataUpdateCoordinator._process_session
    _process_tag = OuraDataUpdateCoordinator._process_tag
    _process_enhanced_tag = OuraDataUpdateCoordinator._process_enhanced_tag
    _process_rest_mode = OuraDataUpdateCoordinator._process_rest_mode
    _process_ring_battery_level = OuraDataUpdateCoordinator._process_ring_battery_level
    _process_ring_configuration = OuraDataUpdateCoordinator._process_ring_configuration
    _parse_api_day = staticmethod(OuraDataUpdateCoordinator._parse_api_day)
    _parse_iso_datetime = staticmethod(OuraDataUpdateCoordinator._parse_iso_datetime)


def test_process_sleep_scores():
    """Test processing of sleep score data."""
    coordinator = MockCoordinator()
    data = {
        "sleep": {
            "data": [
                {
                    "score": 85,
                    "contributors": {
                        "efficiency": 90,
                        "restfulness": 80,
                        "timing": 75
                    }
                }
            ]
        }
    }
    processed = {}
    coordinator._process_sleep_scores(data, processed)

    assert processed["sleep_score"] == 85
    assert processed["restfulness"] == 80
    assert processed["sleep_timing"] == 75


def test_process_sleep_details_with_durations():
    """Test processing of sleep detail data with duration conversions."""
    from datetime import datetime, timezone
    coordinator = MockCoordinator()
    data = {
        "sleep_detail": {
            "data": [
                {
                    "efficiency": 92,
                    "total_sleep_duration": 28800,  # 8 hours in seconds
                    "deep_sleep_duration": 7200,    # 2 hours
                    "rem_sleep_duration": 7200,     # 2 hours
                    "light_sleep_duration": 14400,  # 4 hours
                    "awake_time": 1800,             # 0.5 hours
                    "latency": 600,                 # 10 minutes
                    "time_in_bed": 30600,           # 8.5 hours
                    "average_hrv": 45,
                    "average_heart_rate": 61.125,
                    "lowest_heart_rate": 55,
                    "bedtime_start": "2024-01-15T23:30:00+00:00",
                    "bedtime_end": "2024-01-16T07:30:00+00:00",
                }
            ]
        }
    }
    processed = {}
    coordinator._process_sleep_details(data, processed)

    assert processed["sleep_efficiency"] == 92
    assert processed["total_sleep_duration"] == 8.0
    assert processed["deep_sleep_duration"] == 2.0
    assert processed["rem_sleep_duration"] == 2.0
    assert processed["light_sleep_duration"] == 4.0
    assert processed["awake_time"] == 0.5
    assert processed["sleep_latency"] == 10.0
    assert processed["time_in_bed"] == 8.5
    assert processed["average_sleep_hrv"] == 45
    assert processed["lowest_sleep_heart_rate"] == 55.0
    assert processed["average_sleep_heart_rate"] == 61.125
    assert processed["deep_sleep_percentage"] == 25.0
    assert processed["rem_sleep_percentage"] == 25.0
    assert processed["bedtime_start"] == datetime(2024, 1, 15, 23, 30, 0, tzinfo=timezone.utc)
    assert processed["bedtime_end"] == datetime(2024, 1, 16, 7, 30, 0, tzinfo=timezone.utc)


def test_process_sleep_details_low_battery_alert():
    """Test that low_battery_alert is extracted from sleep_detail data."""
    coordinator = MockCoordinator()

    # Test with True value
    data_true = {
        "sleep_detail": {
            "data": [
                {
                    "low_battery_alert": True
                }
            ]
        }
    }
    processed = {}
    coordinator._process_sleep_details(data_true, processed)
    assert processed["low_battery_alert"] is True

    # Test with False value
    data_false = {
        "sleep_detail": {
            "data": [
                {
                    "low_battery_alert": False
                }
            ]
        }
    }
    processed = {}
    coordinator._process_sleep_details(data_false, processed)
    assert processed["low_battery_alert"] is False

    # Test with missing value (should default to False)
    data_missing = {
        "sleep_detail": {
            "data": [
                {
                    "total_sleep_duration": 28800
                }
            ]
        }
    }
    processed = {}
    coordinator._process_sleep_details(data_missing, processed)
    assert processed["low_battery_alert"] is False


def test_process_readiness():
    """Test processing of readiness data."""
    coordinator = MockCoordinator()
    data = {
        "readiness": {
            "data": [
                {
                    "score": 82,
                    "temperature_deviation": -0.5,
                    "contributors": {
                        "resting_heart_rate": 85,
                        "hrv_balance": 90
                    }
                }
            ]
        }
    }
    processed = {}
    coordinator._process_readiness(data, processed)

    assert processed["readiness_score"] == 82
    assert processed["temperature_deviation"] == -0.5
    assert processed["resting_heart_rate"] == 85
    assert processed["hrv_balance"] == 90


def test_process_activity():
    """Test processing of activity data."""
    coordinator = MockCoordinator()
    data = {
        "activity": {
            "data": [
                {
                    "score": 88,
                    "steps": 12345,
                    "active_calories": 450,
                    "total_calories": 2200,
                    "target_calories": 500,
                    "high_activity_met_minutes": 120,
                    "medium_activity_met_minutes": 180,
                    "low_activity_met_minutes": 240
                }
            ]
        }
    }
    processed = {}
    coordinator._process_activity(data, processed)

    assert processed["activity_score"] == 88
    assert processed["steps"] == 12345
    assert processed["active_calories"] == 450
    assert processed["total_calories"] == 2200
    assert processed["target_calories"] == 500
    assert processed["met_min_high"] == 120
    assert processed["met_min_medium"] == 180
    assert processed["met_min_low"] == 240


def test_process_heart_rate_with_aggregation():
    """Test processing of heart rate data with aggregation."""
    coordinator = MockCoordinator()
    data = {
        "heartrate": {
            "data": [
                {"bpm": 55, "timestamp": "2024-01-01T00:00:00"},
                {"bpm": 58, "timestamp": "2024-01-01T00:05:00"},
                {"bpm": 62, "timestamp": "2024-01-01T00:10:00"},
                {"bpm": 60, "timestamp": "2024-01-01T00:15:00"},
                {"bpm": 57, "timestamp": "2024-01-01T00:20:00"}
            ]
        }
    }
    processed = {}
    coordinator._process_heart_rate(data, processed)

    assert processed["current_heart_rate"] == 57
    assert processed["heart_rate_timestamp"] == "2024-01-01T00:20:00"
    assert processed["average_heart_rate"] == (55 + 58 + 62 + 60 + 57) / 5
    assert processed["min_heart_rate"] == 55
    assert processed["max_heart_rate"] == 62


def test_process_stress():
    """Test processing of stress data."""
    coordinator = MockCoordinator()
    data = {
        "stress": {
            "data": [
                {
                    "stress_high": 3600,
                    "recovery_high": 1800,
                    "day_summary": "good"
                }
            ]
        }
    }
    processed = {}
    coordinator._process_stress(data, processed)

    assert processed["stress_high_duration"] == 60
    assert processed["recovery_high_duration"] == 30
    assert processed["stress_day_summary"] == "good"


def test_process_resilience():
    """Test processing of resilience data."""
    coordinator = MockCoordinator()
    data = {
        "resilience": {
            "data": [
                {
                    "level": "solid",
                    "contributors": {
                        "sleep_recovery": 85,
                        "daytime_recovery": 78,
                        "stress": 82
                    }
                }
            ]
        }
    }
    processed = {}
    coordinator._process_resilience(data, processed)

    assert processed["resilience_level"] == "solid"
    assert processed["sleep_recovery_score"] == 85
    assert processed["daytime_recovery_score"] == 78
    assert processed["stress_resilience_score"] == 82


def test_process_spo2():
    """Test processing of SpO2 data."""
    coordinator = MockCoordinator()
    data = {
        "spo2": {
            "data": [
                {
                    "spo2_percentage": {"average": 96.5},
                    "breathing_disturbance_index": 12
                }
            ]
        }
    }
    processed = {}
    coordinator._process_spo2(data, processed)

    assert processed["spo2_average"] == 96.5
    assert processed["breathing_disturbance_index"] == 12


def test_process_vo2_max():
    """Test processing of VO2 Max data."""
    coordinator = MockCoordinator()
    data = {
        "vo2_max": {
            "data": [{"vo2_max": 45.2}]
        }
    }
    processed = {}
    coordinator._process_vo2_max(data, processed)

    assert processed["vo2_max"] == 45.2


def test_process_cardiovascular_age():
    """Test processing of cardiovascular age data."""
    coordinator = MockCoordinator()
    data = {
        "cardiovascular_age": {
            "data": [{"vascular_age": 28}]
        }
    }
    processed = {}
    coordinator._process_cardiovascular_age(data, processed)

    assert processed["cardiovascular_age"] == 28


def test_process_sleep_time():
    """Test processing of sleep time recommendations."""
    from datetime import datetime, timezone
    coordinator = MockCoordinator()
    data = {
        "sleep_time": {
            "data": [
                {
                    "day": "2023-10-25",
                    "optimal_bedtime": {
                        "day_tz": 0,
                        "start_offset": 79200,  # 22:00:00
                        "end_offset": 82800     # 23:00:00
                    }
                }
            ]
        }
    }
    processed = {}
    coordinator._process_sleep_time(data, processed)

    # 2023-10-25 22:00:00 UTC
    expected_start = datetime(2023, 10, 25, 22, 0, 0, tzinfo=timezone.utc)
    expected_end = datetime(2023, 10, 25, 23, 0, 0, tzinfo=timezone.utc)

    assert processed["optimal_bedtime_start"] == expected_start
    assert processed["optimal_bedtime_end"] == expected_end


def test_process_data_orchestration():
    """Test the main _process_data orchestration method."""
    coordinator = MockCoordinator()
    data = {
        "sleep": {"data": [{"score": 85, "contributors": {"efficiency": 90}}]},
        "sleep_detail": {"data": [{"efficiency": 92}]},
        "activity": {"data": [{"score": 88, "steps": 12345}]},
        "readiness": {"data": [{"score": 82}]}
    }

    processed = coordinator._process_data(data)

    # Verify orchestration calls all relevant processors
    assert processed["sleep_score"] == 85
    assert processed["sleep_efficiency"] == 92
    assert processed["activity_score"] == 88
    assert processed["steps"] == 12345
    assert processed["readiness_score"] == 82


def test_empty_data_handling():
    """Test that empty data structures don't cause errors."""
    coordinator = MockCoordinator()
    data = {
        "sleep": {"data": []},
        "activity": {},
        "readiness": {"data": None}
    }

    processed = coordinator._process_data(data)

    # Should return dict with default values without errors
    assert isinstance(processed, dict)
    assert processed == {"rest_mode_active": False, "workouts_today": 0}


def test_process_workout_data():
    """Test processing of workout data."""
    from datetime import datetime, timezone

    coordinator = MockCoordinator()
    today = datetime.now(timezone.utc).date().isoformat()
    data = {
        "workout": {
            "data": [
                {
                    "day": today,
                    "activity": "running",
                    "distance": 5000,
                    "calories": 320,
                    "intensity": "moderate",
                    "start_datetime": f"{today}T06:30:00+00:00",
                    "end_datetime": f"{today}T07:00:00+00:00",
                }
            ]
        }
    }

    processed = {}
    coordinator._process_workout(data, processed)

    assert processed["workouts_today"] == 1
    assert processed["last_workout_type"] == "running"
    assert processed["last_workout_distance"] == 5000
    assert processed["last_workout_calories"] == 320
    assert processed["last_workout_intensity"] == "moderate"
    assert processed["last_workout_duration"] == 30


def test_process_workout_preserves_last_values():
    """Test that last_workout_* values are preserved when no new workout data exists."""
    coordinator = MockCoordinator()
    # Simulate previous coordinator data with workout values
    coordinator.data = {
        "last_workout_type": "cycling",
        "last_workout_distance": 10000,
        "last_workout_calories": 500,
        "last_workout_intensity": "hard",
        "last_workout_duration": 45,
        "_last_workout_raw": {"activity": "cycling"},
    }

    # Empty workout response (no workouts in API window)
    data = {"workout": {"data": []}}
    processed = {}
    coordinator._process_workout(data, processed)

    assert processed["workouts_today"] == 0
    assert processed["last_workout_type"] == "cycling"
    assert processed["last_workout_distance"] == 10000
    assert processed["last_workout_calories"] == 500
    assert processed["last_workout_intensity"] == "hard"
    assert processed["last_workout_duration"] == 45
    assert processed["_last_workout_raw"] == {"activity": "cycling"}


def test_process_workout_no_previous_data():
    """Test that empty workout with no previous data doesn't crash."""
    coordinator = MockCoordinator()
    coordinator.data = None  # First run, no previous data

    data = {"workout": {"data": []}}
    processed = {}
    coordinator._process_workout(data, processed)

    assert processed["workouts_today"] == 0
    assert "last_workout_type" not in processed
    assert "last_workout_distance" not in processed
    assert "last_workout_calories" not in processed
    assert "last_workout_intensity" not in processed
    assert "last_workout_duration" not in processed


def test_process_workout_new_replaces_old():
    """Test that new workout data replaces previously carried-forward values."""
    from datetime import datetime, timezone

    coordinator = MockCoordinator()
    # Old carried-forward data
    coordinator.data = {
        "last_workout_type": "cycling",
        "last_workout_distance": 10000,
        "last_workout_calories": 500,
        "last_workout_intensity": "hard",
        "last_workout_duration": 45,
    }

    today = datetime.now(timezone.utc).date().isoformat()
    data = {
        "workout": {
            "data": [
                {
                    "day": today,
                    "activity": "running",
                    "distance": 3000,
                    "calories": 200,
                    "intensity": "easy",
                    "start_datetime": f"{today}T08:00:00+00:00",
                    "end_datetime": f"{today}T08:20:00+00:00",
                }
            ]
        }
    }

    processed = {}
    coordinator._process_workout(data, processed)

    assert processed["last_workout_type"] == "running"
    assert processed["last_workout_distance"] == 3000
    assert processed["last_workout_calories"] == 200
    assert processed["last_workout_intensity"] == "easy"
    assert processed["last_workout_duration"] == 20


def test_process_session_data():
    """Test processing of current-day sessions."""
    from datetime import datetime, timezone

    coordinator = MockCoordinator()
    today = datetime.now(timezone.utc).date().isoformat()
    data = {
        "session": {
            "data": [
                {
                    "day": today,
                    "type": "meditation",
                    "start_datetime": f"{today}T20:00:00+00:00",
                    "end_datetime": f"{today}T20:10:00+00:00",
                },
                {
                    "day": today,
                    "type": "breathing",
                    "start_datetime": f"{today}T21:00:00+00:00",
                    "end_datetime": f"{today}T21:05:00+00:00",
                }
            ]
        }
    }

    processed = {}
    coordinator._process_session(data, processed)

    assert processed["mindfulness_sessions_today"] == 2
    assert processed["meditation_duration_today"] == 15


def test_process_tag_data():
    """Test processing of current-day tags."""
    from datetime import datetime, timezone

    coordinator = MockCoordinator()
    today = datetime.now(timezone.utc).date().isoformat()
    data = {
        "tag": {
            "data": [
                {"day": today, "tags": ["coffee", "travel", "coffee"]},
            ]
        },
        "enhanced_tag": {
            "data": [
                {
                    "day": today,
                    "tag_type_code": "coffee",
                    "start_time": f"{today}T08:00:00+00:00",
                    "end_time": f"{today}T08:15:00+00:00",
                    "comment": "Morning coffee",
                }
            ]
        },
    }

    processed = {}
    coordinator._process_tag(data, processed)
    coordinator._process_enhanced_tag(data, processed)

    assert processed["tags_today"] == "coffee, travel"
    assert processed["tag_count_today"] == 2
    assert processed["_tags_today_list"] == ["coffee", "travel"]
    assert processed["_enhanced_tags_today"][0]["comment"] == "Morning coffee"


def test_process_rest_mode_data():
    """Test processing of active rest mode period."""
    from datetime import datetime, timedelta, timezone
    from unittest.mock import patch
    from homeassistant.util import dt as dt_util

    coordinator = MockCoordinator()
    now = datetime.now(timezone.utc)
    data = {
        "rest_mode": {
            "data": [
                {
                    "id": "rest-mode-1",
                    "start_day": now.date().isoformat(),
                    "end_day": (now.date() + timedelta(days=1)).isoformat(),
                    "start_time": (now - timedelta(hours=1)).isoformat(),
                    "end_time": (now + timedelta(hours=1)).isoformat(),
                }
            ]
        }
    }

    processed = {}
    with patch.object(dt_util, "now", return_value=now):
        coordinator._process_rest_mode(data, processed)

    assert processed["rest_mode_active"] is True
    assert processed["rest_mode_start"] == now - timedelta(hours=1)
    assert processed["rest_mode_end"] == now + timedelta(hours=1)
