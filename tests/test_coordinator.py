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
    today = datetime.now(timezone.utc).date().isoformat()
    data = {
        "sleep_detail": {
            "data": [
                {
                    "day": today,
                    "type": "long_sleep",
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
    from datetime import datetime, timezone
    coordinator = MockCoordinator()
    today = datetime.now(timezone.utc).date().isoformat()

    # Test with True value (record must be completed to be processed)
    data_true = {
        "sleep_detail": {
            "data": [
                {
                    "day": today,
                    "bedtime_start": "2024-01-15T23:30:00+00:00",
                    "bedtime_end": "2024-01-16T07:30:00+00:00",
                    "low_battery_alert": True,
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
                    "day": today,
                    "bedtime_start": "2024-01-15T23:30:00+00:00",
                    "bedtime_end": "2024-01-16T07:30:00+00:00",
                    "low_battery_alert": False,
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
                    "day": today,
                    "bedtime_start": "2024-01-15T23:30:00+00:00",
                    "bedtime_end": "2024-01-16T07:30:00+00:00",
                    "total_sleep_duration": 28800,
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
                    "low_activity_met_minutes": 240,
                    "high_activity_time": 3600,    # 60 minutes in seconds
                    "medium_activity_time": 5400,  # 90 minutes in seconds
                    "low_activity_time": 7200,     # 120 minutes in seconds
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
    assert processed["high_activity_time"] == 60.0
    assert processed["medium_activity_time"] == 90.0
    assert processed["low_activity_time"] == 120.0


def test_process_heart_rate_with_aggregation():
    """Test processing of heart rate data with aggregation (uses recent timestamps)."""
    from datetime import datetime, timedelta, timezone
    coordinator = MockCoordinator()
    now = datetime.now(timezone.utc)
    # Use recent timestamps so they fall within the 24h aggregation window
    t = [(now - timedelta(minutes=20 - i * 5)).strftime("%Y-%m-%dT%H:%M:%S+00:00") for i in range(5)]
    bpms = [55, 58, 62, 60, 57]
    data = {
        "heartrate": {
            "data": [{"bpm": bpms[i], "timestamp": t[i]} for i in range(5)]
        }
    }
    processed = {}
    coordinator._process_heart_rate(data, processed)

    assert processed["current_heart_rate"] == 57
    assert isinstance(processed["heart_rate_timestamp"], datetime)
    assert processed["average_heart_rate"] == sum(bpms) / len(bpms)
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
            "data": [{"vascular_age": 28, "pulse_wave_velocity": 6.5}]
        }
    }
    processed = {}
    coordinator._process_cardiovascular_age(data, processed)

    assert processed["cardiovascular_age"] == 28
    assert processed["pulse_wave_velocity"] == 6.5


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
    from datetime import datetime, timezone
    coordinator = MockCoordinator()
    today = datetime.now(timezone.utc).date().isoformat()
    data = {
        "sleep": {"data": [{"score": 85, "contributors": {"efficiency": 90}}]},
        "sleep_detail": {"data": [{"day": today, "efficiency": 92, "bedtime_start": "2024-01-15T23:30:00+00:00", "bedtime_end": "2024-01-16T07:30:00+00:00"}]},
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


# --- Bedtime sensor stability tests ---

def test_bedtime_inprogress_record_filtered():
    """In-progress record (null bedtime_end) is ignored; completed record used."""
    from datetime import datetime, timezone

    coordinator = MockCoordinator()
    today = datetime.now(timezone.utc).date().isoformat()
    completed_record = {
        "day": today,
        "type": "long_sleep",
        "bedtime_start": "2024-01-15T23:00:00+00:00",
        "bedtime_end": "2024-01-16T07:00:00+00:00",
        "total_sleep_duration": 28800,
    }
    inprogress_record = {
        "day": today,
        "type": "long_sleep",
        "bedtime_start": "2024-01-16T23:30:00+00:00",
        "bedtime_end": None,  # still sleeping
    }

    data = {"sleep_detail": {"data": [completed_record, inprogress_record]}}
    processed = {}
    coordinator._process_sleep_details(data, processed)

    assert processed["bedtime_start"] == datetime(2024, 1, 15, 23, 0, 0, tzinfo=timezone.utc)
    assert processed["bedtime_end"] == datetime(2024, 1, 16, 7, 0, 0, tzinfo=timezone.utc)
    assert processed["total_sleep_duration"] == 8.0


def test_bedtime_long_sleep_preferred_over_nap():
    """long_sleep type is preferred over a confirmed nap when both are completed."""
    from datetime import datetime, timezone

    coordinator = MockCoordinator()
    today = datetime.now(timezone.utc).date().isoformat()
    nap_record = {
        "day": today,
        "type": "sleep",
        "bedtime_start": "2024-01-16T14:00:00+00:00",
        "bedtime_end": "2024-01-16T14:45:00+00:00",
    }
    main_record = {
        "day": today,
        "type": "long_sleep",
        "bedtime_start": "2024-01-15T23:00:00+00:00",
        "bedtime_end": "2024-01-16T07:00:00+00:00",
    }

    data = {"sleep_detail": {"data": [nap_record, main_record]}}
    processed = {}
    coordinator._process_sleep_details(data, processed)

    assert processed["bedtime_start"] == datetime(2024, 1, 15, 23, 0, 0, tzinfo=timezone.utc)
    assert processed["bedtime_end"] == datetime(2024, 1, 16, 7, 0, 0, tzinfo=timezone.utc)


def test_bedtime_fallback_to_existing_data():
    """When only in-progress records exist, last known bedtime values are preserved."""
    from datetime import datetime, timezone

    coordinator = MockCoordinator()
    previous_start = datetime(2024, 1, 15, 23, 0, 0, tzinfo=timezone.utc)
    previous_end = datetime(2024, 1, 16, 7, 0, 0, tzinfo=timezone.utc)
    coordinator.data = {
        "bedtime_start": previous_start,
        "bedtime_end": previous_end,
        "sleep_score": 82,
    }

    inprogress_record = {
        "type": "long_sleep",
        "bedtime_start": "2024-01-16T23:30:00+00:00",
        "bedtime_end": None,
    }
    data = {"sleep_detail": {"data": [inprogress_record]}}
    processed = {}
    coordinator._process_sleep_details(data, processed)

    assert processed["bedtime_start"] == previous_start
    assert processed["bedtime_end"] == previous_end


def test_bedtime_no_data_no_existing():
    """Empty sleep_detail with no self.data → no crash, bedtime keys absent."""
    coordinator = MockCoordinator()
    coordinator.data = None

    data = {"sleep_detail": {"data": []}}
    processed = {}
    coordinator._process_sleep_details(data, processed)

    assert "bedtime_start" not in processed
    assert "bedtime_end" not in processed


# --- New tests for v2.8.0 changes ---

def test_process_activity_time_fields():
    """Activity time fields (seconds) are converted to minutes."""
    coordinator = MockCoordinator()
    data = {
        "activity": {
            "data": [
                {
                    "high_activity_time": 1800,    # 30 min
                    "medium_activity_time": 3600,  # 60 min
                    "low_activity_time": 0,
                }
            ]
        }
    }
    processed = {}
    coordinator._process_activity(data, processed)

    assert processed["high_activity_time"] == 30.0
    assert processed["medium_activity_time"] == 60.0
    assert processed["low_activity_time"] == 0.0


def test_process_activity_time_fields_absent():
    """Missing activity time fields don't populate keys."""
    coordinator = MockCoordinator()
    data = {
        "activity": {
            "data": [{"high_activity_met_minutes": 50}]
        }
    }
    processed = {}
    coordinator._process_activity(data, processed)

    assert "high_activity_time" not in processed
    assert "medium_activity_time" not in processed
    assert "low_activity_time" not in processed


def test_process_cardiovascular_age_pulse_wave_velocity():
    """pulse_wave_velocity is populated when present in API response."""
    coordinator = MockCoordinator()
    data = {
        "cardiovascular_age": {
            "data": [{"vascular_age": 32, "pulse_wave_velocity": 7.2}]
        }
    }
    processed = {}
    coordinator._process_cardiovascular_age(data, processed)

    assert processed["cardiovascular_age"] == 32
    assert processed["pulse_wave_velocity"] == 7.2


def test_process_cardiovascular_age_no_pulse_wave_velocity():
    """pulse_wave_velocity absent from response doesn't populate key."""
    coordinator = MockCoordinator()
    data = {
        "cardiovascular_age": {
            "data": [{"vascular_age": 32}]
        }
    }
    processed = {}
    coordinator._process_cardiovascular_age(data, processed)

    assert processed["cardiovascular_age"] == 32
    assert "pulse_wave_velocity" not in processed


def test_process_sleep_details_sorts_by_day():
    """Most recent record by day wins even when API returns older record last."""
    from datetime import datetime, timedelta, timezone

    coordinator = MockCoordinator()
    today = datetime.now(timezone.utc).date()
    yesterday = (today - timedelta(days=1)).isoformat()
    today_str = today.isoformat()

    older_record = {
        "day": yesterday,
        "type": "long_sleep",
        "bedtime_start": "2024-01-14T23:00:00+00:00",
        "bedtime_end": "2024-01-15T07:00:00+00:00",
    }
    newer_record = {
        "day": today_str,
        "type": "long_sleep",
        "bedtime_start": "2024-01-15T23:30:00+00:00",
        "bedtime_end": "2024-01-16T07:30:00+00:00",
    }
    # API returns older record last — the sort should still pick the newer one
    data = {"sleep_detail": {"data": [newer_record, older_record]}}
    processed = {}
    coordinator._process_sleep_details(data, processed)

    assert processed["bedtime_start"] == datetime(2024, 1, 15, 23, 30, 0, tzinfo=timezone.utc)
    assert processed["bedtime_end"] == datetime(2024, 1, 16, 7, 30, 0, tzinfo=timezone.utc)


def test_process_sleep_details_ignores_records_older_than_2_days():
    """Records older than 2 days are discarded; last-known values preserved."""
    from datetime import datetime, timedelta, timezone

    coordinator = MockCoordinator()
    today = datetime.now(timezone.utc).date()
    three_days_ago = (today - timedelta(days=3)).isoformat()

    previous_start = datetime(2024, 1, 15, 23, 0, 0, tzinfo=timezone.utc)
    previous_end = datetime(2024, 1, 16, 7, 0, 0, tzinfo=timezone.utc)
    coordinator.data = {"bedtime_start": previous_start, "bedtime_end": previous_end}

    stale_record = {
        "day": three_days_ago,
        "type": "long_sleep",
        "bedtime_start": "2023-01-10T22:00:00+00:00",
        "bedtime_end": "2023-01-11T06:00:00+00:00",
    }
    data = {"sleep_detail": {"data": [stale_record]}}
    processed = {}
    coordinator._process_sleep_details(data, processed)

    # Stale record filtered → no completed records → fall back to previous data
    assert processed.get("bedtime_start") == previous_start
    assert processed.get("bedtime_end") == previous_end


def test_process_heart_rate_sorts_by_timestamp():
    """Out-of-order heart rate readings are sorted; most recent is current_heart_rate."""
    from datetime import datetime, timedelta, timezone

    coordinator = MockCoordinator()
    now = datetime.now(timezone.utc)
    t = lambda m: (now - timedelta(minutes=m)).strftime("%Y-%m-%dT%H:%M:%S+00:00")

    # Provide readings out of order: oldest is last in list
    data = {
        "heartrate": {
            "data": [
                {"bpm": 70, "timestamp": t(10)},  # 10 min ago — should win
                {"bpm": 80, "timestamp": t(0)},   # now — this is the latest
                {"bpm": 65, "timestamp": t(20)},  # oldest
            ]
        }
    }
    processed = {}
    coordinator._process_heart_rate(data, processed)

    assert processed["current_heart_rate"] == 80


def test_process_heart_rate_aggregates_last_24h():
    """Aggregation uses only readings within the last 24 hours."""
    from datetime import datetime, timedelta, timezone

    coordinator = MockCoordinator()
    now = datetime.now(timezone.utc)
    recent_ts = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    old_ts = (now - timedelta(hours=30)).strftime("%Y-%m-%dT%H:%M:%S+00:00")

    data = {
        "heartrate": {
            "data": [
                {"bpm": 100, "timestamp": old_ts},   # outside 24h window
                {"bpm": 60, "timestamp": recent_ts},  # inside 24h window
            ]
        }
    }
    processed = {}
    coordinator._process_heart_rate(data, processed)

    # current_heart_rate is still the most recent overall reading
    assert processed["current_heart_rate"] == 60
    # aggregation should only include the recent reading
    assert processed["average_heart_rate"] == 60.0
    assert processed["min_heart_rate"] == 60
    assert processed["max_heart_rate"] == 60


def test_process_heart_rate_fallback_to_last10_when_no_recent():
    """When all readings are older than 24h, falls back to last 10 by position."""
    from datetime import datetime, timedelta, timezone

    coordinator = MockCoordinator()
    now = datetime.now(timezone.utc)
    old_ts = lambda m: (now - timedelta(hours=30 + m)).strftime("%Y-%m-%dT%H:%M:%S+00:00")

    data = {
        "heartrate": {
            "data": [
                {"bpm": 55, "timestamp": old_ts(0)},
                {"bpm": 65, "timestamp": old_ts(1)},
                {"bpm": 75, "timestamp": old_ts(2)},
            ]
        }
    }
    processed = {}
    coordinator._process_heart_rate(data, processed)

    # Falls back to last 10; current is most recent after sort
    assert processed["current_heart_rate"] == 55  # smallest offset = most recent
    assert processed["average_heart_rate"] == (55 + 65 + 75) / 3
