""" consts for jackett """

DOMAIN = "jackett"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.1"
PLATFORMS = ["sensor"]
REQUIRED_FILES = ["const.py", "__init__.py", "sensor.py"]
ATTRIBUTION = "Data from this is provided by Jackett."
ICON = "mdi:format-quote-close"

# Config
CONF_SENSOR = "sensor"
CONF_NAME = "name"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_URL_BASE = "url_base"
CONF_API = "api_key"
CONF_ENABLED = "enabled"

DEFAULT_NAME = DOMAIN
