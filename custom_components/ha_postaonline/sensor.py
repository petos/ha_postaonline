from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    tracking_number = entry.data["tracking_number"]

    async_add_entities(
        [
            PostaStatusSensor(coordinator,entry,tracking_number,),
            PostaLocationSensor(coordinator,entry,tracking_number,),
        ]
    )


class PostaBaseSensor(CoordinatorEntity,SensorEntity):
    def __init__(self,coordinator,entry,tracking_number: str,):
        super().__init__(coordinator)

        self._entry = entry
        self._tracking_number = tracking_number

    @property
    def _parcel(self):
        return (
            self.coordinator.data or {}
        ).get(
            self._tracking_number,
            {},
        )

    @property
    def available(self):
        return bool(self._parcel)

    @property
    def device_info(self):
        description = self._entry.data.get("description")

        name = (
            f"{self._tracking_number} - {description}"
            if description
            else self._tracking_number
        )

        return DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    self._tracking_number,
                )
            },
            name=name,
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def _parcel(self):
        return self.coordinator.data.get(self._tracking_number, {})

class PostaStatusSensor(PostaBaseSensor):
    def __init__(self,coordinator,entry,tracking_number):
        super().__init__(coordinator,entry,tracking_number,)
        self._attr_unique_id = (f"{tracking_number}_status")
        self._attr_name = "Status"
        self._attr_icon = ("mdi:package-variant")

    @property
    def native_value(self):
        return self._parcel.get("status_text")

    @property
    def extra_state_attributes(self):
        return {
            "event_date": self._parcel.get("event_date"),
            "location": self._parcel.get("location"),
            "zip": self._parcel.get("zip"),
            "tracking_number": self._tracking_number,
        }

class PostaLocationSensor(PostaBaseSensor):
    def __init__(self,coordinator,entry,tracking_number,):
        super().__init__(coordinator,entry,tracking_number,)
        self._attr_unique_id = (f"{tracking_number}_location")
        self._attr_name = "Location"
        self._attr_icon = ("mdi:map-marker")

    @property
    def native_value(self):
        return self._parcel.get("location")

    @property
    def extra_state_attributes(self):
        return {
            "zip": self._parcel.get("zip"),
        }
