""" component to integrate with jackett """

import os
import requests
from datetime import timedelta
import logging
import voluptuous as vol
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import discovery
from homeassistant.util import Throttle

from .const import (
    CONF_NAME,
    CONF_HOST,
    CONF_PORT,
    CONF_URL_BASE,
    CONF_API,
    CONF_ENABLED,
    CONF_SENSOR,
    DOMAIN,
    DOMAIN_DATA,
    VERSION,
    PLATFORMS,
    REQUIRED_FILES,
    DEFAULT_NAME,
)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

_LOGGER = logging.getLogger(__name__)

SENSOR_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_ENABLED, default=True): cv.boolean,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_API): cv.string,
                vol.Optional(CONF_HOST, default="localhost"): cv.string,
                vol.Optional(CONF_PORT, default=9117): cv.port,
                vol.Optional(CONF_URL_BASE, default=""): cv.string,
                vol.Optional(CONF_SENSOR): vol.All(cv.ensure_list, [SENSOR_SCHEMA]),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """ setup this component using yaml """
    if config.get(DOMAIN) is None:
        # We get here if the integration is set up using config flow
        return True

    _LOGGER.info("Starting the jackett integration")

    file_check = await check_files(hass)
    if not file_check:
        return False

    hass.data[DOMAIN_DATA] = {}

    host = config[DOMAIN].get(CONF_HOST)

    hass.data[DOMAIN_DATA]["jackett"] = JackettData(hass, host, config)

    for platform in PLATFORMS:
        platform_config = config[DOMAIN].get(platform, {})

        if not platform_config:
            continue

        for entry in platform_config:
            entry_config = entry

            if not entry_config[CONF_ENABLED]:
                continue

            hass.async_create_task(
                discovery.async_load_platform(
                    hass, platform, DOMAIN, entry_config, config
                )
            )
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_IMPORT}, data={}
        )
    )
    return True


async def async_setup_entry(hass, config_entry):
    """ setup using UI """
    conf = hass.data.get(DOMAIN_DATA)
    if config_entry.source == config_entries.SOURCE_IMPORT:
        if conf is None:
            hass.async_create_task(
                hass.config_entries.async_remove(config_entry.entry_id)
            )
        return False

    _LOGGER.info("Starting the jackett integration")

    file_check = await check_files(hass)
    if not file_check:
        return False

    hass.data[DOMAIN_DATA] = {}

    host = config_entry[DOMAIN].get(CONF_HOST)

    hass.data[DOMAIN_DATA]["jackett"] = JackettData(hass, host, config_entry)

    hass.async_add_job(
        hass.config_entries.async_forward_entry_setup(config_entry, "sensor")
    )

    _LOGGER.info("Jackett all set up")

    return True


class JackettData:
    """ Handles communication and data """

    def __init__(self, hass, host, conf):
        """ init the calss """
        self.hass = hass
        self.conf = conf
        self.host = host

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def update_data(self):
        """ update data """
        self.host = self.conf.get(CONF_HOST)
        self.port = self.conf.get(CONF_PORT)
        self.apikey = self.conf.get(CONF_API)

        _LOGGER.info("host: %s", self.host)
        # try:
        #     api = requests.get(
        #         "http://{1}:{2}/api/v2.0/indexers/acgsou/test&apikey={3}".format(
        #             self.host, self.port, self.apikey
        #         ),
        #         timeout=10,
        #     )
        # except OSError:
        #     _LOGGER.warning("Host %s is not reachable", self.host)
        #     self._state = "%s cannot be reached" % self.host
        #     return

        # if api.status_code == 200:
        #     self._state = "Online"


async def check_files(hass):
    """ Return a boll that indicates that all files are present """
    base = f"{hass.config.path()}/custom_components/{DOMAIN}/"
    missing = []
    for file in REQUIRED_FILES:
        full_path = "{}{}".format(base, file)
        if not os.path.exists(full_path):
            missing.append(file)

    if missing:
        _LOGGER.critical("The following files are missing: %s", str(missing))
        returnvalue = False
    else:
        returnvalue = True

    return returnvalue


async def async_remove_entry(hass, config_entry):
    """ Handle removal of an entry """
    try:
        await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
        _LOGGER.info("Successfully removed the sensor from the Jackett integration")
    except ValueError:
        pass
