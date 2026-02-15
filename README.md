# Home Assistant Fallback Sensor Integration

A custom integration for Home Assistant that creates a sensor with priority-based fallback behavior. The sensor displays the state of the first available entity from an ordered list.

## Concept

The Fallback Sensor walks through an ordered list of source entities and returns the state of the first one that isn't `unavailable` or `unknown`. This provides automatic failover when sensors go offline.

**Example use case:** You have three temperature sensors for a room:
1. Z-Wave sensor (primary)
2. Zigbee sensor (backup)
3. Cloud-based Thermostat integration (last resort)

The fallback sensor will show the Z-Wave reading normally, but if that device goes offline, it automatically switches to the Zigbee sensor, and so on.

## Features

- **Priority-based fallback**: Entity order matters — first in the list has highest priority
- **Automatic recovery**: When a higher-priority sensor comes back online, the fallback sensor switches back
- **Timeout detection**: Optional feature to detect "stuck" sensors that stop updating (configurable)
- **Attribute inheritance**: Inherits `device_class`, `unit_of_measurement`, and `state_class` from the active entity
- **Works with any sensor type**: Numeric sensors, string sensors, binary sensors, etc.
- **Transparent operation**: Exposes which entity is currently active via attributes

## Installation

### Manual Installation

1. Copy the `custom_components/fallback` directory to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Helpers
4. Click "Create Helper" → "Fallback"
5. Configure your sensor

### HACS Installation (coming soon)

This integration will be available through HACS once it's published to the default repository.

## Configuration

The integration is configured through the UI:

1. **Name**: Give your fallback sensor a name
2. **Entities**: Select entities in priority order (drag to reorder)
   - First entity = highest priority
   - Last entity = lowest priority (last resort)
3. **State change timeout** (optional): Number of minutes before considering a sensor "stuck"
   - Set to 0 to disable timeout detection (default)
   - If enabled, the sensor will fall back to the next entity if the current entity's state hasn't changed for this duration
   - Useful for detecting sensors that are still "available" but have stopped updating

## Usage

Once created, the fallback sensor will:
- Display the state of the first available entity
- Update automatically when source entities change state
- Switch to the next available entity if the current one becomes unavailable
- Switch to the next available entity if the current one times out (if timeout is configured)
- Switch back to higher-priority entities when they become available again

### Attributes

The sensor exposes these attributes:
- `entity_ids`: The full ordered list of source entities
- `active_entity`: The entity_id currently providing the state
- `active_priority`: The priority position of the active entity (1 = primary, 2 = first backup, etc.)

## License

MIT License - See LICENSE file for details
