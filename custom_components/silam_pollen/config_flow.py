import collections
import voluptuous as vol
import aiohttp
import async_timeout
import xml.etree.ElementTree as ET
import logging

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    LocationSelector,
    LocationSelectorConfig,
    SelectSelector,
    SelectSelectorConfig,
)
from .const import (
    DOMAIN,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_ALTITUDE,
    BASE_URL_V5_9_1,
    BASE_URL_V6_0,
)

_LOGGER = logging.getLogger(__name__)

class SilamPollenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """
    Configuration flow for the SILAM Pollen integration with two steps.
    
    Step 1: The user selects basic parameters – observation area, types of pollen (optional)
           and update interval. [org ru]
    Step 2: The coordinates of the selected area are displayed, and the user is prompted to enter (or correct)
           the name of the area and coordinates via the location selector. [org ru]
           The final name of the integration is formed as "SILAM Pollen - {zone_name}". [org ru]
    """
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Step 1: basic parameters (without coordinates). [org ru]"""
        zones = {
            state.entity_id: state.attributes.get("friendly_name", state.entity_id)
            for state in self.hass.states.async_all()
            if state.entity_id.startswith("zone.")
        }
        if not zones:
            zones = {"zone.home": "Home"}
        default_zone = "zone.home" if "zone.home" in zones else list(zones.keys())[0]
        default_altitude = getattr(self.hass.config, "elevation", DEFAULT_ALTITUDE)
        # Create a list of options from the zones dictionary [org ru]
        zone_options = [{"value": zone_id, "label": name} for zone_id, name in zones.items()]
        data_schema = vol.Schema({
            vol.Required("zone_id", default=default_zone): SelectSelector(
                SelectSelectorConfig(
                    options=zone_options,
                    multiple=False,
                    mode="dropdown"
                )
            ),
            #vol.Required("altitude", default=default_altitude): vol.Coerce(float),
            vol.Optional("var", default=[]): SelectSelector(
                SelectSelectorConfig(
                    options=[
                        "alder_m22",
                        "birch_m22",
                        "grass_m32",
                        "hazel_m23",
                        "mugwort_m18",
                        "olive_m28",
                        "ragweed_m18"
                    ],
                    multiple=True,
                    mode="dropdown",
                    translation_key="config_pollen"
                )
            ),
            vol.Required("update_interval", default=DEFAULT_UPDATE_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=30)),
            vol.Optional("forecast", default=False): bool,
        })
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=data_schema
            )

        # Save the data from the first step in context [org ru]
        self.context["base_data"] = user_input.copy()
        self.context["zone_id"] = user_input.get("zone_id")
        return await self.async_step_manual_coords()

    async def async_step_manual_coords(self, user_input=None):
        """Step 2: enter coordinates and area name. [org ru]"""
        if user_input is None:
            zone_id = self.context.get("zone_id", "zone.home")
            zone = self.hass.states.get(zone_id)
            if zone is not None:
                default_latitude = zone.attributes.get("latitude", self.hass.config.latitude)
                default_longitude = zone.attributes.get("longitude", self.hass.config.longitude)
                default_zone_name = zone.attributes.get("friendly_name", "Home")
            else:
                default_latitude = self.hass.config.latitude
                default_longitude = self.hass.config.longitude
                default_zone_name = "Home"
            base_data = self.context.get("base_data", {})
            # If the "zone.home" area is selected, take the altitude from hass.config.elevation,
            # otherwise use DEFAULT_ALTITUDE from const.py. [org ru]
            if zone_id == "zone.home":
                default_altitude = getattr(self.hass.config, "elevation", DEFAULT_ALTITUDE)
            else:
                default_altitude = DEFAULT_ALTITUDE

            schema_fields = collections.OrderedDict()
            schema_fields[vol.Optional("zone_name", default=default_zone_name)] = str
            schema_fields[vol.Required("altitude", default=default_altitude)] = vol.Coerce(float)
            schema_fields[vol.Required("location", default={
                "latitude": default_latitude,
                "longitude": default_longitude,
                "radius": 5000,
            })] = LocationSelector(LocationSelectorConfig(radius=True))

            data_schema = vol.Schema(schema_fields)
            return self.async_show_form(
                step_id="manual_coords",
                data_schema=data_schema,
                description_placeholders={"altitude": "Altitude above sea level"}
            )

        # Processing the entered data [org ru]
        location = user_input.get("location", {})
        latitude = location.get("latitude")
        longitude = location.get("longitude")
        altitude_input = user_input.get("altitude")
        if altitude_input in (None, ""):
            altitude_input = getattr(self.hass.config, "elevation", DEFAULT_ALTITUDE)
        base_data = self.context.get("base_data", {})
        base_data["latitude"] = latitude
        base_data["longitude"] = longitude
        base_data["altitude"] = altitude_input
        base_data["zone_name"] = user_input.get("zone_name")
        base_data["manual_coordinates"] = True
        base_data["title"] = "SILAM Pollen - {zone_name}".format(zone_name=base_data["zone_name"])
        # Save the "forecast" parameter from the first step [org ru]
        base_data["forecast"] = self.context.get("base_data", {}).get("forecast", False)
        # Add a unique identifier based on the coordinates. [org ru]
        # (You can use different logic to generate a unique identifier)
        unique_id = f"{latitude}_{longitude}"
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        # Perform a test request to the API using the entered coordinates. [org ru]
        # The _test_api method returns True, None, and the selected URL (chosen_url) on a successful response. [org ru]
        valid, error, chosen_url = await self._test_api(latitude, longitude)
        if not valid:
            errors = {"base": error}
            return self.async_show_form(
                step_id="manual_coords",
                data_schema=vol.Schema({
                    vol.Optional("zone_name", default=base_data["zone_name"]): str,
                    vol.Required("altitude", default=altitude_input): vol.Coerce(float),
                    vol.Required("location", default={
                        "latitude": latitude,
                        "longitude": longitude,
                        "radius": 5000,
                    }): LocationSelector(LocationSelectorConfig(radius=True)),
                }),
                errors=errors,
                description_placeholders={"altitude": "Altitude above sea level"}
            )
        # Save the selected base URL in the configuration data. [org ru]
        base_data["base_url"] = chosen_url
        return self.async_create_entry(title=base_data["title"], data=base_data)

    async def _test_api(self, latitude, longitude):
        """
        Helper method to check API availability using the entered coordinates. [org ru]
        First tries a request to BASE_URL_V5_9_1, if the status is not 200 – it queries BASE_URL_V6_0. [org ru]
        If one of the base URLs returns status 200, the method returns True, None, and the chosen URL. [org ru]
        """
        urls = [BASE_URL_V5_9_1, BASE_URL_V6_0]
        last_response = ""
        chosen_url = None
        for url in urls:
            test_url = url + f"?var=POLI&latitude={latitude}&longitude={longitude}&time=present&accept=xml"
            try:
                async with aiohttp.ClientSession() as session:
                    async with async_timeout.timeout(10):
                        async with session.get(test_url) as response:
                            text = await response.text()
                            if response.status == 200:
                                chosen_url = url
                                return True, None, chosen_url
                            else:
                                last_response = text
                                _LOGGER.debug("API returned %s from %s: %s", response.status, url, text)
            except Exception as err:
                last_response = str(err)
                _LOGGER.debug("Exception when requesting %s: %s", url, str(err))
        return False, last_response, None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Returns the Options Flow handler for this entry. [org ru]"""
        # Return OptionsFlowHandler without passing config_entry [org ru]
        return OptionsFlowHandler()

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Options Flow handler for the SILAM Pollen integration."""

    async def async_step_init(self, user_input=None):
        """First and only step of Options Flow.""" 
        if user_input is not None:
            
            # If the user selected forecast_daily, automatically set forecast_hourly to True
            if user_input.get("forecast_daily"):
                user_input["forecast_hourly"] = True
                
            # Update options
            new_options = dict(self.config_entry.options)
            new_options.update(user_input)
            
            # Update data: base_url is stored in data and used by the coordinator
            new_data = dict(self.config_entry.data)
            new_version = user_input.get("version")
            new_data["version"] = new_version
            if new_version == "v5_9_1":
                new_data["base_url"] = BASE_URL_V5_9_1
            elif new_version == "v6_0":
                new_data["base_url"] = BASE_URL_V6_0
            else:
                new_data["base_url"] = "unknown"
            
            self.hass.config_entries.async_update_entry(self.config_entry, data=new_data, options=new_options)
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data=user_input)

        # If user_input is None – show the form with the pre-set version value.
        # Determine the value automatically by base_url from the entry.
        base_url = self.config_entry.data.get("base_url", "")
        if "silam_europe_pollen" in base_url:
            default_version = "v6_0"
        elif "silam_regional_pollen" in base_url:
            default_version = "v5_9_1"
        else:
            default_version = "unknown"

        # Test the availability of BASE_URL_V5_9_1 using the coordinates from the entry.
        lat = self.config_entry.data.get("latitude")
        lon = self.config_entry.data.get("longitude")
        device_name = self.config_entry.title  # Device name
        v5_9_1_available = False
        if lat is not None and lon is not None:
            try:
                async with aiohttp.ClientSession() as session:
                    async with async_timeout.timeout(10):
                        test_url = BASE_URL_V5_9_1 + f"?var=POLI&latitude={lat}&longitude={lon}&time=present&accept=xml"
                        async with session.get(test_url) as response:
                            if response.status == 200:
                                v5_9_1_available = True
                                _LOGGER.debug(
                                    "Successful check: URL %s is available for device %s",
                                    test_url, device_name
                                )
            except Exception as err:
                _LOGGER.debug(
                    "Test request for v5_9_1 failed for device %s on URL %s: %s",
                    device_name, test_url, err
                )

        # If the v5_9_1 test failed, the only option will be v6_0.
        if v5_9_1_available:
            version_options = [
                {"value": "v6_0", "label": "SILAM Europe (v6.0)"},
                {"value": "v5_9_1", "label": "SILAM Regional (v5.9.1)"}
            ]
        else:
            version_options = [
                {"value": "v6_0", "label": "SILAM Europe (v6.0)"}
            ]
            default_version = "v6_0"

        data_schema = vol.Schema({
            vol.Optional(
                "var",
                default=self.config_entry.options.get("var", self.config_entry.data.get("var", []))
            ): SelectSelector(
                SelectSelectorConfig(
                    options=[
                        "alder_m22",
                        "birch_m22",
                        "grass_m32",
                        "hazel_m23",
                        "mugwort_m18",
                        "olive_m28",
                        "ragweed_m18"
                    ],
                    multiple=True,
                    mode="dropdown",
                    translation_key="config_pollen"
                )
            ),
            vol.Optional(
                "update_interval",
                default=self.config_entry.options.get("update_interval", self.config_entry.data.get("update_interval", DEFAULT_UPDATE_INTERVAL))
            ): vol.All(vol.Coerce(int), vol.Range(min=30)),
            vol.Optional(
                "version",
                default=self.config_entry.options.get("version", self.config_entry.data.get("version", default_version))
            ): SelectSelector(
                SelectSelectorConfig(
                    options=version_options,
                    multiple=False,
                    mode="dropdown"
                )
            ),
            vol.Optional(
                "forecast",
                default=self.config_entry.options.get("forecast", self.config_entry.data.get("forecast", False))
            ): bool,
        })
        return self.async_show_form(step_id="init", data_schema=data_schema)
