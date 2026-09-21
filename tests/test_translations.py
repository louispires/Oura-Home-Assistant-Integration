"""Tests that strings.json and all translations stay in sync with SENSOR_TYPES.

Guards against adding a sensor to SENSOR_TYPES without a matching entity name,
and against translations/*.json drifting out of sync with strings.json.
"""
import json
from pathlib import Path

import pytest

from custom_components.oura.const import SENSOR_TYPES

_COMPONENT_DIR = Path(__file__).parent.parent / "custom_components" / "oura"
_STRINGS_PATH = _COMPONENT_DIR / "strings.json"
_TRANSLATION_LOCALES = ("en", "de", "es", "fr")


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def test_strings_json_has_a_name_for_every_sensor():
    """Every SENSOR_TYPES key must have an entity.sensor name in strings.json."""
    strings = _load(_STRINGS_PATH)
    sensor_names = strings["entity"]["sensor"]

    missing = [key for key in SENSOR_TYPES if key not in sensor_names]
    assert not missing, f"strings.json missing entity.sensor names for: {missing}"


@pytest.mark.parametrize("locale", _TRANSLATION_LOCALES)
def test_translation_sensor_keys_match_strings_json(locale):
    """Each translation file must have the exact same entity.sensor keys as strings.json."""
    strings_keys = set(_load(_STRINGS_PATH)["entity"]["sensor"])
    translation_path = _COMPONENT_DIR / "translations" / f"{locale}.json"
    translation_keys = set(_load(translation_path)["entity"]["sensor"])

    assert translation_keys == strings_keys, (
        f"{locale}.json entity.sensor keys differ from strings.json: "
        f"missing={strings_keys - translation_keys}, extra={translation_keys - strings_keys}"
    )


@pytest.mark.parametrize("locale", _TRANSLATION_LOCALES)
def test_translation_abort_keys_match_strings_json(locale):
    """Each translation file must have the exact same config.abort keys as strings.json."""
    strings_keys = set(_load(_STRINGS_PATH)["config"]["abort"])
    translation_path = _COMPONENT_DIR / "translations" / f"{locale}.json"
    translation_keys = set(_load(translation_path)["config"]["abort"])

    assert translation_keys == strings_keys, (
        f"{locale}.json config.abort keys differ from strings.json: "
        f"missing={strings_keys - translation_keys}, extra={translation_keys - strings_keys}"
    )
