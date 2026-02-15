"""Sensor platform for Fallback integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_UNIT_OF_MEASUREMENT,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_interval
from homeassistant.util import dt as dt_util

from .const import CONF_ENTITY_IDS, CONF_TIMEOUT, DEFAULT_TIMEOUT

_LOGGER = logging.getLogger(__name__)

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
    timeout = int(entry.options.get(CONF_TIMEOUT, DEFAULT_TIMEOUT))

    async_add_entities([FallbackSensor(name, entity_ids, unique_id, timeout)], True)


class FallbackSensor(SensorEntity):
    """Representation of a Fallback Sensor."""

    _attr_should_poll = False

    def __init__(self, name: str, entity_ids: list[str], unique_id: str, timeout: int) -> None:
        """Initialize the Fallback sensor."""
        self._entity_ids = entity_ids
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._timeout = timeout  # Timeout in minutes
        self._active_entity_id: str | None = None
        self._active_entity_priority: int | None = None
        self._fallback_reason: str | None = None
        self._attr_native_value: Any = None
        self._attr_native_unit_of_measurement: str | None = None
        self._attr_device_class: str | None = None
        self._attr_state_class: str | None = None
        # Track last state and change time for each entity
        self._entity_states: dict[str, Any] = {}
        self._entity_last_changed: dict[str, datetime] = {}

    async def async_added_to_hass(self) -> None:
        """Register state change listener when added to hass."""
        # Subscribe to state changes for all source entities
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, self._entity_ids, self._async_state_changed
            )
        )

        # If timeout is enabled, set up periodic check
        if self._timeout > 0:
            self.async_on_remove(
                async_track_time_interval(
                    self.hass,
                    self._async_check_timeout,
                    timedelta(minutes=1),  # Check every minute
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
    def _async_check_timeout(self, now: datetime) -> None:
        """Periodically check if current entity has timed out."""
        self._update_state()
        self.async_write_ha_state()

    @callback
    def _update_state(self) -> None:
        """Walk the priority list and pick the first available entity."""
        now = dt_util.utcnow()
        previous_active = self._active_entity_id
        last_skip_reason: str | None = None

        for index, entity_id in enumerate(self._entity_ids):
            state = self.hass.states.get(entity_id)
            if state is None:
                last_skip_reason = "not_loaded"
                continue
            if state.state in IGNORE_STATES:
                last_skip_reason = state.state  # "unavailable" or "unknown"
                continue

            # Track state changes for timeout detection
            prev_state = self._entity_states.get(entity_id)
            if prev_state != state.state:
                # State changed, update tracking
                self._entity_states[entity_id] = state.state
                self._entity_last_changed[entity_id] = now
            elif entity_id not in self._entity_last_changed:
                # First time seeing this entity
                self._entity_states[entity_id] = state.state
                self._entity_last_changed[entity_id] = now

            # Check if entity has timed out (if timeout is enabled)
            if self._timeout > 0:
                last_changed = self._entity_last_changed.get(entity_id, now)
                time_since_change = now - last_changed
                timeout_duration = timedelta(minutes=self._timeout)

                if time_since_change >= timeout_duration:
                    last_skip_reason = "timeout"
                    continue

            # Found a valid entity, use its state
            self._active_entity_id = entity_id
            self._active_entity_priority = index + 1  # 1-based priority
            self._fallback_reason = last_skip_reason if index > 0 else None

            if previous_active != entity_id:
                if previous_active is None:
                    _LOGGER.debug(
                        "Fallback sensor '%s' initial active entity: %s (priority %d)",
                        self._attr_name, entity_id, index + 1,
                    )
                else:
                    _LOGGER.debug(
                        "Fallback sensor '%s' switched from %s to %s (priority %d, reason: %s)",
                        self._attr_name, previous_active, entity_id, index + 1,
                        last_skip_reason,
                    )

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

        # All entities are unavailable/unknown/timed out
        if previous_active is not None:
            _LOGGER.debug(
                "Fallback sensor '%s' has no available entities",
                self._attr_name,
            )
        self._attr_native_value = None
        self._active_entity_id = None
        self._active_entity_priority = None
        self._fallback_reason = None
        self._attr_native_unit_of_measurement = None
        self._attr_device_class = None
        self._attr_state_class = None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            "entity_ids": self._entity_ids,
            "active_entity": self._active_entity_id,
            "active_priority": self._active_entity_priority,
            "fallback_reason": self._fallback_reason,
        }

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend."""
        return "mdi:format-list-numbered"
