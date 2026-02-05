"""Sensor platform for Oura Ring integration."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, SENSOR_TYPES
from .coordinator import OuraDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Oura Ring sensors."""
    coordinator: OuraDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        OuraSensor(coordinator, sensor_type, sensor_info)
        for sensor_type, sensor_info in SENSOR_TYPES.items()
    ]

    async_add_entities(entities)


class OuraSensor(CoordinatorEntity[OuraDataUpdateCoordinator], SensorEntity):
    """Representation of an Oura Ring sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OuraDataUpdateCoordinator,
        sensor_type: str,
        sensor_info: dict,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = sensor_info['name']
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{sensor_type}"
        self._attr_translation_key = sensor_type
        self._attr_icon = sensor_info["icon"]
        self._attr_native_unit_of_measurement = sensor_info.get("unit")
        self._attr_device_class = sensor_info.get("device_class")
        self._attr_state_class = sensor_info.get("state_class")
        self._attr_entity_category = sensor_info.get("entity_category")
        
        # Set options for enum sensors
        if sensor_info.get("device_class") == "enum" and "options" in sensor_info:
            self._attr_options = sensor_info["options"]

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Oura Ring."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.entry.entry_id)},
            name="Oura Ring",
            manufacturer="Oura",
            model="Oura Ring",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._sensor_type)

    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Return extra state attributes.
        
        Includes the data_date to show which day's data is being displayed.
        """
        if self.coordinator.data and "_data_date" in self.coordinator.data:
            return {"data_date": self.coordinator.data["_data_date"]}
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available.
        
        Sensor is available if:
        1. We have data (even if last update failed due to transient error)
        2. The sensor key exists in the data
        3. The value is not None
        """
        return (
            self.coordinator.data is not None
            and self._sensor_type in self.coordinator.data
            and self.coordinator.data[self._sensor_type] is not None
        )
