DOMAIN = "ha_postaonline"

DEFAULT_UPDATE_INTERVAL = 1800 #in seconds, 30 min.
PLATFORMS = ["sensor"]

BASE_URL = "https://www.postaonline.cz/trackandtrace/-/zasilka/cislo?parcelNumbers={tracking_number}"


CONF_UPDATE_INTERVAL = "update_interval"

MANUFACTURER = "Česká pošta"
MODEL = "Parcel tracking"

CONF_TRACKING_NUMBER = "tracking_number"
CONF_DESCRIPTION = "description"
