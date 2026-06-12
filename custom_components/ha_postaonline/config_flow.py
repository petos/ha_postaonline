import voluptuous as vol

from homeassistant import config_entries

from .const import (
    DOMAIN,
    CONF_TRACKING_NUMBER,
    CONF_DESCRIPTION,
)


class PostaOnlineConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    VERSION = 1

    async def async_step_user(
        self,
        user_input=None,
    ):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=(user_input[CONF_DESCRIPTION] or user_input[CONF_TRACKING_NUMBER]),
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_TRACKING_NUMBER,
                ): str,

                vol.Optional(
                    CONF_DESCRIPTION,
                    default="",
                ): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
