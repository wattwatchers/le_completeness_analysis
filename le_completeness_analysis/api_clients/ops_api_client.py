import json

from .rest_api_client import RestAPIClient, RestError


class OpsApiClient(RestAPIClient):

    def __init__(self, environment: str, api_key: str, requests_per_sec_max: int):
        match environment:
            case "production" | "prod":
                base_url = "https://api.ops.wattwatchers.net"
            case "staging":
                base_url = "https://stage.api.ops.wattwatchers.net"
            case _:
                # fallback is prod
                base_url = "https://api.ops.wattwatchers.net"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        # TODO: use a considered value for number of requests per second
        super().__init__(base_url, requests_per_sec_max, headers=headers)

    def get_available_firmware_versions(
        self,
        device_id: str,
        include_prerelease: bool = False,
        include_is_active_field: bool = False,
    ) -> tuple[list | None, RestError | None]:
        """
        Retrieves the available firmware versions for the device associated
        with the device_id
        """
        params = {"include-prerelease": include_prerelease}
        if include_is_active_field:
            params["fields"] = "is_active"

        result = super().get(f"devices/{device_id}/firmware/available", params=params)
        return result

    def get_current_firmware_version(
        self, device_id: str
    ) -> tuple[dict | None, RestError | None]:
        """
        Retrieves the currently installed firmware version for the device associated
        with the device_id
        """
        result = super().get(f"devices/{device_id}/firmware")
        return result

    def get_firmware_history(
        self, device_id: str
    ) -> tuple[dict | None, RestError | None]:
        """
        Retrieves the firmware history for the device associated with the device_id
        """
        result = super().get(f"devices/{device_id}/firmware-history")
        return result

    def request_firmware_update(
        self, device_id: str, desired_version: str
    ) -> tuple[dict | None, RestError | None]:
        """
        Patches the device status of the device associated with the device_id
        with the desired firmware version. This initiates an OTA firmware update.
        """
        payload = {"desiredVersion": desired_version}
        result = super().patch(
            f"devices/{device_id}/firmware", data=json.dumps(payload)
        )
        return result

    def get_server_messages(
        self, device_id: str
    ) -> tuple[dict | None, RestError | None]:
        """
        Retrieves the server messages queued for the device.
        """
        result = super().get(f"devices/{device_id}/server-messages")
        return result

    def get_device(self, device_id: str) -> tuple[dict | None, RestError | None]:
        """
        Retrieves the the device configuration.
        """
        result = super().get(f"devices/{device_id}")
        return result

    def get_latest_status(self, device_id: str) -> tuple[dict | None, RestError | None]:
        """
        Retrieves the latest available device status.
        """
        result = super().get(f"devices/{device_id}/status/latest")
        return result

    def get_status_history(
        self, device_id: str, timestamp_start: int | None, timestamp_end: int | None
    ) -> tuple[dict | None, RestError | None]:
        """
        Retrieves a time series of device statuses between timestamp_start and timestamp_end.
        """
        if timestamp_start is None and timestamp_end is None:
            return None, RestError(
                "You need to define at least one of the timestamp_start and timestamp_end params."
            )
        if (
            timestamp_start is not None
            and timestamp_end is not None
            and timestamp_start > timestamp_end
        ):
            return None, RestError("timestamp_start needs to be before timestamp_end")
        # TODO: batch for long time intervals
        params = {"fromTs": timestamp_start, "toTs": timestamp_end}
        result = super().get(f"devices/{device_id}/status", params=params)
        return result

    def get_latest_config_audit_log(
        self, device_id: str
    ) -> tuple[dict | None, RestError | None]:
        """
        Retrieves the latest available config audit log.
        """
        result = super().get(f"devices/{device_id}/config-logs/latest")
        return result

    def get_config_audit_log_history(
        self, device_id: str, timestamp_start: int | None, timestamp_end: int | None
    ) -> tuple[dict | None, RestError | None]:
        """
        Retrieves a time series of device statuses between timestamp_start and timestamp_end.
        """
        if timestamp_start is None and timestamp_end is None:
            return None, RestError(
                "You need to define at least one of the timestamp_start and timestamp_end params."
            )
        if (
            timestamp_start is not None
            and timestamp_end is not None
            and timestamp_start > timestamp_end
        ):
            return None, RestError("timestamp_start needs to be before timestamp_end")
        # TODO: batch for long time intervals
        params = {"fromTs": timestamp_start, "toTs": timestamp_end}
        result = super().get(f"devices/{device_id}/config-logs", params=params)
        return result

    def get_online_state_history_for_device(
        self,
        device_id: str,
        timestamp_start: int | None = None,
        timestamp_end: int | None = None,
        excl_source: bool = True,
    ) -> tuple[list | None, RestError | None]:
        params = {"exclSource": excl_source}
        if timestamp_start is not None:
            params["fromTs"] = timestamp_start
        if timestamp_end is not None:
            params["toTs"] = timestamp_end
        result = super().get(f"devices/{device_id}/comms/online-state", params=params)
        return result

    def get_online_state_history(
        self,
        devices: list | None = None,
        timestamp_end: int | None = None,
        timestamp_start: int | None = None,
        excl_source: bool = True,
    ) -> tuple[list | None, RestError | None]:
        params = {"exclSource": excl_source}
        if timestamp_start is not None:
            params["fromTs"] = timestamp_start
        if timestamp_end is not None:
            params["toTs"] = timestamp_end
        if devices is not None:
            params["devices"] = ",".join(devices)
        result = super().get("devices/comms/online-state", params=params)
        return result
