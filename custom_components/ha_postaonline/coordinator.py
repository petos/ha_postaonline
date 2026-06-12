from datetime import timedelta
import logging

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import PostaOnlineApi
from .const import (
    DOMAIN,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class PostaOnlineDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, config_entry):
        self.config_entry = config_entry

        session = async_get_clientsession(hass)
        self.api = PostaOnlineApi(session)

        update_interval = (
            config_entry.options.get(CONF_UPDATE_INTERVAL)
            or config_entry.data.get(CONF_UPDATE_INTERVAL)
            or DEFAULT_UPDATE_INTERVAL
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self):
        tracking_number = self.config_entry.data["tracking_number"]

        try:
            data = await self.api.fetch(tracking_number)

            _LOGGER.debug(
                "Fetched parcel %s: %s",
                tracking_number,
                data,
            )

            return {
                tracking_number: data
            }

        except Exception as err:
            raise UpdateFailed(
                f"Unable to update tracking {tracking_number}: {err}"
            ) from err
