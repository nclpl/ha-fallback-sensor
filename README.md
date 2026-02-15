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

## Usage

Once created, the fallback sensor will:
- Display the state of the first available entity
- Update automatically when source entities change state
- Switch to the next available entity if the current one becomes unavailable
- Switch back to higher-priority entities when they become available again

### Attributes

The sensor exposes these attributes:
- `entity_ids`: The full ordered list of source entities
- `active_entity`: The entity_id currently providing the state

## Development Status

This is currently in **Phase 1** (local iteration). The integration is being tested as a custom component before being submitted to Home Assistant core.

## Roadmap

- [x] Phase 1: Custom integration (iterate locally)
- [ ] Phase 2: Prepare for core contribution
- [ ] Phase 3: Get community buy-in
- [ ] Phase 4: Submit PR to Home Assistant core

## Contributing

This integration is intended for submission to Home Assistant core. Feedback and testing are welcome!

## License

MIT License - See LICENSE file for details
