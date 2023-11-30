from __future__ import annotations

from typing import TYPE_CHECKING

from cloudshell.shell.flows.firmware.basic_flow import AbstractFirmwareFlow
from cloudshell.checkpoint.gaia.helpers.errors import NotImplementedCheckpointError


if TYPE_CHECKING:
    from typing import Union

    from cloudshell.shell.flows.utils.url import BasicLocalUrl, RemoteURL
    from cloudshell.shell.standards.firewall.resource_config import (
        FirewallResourceConfig,
    )

    from ..cli.checkpoint_cli_configurator import CheckpointCliConfigurator

    Url = Union[RemoteURL, BasicLocalUrl]


class CheckpointFirmwareFlow(AbstractFirmwareFlow):
    def __init__(
        self,
        resource_config: FirewallResourceConfig,
        cli_configurator: CheckpointCliConfigurator,
    ):
        super().__init__(resource_config)
        self.cli_configurator = cli_configurator

    def _load_firmware_flow(
        self,
        firmware_url: Url,
        vrf_management_name: str | None,
        timeout: int,
    ) -> None:
        """Load firmware."""
        raise NotImplementedCheckpointError("Load firmware is not implemented.")
