"""
pollen_forecast.py

Pollen level forecast sensor for SILAM Pollen integration.
Uses a coordinator to update data. Dynamically forms a forecast based on
cached aggregated data obtained from merged_data.
Converts temperature from Kelvin to Celsius.
"""

import logging
import aiohttp
import async_timeout
from datetime import datetime, timezone
from homeassistant.components.weather import WeatherEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
try:
    from homeassistant.components.weather.const import SUPPORT_FORECAST_HOURLY, SUPPORT_FORECAST_TWICE_DAILY
except ImportError:
    SUPPORT_FORECAST_HOURLY = 2
    SUPPORT_FORECAST_TWICE_DAILY = 4
from .const import DOMAIN, RESPONSIBLE_MAPPING

_LOGGER = logging.getLogger(__name__)

async def fetch_pollen_data(latitude, longitude, base_url):
    """
    Fetch pollen data from the SILAM API using the provided latitude and longitude. [org ru]
    """
    url = f"{base_url}?var=POLI&latitude={latitude}&longitude={longitude}&time=present&accept=xml"
    try:
        async with aiohttp.ClientSession() as session:
            async with async_timeout.timeout(10):
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        _LOGGER.error("Failed to fetch data: %s", response.status)
                        return None
    except Exception as e:
        _LOGGER.error("Error fetching pollen data: %s", str(e))
        return None


class PollenForecastSensor(CoordinatorEntity, WeatherEntity):
    """Pollen level forecast sensor for SILAM Pollen integration."""

    # Only hourly and twice-daily forecasts are supported
    _attr_supported_features = SUPPORT_FORECAST_HOURLY | SUPPORT_FORECAST_TWICE_DAILY
    _attr_native_temperature_unit = "°C"

    def __init__(self, coordinator, entry_id: str, base_device_name: str):
        """
        Initialize the pollen level forecast sensor.

        :param coordinator: Coordinator instance that will update the data.
        :param entry_id: Unique entry identifier.
        :param base_device_name: Device (entry) name, used to form the sensor name.
        """
        CoordinatorEntity.__init__(self, coordinator)
        WeatherEntity.__init__(self)
        self._entry_id = entry_id
        self._base_device_name = base_device_name
        # Cached hourly forecast and twice-daily forecast,
        # which are already aggregated and saved in merged_data
        self._forecast_hourly = []
        self._forecast_twice_daily = []
        self._extra_attributes = {}
        self._attr_translation_key = "index_polen_weather"
        self._attr_has_entity_name = True
        from homeassistant.helpers.device_registry import DeviceInfo
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
        )

    @property
    def extra_state_attributes(self) -> dict:
        """Returns additional sensor attributes."""
        return self._extra_attributes

    def _update_listener(self) -> None:
        """Synchronous wrapper for triggering forecast updates.
        
        This function is called by the coordinator and should return None.
        """
        self.hass.async_create_task(self._handle_coordinator_update())
        # Explicitly return None
        return None

    async def async_added_to_hass(self) -> None:
        """Called after the sensor is added to HA.
        
        Register an update listener via the wrapper so the callback returns None.
        Then trigger a forecast update.
        """
        await super().async_added_to_hass()
        self.async_on_remove(self.coordinator.async_add_listener(self._update_listener))
        await self._handle_coordinator_update()

    @property
    def unique_id(self) -> str:
        """Returns a unique identifier for this entity."""
        return f"{self._entry_id}_pollen_forecast"

    @property
    def state(self) -> str | None:
        """
        Returns the current state – the 'condition' value
        from the first element of the hourly forecast.
        """
        if self._forecast_hourly:
            return self._forecast_hourly[0].get("condition")
        return None

    async def _handle_coordinator_update(self) -> None:
        """
        Updates sensor data using cached data from merged_data.

        From the merged dictionary:
          - The "hourly_forecast" section is used for hourly forecast data.
          - The "twice_daily_forecast" section is used for twice-daily forecast data.
          - Additionally, the "now" section is used for attributes.
        """
        _LOGGER.debug("PollenForecastSensor: calling _handle_coordinator_update")
        merged = self.coordinator.merged_data
        if not merged:
            _LOGGER.error("Merged data is missing for forming forecasts")
            return

        # Log the content for debugging
        _LOGGER.debug("Merged data content: now=%s, hourly_forecast=%s, twice_daily_forecast=%s",
                      merged.get("now"), merged.get("hourly_forecast"), merged.get("twice_daily_forecast"))

        # Update hourly forecast
        self._forecast_hourly = merged.get("hourly_forecast", [])
        # Update twice-daily forecast
        self._forecast_twice_daily = merged.get("twice_daily_forecast", [])

        # Update additional attributes from the "now" section, if present
        now_entry = merged.get("now", {})
        if now_entry:
            polisrc_val = now_entry["data"].get("POLISRC", {}).get("value")
            try:
                re_value = int(float(polisrc_val)) if polisrc_val is not None else None
            except (ValueError, TypeError):
                re_value = None
            self._extra_attributes["responsible_elevated"] = RESPONSIBLE_MAPPING.get(re_value, "unknown")
            # Additional attributes from now_entry can be added here

        self.async_write_ha_state()

    async def async_forecast_hourly(self) -> list[dict] | None:
        """Returns the hourly forecast."""
        return self._forecast_hourly

    async def async_forecast_twice_daily(self) -> list[dict] | None:
        """Returns the twice-daily forecast."""
        return self._forecast_twice_daily
