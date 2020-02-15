from homeassistant.helpers.entity import Entity
from .const import ATTRIBUTION, DEFAULT_NAME, DOMAIN_DATA, ICON, DOMAIN


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the sensor platform"""
    if discovery_info is None:
        return
    async_add_entities([JackettSensor(hass, discovery_info)], True)


async def async_setup_entry(hass, config_entry, async_add_devices):
    async_add_devices([JackettSensor(hass, {})], True)


class JackettSensor(Entity):
    """ reprisentation of the sensor"""

    def __init__(self, hass, conf):
        """ Initialise the sensor """
        self.hass = hass
        self.attr = {}
        self._state = None
        self._name = conf.get("name", DEFAULT_NAME)

    async def async_update(self):
        """ Update the sensor """
        await self.hass.data[DOMAIN_DATA]["jackett"].update_data()

    @property
    def unique_id(self):
        return "012547856632-6695548585fdc"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return ICON

    @property
    def device_state_attributes(self):
        import re

        attributes = {}
        default = {}
        card_json = []
        default["title"] = "$title"
        default["line1_default"] = "$episode"
        default["line2_default"] = "$release"
        default["line3_default"] = "$rating - $runtime"
        default["line4_default"] = "$number - $studio"
        default["icon"] = "mdi:arrow-down-bold"
        card_json.append(default)
