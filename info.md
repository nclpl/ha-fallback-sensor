# Fallback Sensor

A Home Assistant integration that creates a sensor with priority-based fallback behavior.

## What it does

The Fallback Sensor walks through an ordered list of source entities and returns the state of the first one that isn't `unavailable` or `unknown`. This provides automatic failover when sensors go offline.

## Example Use Case

You have three temperature sensors for a room:
1. **Z-Wave sensor** (primary)
2. **Zigbee sensor** (backup)
3. **Cloud-based weather API** (last resort)

The fallback sensor will show the Z-Wave reading normally, but if that device goes offline, it automatically switches to the Zigbee sensor, and so on. When the Z-Wave sensor comes back online, it automatically switches back.

## Features

✅ **Priority-based fallback** - Entity order matters, first has highest priority
✅ **Automatic recovery** - Switches back to higher-priority sensors when available
✅ **Attribute inheritance** - Inherits device_class, unit_of_measurement, and state_class
✅ **Universal compatibility** - Works with any sensor type (numeric, string, etc.)
✅ **Transparent operation** - Shows which entity is currently active via attributes

## Configuration

1. Go to **Settings** → **Devices & Services** → **Helpers**
2. Click **Create Helper** → **Fallback**
3. Give your sensor a name
4. Select entities in priority order (drag to reorder)
5. Done! The sensor will automatically manage failover

## Exposed Attributes

- `entity_ids` - The full ordered list of source entities
- `active_entity` - The entity_id currently providing the state
