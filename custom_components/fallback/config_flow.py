"""Config flow for Fallback integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er, selector

from .const import CONF_ENTITY_IDS, CONF_TIMEOUT, DEFAULT_TIMEOUT, DOMAIN


class FallbackConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fallback."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate that at least one entity is selected
            if not user_input.get(CONF_ENTITY_IDS):
                errors["base"] = "no_entities"
            else:
                # Create the config entry
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={},
                    options=user_input,
                )

        # Define the schema for the config flow
        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                ),
                vol.Required(CONF_ENTITY_IDS): selector.EntitySelector(
                    selector.EntitySelectorConfig(multiple=True)
                ),
                vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        max=1440,
                        unit_of_measurement="minutes",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlow:
        """Get the options flow for this handler."""
        return FallbackOptionsFlowHandler()


class FallbackOptionsFlowHandler(OptionsFlow):
    """Handle options flow for Fallback integration."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate that at least one entity is selected
            if not user_input.get(CONF_ENTITY_IDS):
                errors["base"] = "no_entities"
            else:
                # Check for circular reference
                registry = er.async_get(self.hass)
                own_entity_ids = [
                    entry.entity_id
                    for entry in er.async_entries_for_config_entry(
                        registry, self.config_entry.entry_id
                    )
                ]
                if any(
                    eid in own_entity_ids
                    for eid in user_input[CONF_ENTITY_IDS]
                ):
                    errors["base"] = "circular_reference"

            if not errors:
                # Update the config entry options
                return self.async_create_entry(title="", data=user_input)

        # Define the schema for the options flow
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_ENTITY_IDS,
                    default=self.config_entry.options.get(CONF_ENTITY_IDS, []),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(multiple=True)
                ),
                vol.Optional(
                    CONF_TIMEOUT,
                    default=self.config_entry.options.get(CONF_TIMEOUT, DEFAULT_TIMEOUT),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        max=1440,
                        unit_of_measurement="minutes",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )
