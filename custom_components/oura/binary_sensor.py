"""Binary sensor platform for Oura Ring integration."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import OuraDataUpdateCoordinator


def _oura_device_info(coordinator: OuraDataUpdateCoordinator) -> DeviceInfo:
    """Return shared Oura Ring device info, enriched with ring configuration when available."""
    model = "Oura Ring"
    sw_version = None
    if coordinator.data:
        if hw_type := coordinator.data.get("ring_hardware_type"):
            model = f"Oura Ring {hw_type.capitalize()}"
        sw_version = coordinator.data.get("ring_firmware_version")
    return DeviceInfo(
        identifiers={(DOMAIN, coordinator.entry.entry_id)},
        name="Oura Ring",
        manufacturer="Oura",
        model=model,
        sw_version=sw_version,
        entry_type=DeviceEntryType.SERVICE,
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Oura Ring binary sensors."""
    coordinator: OuraDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        OuraRestModeBinarySensor(coordinator),
        OuraRingChargingBinarySensor(coordinator),
    ])


class OuraRestModeBinarySensor(CoordinatorEntity[OuraDataUpdateCoordinator], BinarySensorEntity):
    """Representation of Oura Ring rest mode binary sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_icon = "mdi:bed"
    _attr_name = "Rest Mode"
    _attr_translation_key = "rest_mode"

    def __init__(self, coordinator: OuraDataUpdateCoordinator) -> None:
        """Initialize the rest mode binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_rest_mode_active"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Oura Ring."""
        return _oura_device_info(self.coordinator)

    @property
    def is_on(self) -> bool | None:
        """Return true if rest mode is active."""
        return self.coordinator.data.get("rest_mode_active")

    @property
    def extra_state_attributes(self) -> dict[str, str] | dict[str, object] | None:
        """Return extra state attributes."""
        attrs = {}
        if self.coordinator.data and "_active_rest_mode_raw" in self.coordinator.data:
            raw_period = self.coordinator.data["_active_rest_mode_raw"]
            if raw_period.get("id"):
                attrs["id"] = raw_period["id"]
            if raw_period.get("start_day"):
                attrs["start_day"] = raw_period["start_day"]
            if raw_period.get("end_day"):
                attrs["end_day"] = raw_period["end_day"]
        return attrs or None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.data is not None
            and "rest_mode_active" in self.coordinator.data
            and self.coordinator.data["rest_mode_active"] is not None
        )


class OuraRingChargingBinarySensor(CoordinatorEntity[OuraDataUpdateCoordinator], BinarySensorEntity):
    """Representation of Oura Ring charging state binary sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING
    _attr_translation_key = "ring_charging"

    def __init__(self, coordinator: OuraDataUpdateCoordinator) -> None:
        """Initialize the ring charging binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_ring_battery_charging"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Oura Ring."""
        return _oura_device_info(self.coordinator)

    @property
    def is_on(self) -> bool | None:
        """Return true if the ring is charging."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("ring_battery_charging")

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.data is not None
            and "ring_battery_charging" in self.coordinator.data
            and self.coordinator.data["ring_battery_charging"] is not None
        )