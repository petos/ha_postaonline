from __future__ import annotations

from datetime import datetime
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL

import re
import unicodedata

_LOGGER = logging.getLogger(__name__)


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


STATUS_NOW_DELIVERING = "now_delivering"
STATUS_RECEIVED_INFO = "received_info"
STATUS_PREPARING = "preparing_to_delivery"
STATUS_IN_TRANSIT = "in_transit"
STATUS_DELIVERED = "delivered"
STATUS_STORED_MISSED_DELIVERY = "stored_-_missed_delivery"
STATUS_UNKNOWN = "unknown"

STATUS_RULES = [
    (r"\bdorucovani", STATUS_NOW_DELIVERING),
    (r"\bdoruc(en|eno|ena)", STATUS_DELIVERED),
    (r"\bdodani\s+zasilky\b", STATUS_DELIVERED),
    (r"\bpriprav", STATUS_PREPARING),
    (r"\bpreprav", STATUS_IN_TRANSIT),
    (r"\bobdrzeny\s+udaje", STATUS_RECEIVED_INFO),
    (r"\bulozeni\s+zasilky\s+adresat\s+nezastizen\b", STATUS_STORED_MISSED_DELIVERY),
]

STATUS_PATTERNS = [
    (re.compile(pattern), value)
    for pattern, value in STATUS_RULES
]

class PostaStatusSensor(PostaBaseSensor):
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = [
        STATUS_NOW_DELIVERING,
        STATUS_PREPARING,
        STATUS_IN_TRANSIT,
        STATUS_DELIVERED,
        STATUS_STORED_MISSED_DELIVERY,
        STATUS_RECEIVED_INFO,
        STATUS_UNKNOWN,
    ]

    def __init__(self,coordinator,entry,tracking_number):
        super().__init__(coordinator,entry,tracking_number,)
        self._attr_unique_id = (f"{tracking_number}_status")
        self._attr_name = "Status"
        self._attr_icon = ("mdi:package-variant")

    @staticmethod
    def normalize_status(text: str) -> str:
        text = text.lower()
        # odstranění diakritiky
        text = "".join(
            c for c in unicodedata.normalize("NFD", text)
            if unicodedata.category(c) != "Mn"
        )
        # interpunkce -> mezera
        text = re.sub(r"[^\w\s]", " ", text)
        # vícenásobné mezery
        text = " ".join(text.split())
        return text

    @property
    def native_value(self):
        raw_status = self._parcel.get("status_text")
        if not raw_status:
            return STATUS_UNKNOWN
        normalized_status = self.normalize_status(raw_status.lower())
        _LOGGER.debug("Status: %s", normalized_status)

        for pattern, value in STATUS_PATTERNS:
            if pattern.search(normalized_status):
                _LOGGER.debug("Hit pattern: %s ;  Found status: %s", pattern, value)
                return value
        return STATUS_UNKNOWN

    @property
    def extra_state_attributes(self):
        return {
            "event_date": self._parcel.get("event_date"),
            "location": self._parcel.get("location"),
            "zip": self._parcel.get("zip"),
            "tracking_number": self._tracking_number,
        }

    @property
    def extra_state_attributes(self):
        return {
            "raw_status": self._parcel.get("status_text"),
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
