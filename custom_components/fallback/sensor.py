"""Sensor platform for Fallback integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_UNIT_OF_MEASUREMENT,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import CONF_ENTITY_IDS

IGNORE_STATES = {STATE_UNAVAILABLE, STATE_UNKNOWN}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Fallback sensor based on a config entry."""
    entity_ids = entry.options[CONF_ENTITY_IDS]
    name = entry.title
    unique_id = entry.entry_id

    async_add_entities([FallbackSensor(name, entity_ids, unique_id)], True)


class FallbackSensor(SensorEntity):
    """Representation of a Fallback Sensor."""

    _attr_should_poll = False

    def __init__(self, name: str, entity_ids: list[str], unique_id: str) -> None:
        """Initialize the Fallback sensor."""
        self._entity_ids = entity_ids
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._active_entity_id: str | None = None
        self._attr_native_value: Any = None
        self._attr_native_unit_of_measurement: str | None = None
        self._attr_device_class: str | None = None
        self._attr_state_class: str | None = None

    async def async_added_to_hass(self) -> None:
        """Register state change listener when added to hass."""
        # Subscribe to state changes for all source entities
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, self._entity_ids, self._async_state_changed
            )
        )
        # Calculate initial state
        self._update_state()

    @callback
    def _async_state_changed(self, event: Any) -> None:
        """Handle state changes of source entities."""
        self._update_state()
        self.async_write_ha_state()

    @callback
    def _update_state(self) -> None:
        """Walk the priority list and pick the first available entity."""
        for entity_id in self._entity_ids:
            state = self.hass.states.get(entity_id)
            if state is None:
                continue
            if state.state not in IGNORE_STATES:
                # Found a valid entity, use its state
                self._active_entity_id = entity_id

                # Try to convert to numeric if possible, otherwise keep as string
                try:
                    self._attr_native_value = float(state.state)
                except (ValueError, TypeError):
                    self._attr_native_value = state.state

                # Inherit attributes from the active entity
                self._attr_native_unit_of_measurement = state.attributes.get(
                    ATTR_UNIT_OF_MEASUREMENT
                )
                self._attr_device_class = state.attributes.get("device_class")
                self._attr_state_class = state.attributes.get("state_class")

                return

        # All entities are unavailable/unknown
        self._attr_native_value = None
        self._active_entity_id = None
        self._attr_native_unit_of_measurement = None
        self._attr_device_class = None
        self._attr_state_class = None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            "entity_ids": self._entity_ids,
            "active_entity": self._active_entity_id,
        }

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend."""
        return "mdi:format-list-numbered"
