from dataclasses import dataclass
from enum import Enum
import json
import logging

from .rest_api_client import RestAPIClient, RestError


@dataclass
class TimeInterval:
    """
    Data class for a time interval
    """

    timestamp_start: int
    timestamp_end: int


class Granularity(Enum):
    """
    Enum for different LE granularities
    """

    FIVE_MINS = "5m"
    FIFTEEN_MINS = "15m"
    THIRTY_MINS = "30m"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class CallerError(Exception):
    """
    Error by caller of the client.
    """


class PublicApiClient(RestAPIClient):

    def __init__(
        self,
        environment: str,
        api_key: str,
        requests_per_sec_max: int,
        logger: logging.Logger,
    ):
        match environment:
            case "production" | "prod":
                base_url = "https://api-v3.wattwatchers.com.au"
            case "staging":
                base_url = "https://api-v3-stage.wattwatchers.com.au"
            case _:
                # fallback is prod
                base_url = "https://api-v3.wattwatchers.com.au"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        # TODO: use a considered value for number of requests per second
        super().__init__(base_url, requests_per_sec_max, headers=headers)
        self._logger = logger

    def get_devices_list(self) -> tuple[list | None, RestError | None]:
        """
        Retrieves all device ids associated with the API key
        """
        result = super().get("devices")
        return result

    def get_device_status(self, device_id: str) -> tuple[dict | None, RestError | None]:
        """
        Retrieves the status of the device associated with the device_id
        """
        result = super().get(f"devices/{device_id}")
        return result

    def patch_device_status(
        self, device_id: str, payload: dict
    ) -> tuple[dict | None, RestError | None]:
        """
        Patches the device status of the device associated with the device_id
        Used (among other things) to update WiFi credentials
        """
        result = super().patch(f"devices/{device_id}", data=json.dumps(payload))
        return result

    def update_wifi_credentials(
        self, device_id: str, ssid: str | None = None, psk: str | None = None
    ) -> tuple[dict | None, RestError | None]:
        """
        Updates the WiFi credentials of the device associated with the device_id
        If successful, this will cause the device to switch to WiFi comms.
        """
        if ssid is None and psk is None:
            # No credential details provided, return error
            return (
                None,
                CallerError(
                    "Request to update WiFi credentials requires at least one of SSID and PSK to be defined."
                ),
            )

        payload = {"comms": {"wifi": {}}}
        if not (ssid is None):
            payload["comms"]["wifi"]["ssid"] = ssid
        if not (psk is None):
            payload["comms"]["wifi"]["psk"] = psk

        return self.patch_device_status(device_id, payload)

    def reset_wifi_credentials(
        self, device_id: str
    ) -> tuple[dict | None, RestError | None]:
        """
        Resets the WiFi credentials of the device associated with the device_id
        This will cause the device to switch to cellular comms.
        """
        return self.update_wifi_credentials(device_id, "", "")

    def change_switch_state(
        self, device_id: str, switch_id: str, target_state: str
    ) -> tuple[dict | None, RestError | None]:
        """
        Changes the switch state of the switch with id `switch_id` on the device with
        id `device_id` to state `target_state`.
        """
        payload = {
            "id": device_id,
            "switches": [{"id": switch_id, "state": target_state}],
        }
        return self.patch_device_status(device_id, payload)

    def update_se_reporting_interval(
        self, device_id: str, reporting_interval: int
    ) -> tuple[dict | None, RestError | None]:
        """
        Update the SE reporting interval for the device to the requested value
        """
        payload = {"shortEnergyReportingInterval": reporting_interval}
        return super().post(
            f"devices/{device_id}/reporting-interval", data=json.dumps(payload)
        )

    def get_latest_se(
        self, device_id: str, energy_unit: str | None = "kW"
    ) -> tuple[dict | None, RestError | None]:
        if energy_unit is not None and energy_unit in ["kW", "kWh"]:
            params = {"convert[energy]": energy_unit}
            return super().get(f"/short-energy/{device_id}/latest", params=params)
        return super().get(f"/short-energy/{device_id}/latest")

    def _max_interval_for_granularity(self, granularity: Granularity) -> int:
        """
        Returns the maximum interval for a single energy request based on the granularity
        """
        MAX_INTERVALS_DAYS = {
            Granularity.FIVE_MINS: 7,
            Granularity.FIFTEEN_MINS: 14,
            Granularity.THIRTY_MINS: 31,
            Granularity.HOUR: 90,
            Granularity.DAY: 3 * 365,  # ≈ 3 years
            Granularity.WEEK: 5 * 365,  # ≈ 5 years
            Granularity.MONTH: 10 * 365,  # ≈ 10 yers
        }
        return MAX_INTERVALS_DAYS.get(granularity, 7) * 24 * 3600

    def _calculate_intervals_for(
        self, granularity: Granularity, timestamp_start: int, timestamp_end: int
    ) -> list[tuple[int, int]]:
        """
        Batches an interval based on the maximum interval per request for the given granularity.
        """
        batch_interval = self._max_interval_for_granularity(granularity)
        intervals = [
            TimeInterval(batch_start, min(batch_start + batch_interval, timestamp_end))
            for batch_start in range(timestamp_start, timestamp_end, batch_interval)
        ]
        return intervals

    def _load_energy(
        self,
        endpoint: str,
        device_id: str,
        intervals: list[TimeInterval],
        unit: str = "kWh",
        granularity: Granularity | None = None,
    ) -> tuple[list | None, RestError | None]:

        energy_data = []
        for interval in intervals:
            params = {
                "fromTs": interval.timestamp_start,
                "toTs": interval.timestamp_end,
                "convert[energy]": unit,
            }
            if granularity is not None:
                params["granularity"] = granularity.value

            self._logger.info(
                f"load from {interval.timestamp_start} to {interval.timestamp_end} for {device_id}"
            )
            (result, error) = super().get(endpoint, params=params)
            if error is not None:
                self._logger.error(
                    f"Error retrieving LE data for {device_id} between {interval.timestamp_start} and {interval.timestamp_end}: {error}"
                )
                return (None, error)

            energy_data.extend(result)

        return (energy_data, None)

    def load_long_energy(
        self,
        device_id: str,
        timestamp_start: int,
        timestamp_end: int,
        granularity: Granularity = Granularity.FIVE_MINS,
        unit: str = "kWh",
    ) -> tuple[list | None, RestError | None]:

        intervals = self._calculate_intervals_for(
            granularity, timestamp_start, timestamp_end
        )
        return self._load_energy(
            f"/long-energy/{device_id}", device_id, intervals, unit, granularity
        )

    def get_first_le(self, device_id: str) -> tuple[list | None, RestError | None]:
        result = super().get(f"long-energy/{device_id}/first")
        return result

    def load_short_energy(
        self,
        device_id: str,
        timestamp_start: int,
        timestamp_end: int,
        unit: str = "kWh",
    ) -> tuple[list | None, RestError | None]:

        max_interval = 12 * 3600  # maximum request interval for SE is 12 hours
        intervals = [
            TimeInterval(batch_start, min(batch_start + max_interval, timestamp_end))
            for batch_start in range(timestamp_start, timestamp_end, max_interval)
        ]
        return self._load_energy(
            f"/short-energy/{device_id}", device_id, intervals, unit
        )
