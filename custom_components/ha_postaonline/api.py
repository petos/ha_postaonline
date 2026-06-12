import logging

from aiohttp import ClientTimeout
from bs4 import BeautifulSoup

from .const import BASE_URL
from .exceptions import ParcelNotFound

_LOGGER = logging.getLogger(__name__)



class PostaOnlineApi:
    def __init__(self, session):
        self._session = session

        self._headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

    async def fetch(self, tracking_number: str):
        url = BASE_URL.format(
            tracking_number=tracking_number,
        )

        _LOGGER.debug("Fetching %s", url)
        html = await self._get(url)

        data = self._parse(html)

        return data

    def _parse(self, html: str):
        soup = BeautifulSoup(html, "html.parser")

        page_text = soup.get_text(" ", strip=True)

        if "není v evidenci" in page_text:
            raise ParcelNotFound()

        table = soup.find("table", id="parcelInfo")

        if not table:
            raise RuntimeError("Tracking table not found")

        rows = table.find_all("tr")
        if len(rows) < 2:
            raise RuntimeError("Tracking table is empty")

        first_row = table.find("tbody")

        cols = first_row.find_all("td")
        info_col = None
        for col in cols:
            if col.find("a", class_="parcHref"):
                info_col = col
                break

        if info_col is None:
            raise RuntimeError("Parcel info column not found")
        info_idx = cols.index(info_col)

        tracking_number = cols[info_idx].find("a", class_="parcHref").get_text(strip=True)
        status_text = cols[info_idx].get_text(" ", strip=True).replace(tracking_number, "", 1).strip()
        event_date = cols[info_idx+1].get_text(strip=True)
        zip_code = cols[info_idx+2].get_text(strip=True)
        location = cols[info_idx+3].get_text(strip=True)

        return {
            "status_text": status_text,
            "event_date": event_date,
            "zip": zip_code,
            "location": location,
            "tracking_number": tracking_number,
        }

    async def _get(self, url: str) -> str:
        timeout = ClientTimeout(total=10)

        async with self._session.get(
            url,
            headers=self._headers,
            timeout=timeout,
        ) as resp:
            resp.raise_for_status()

            return await resp.text()
