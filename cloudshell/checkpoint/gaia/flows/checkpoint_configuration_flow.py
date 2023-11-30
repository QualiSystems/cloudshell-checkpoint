from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from cloudshell.shell.flows.configuration.basic_flow import (
    AbstractConfigurationFlow,
    ConfigurationType,
    RestoreMethod,
)

from cloudshell.checkpoint.gaia.command_actions.save_restore_actions import (
    SaveRestoreActions,
)
from cloudshell.checkpoint.gaia.command_actions.system_actions import SystemActions

if TYPE_CHECKING:
    from typing import Union

    from cloudshell.shell.flows.utils.url import BasicLocalUrl, RemoteURL
    from cloudshell.shell.standards.firewall.resource_config import (
        FirewallResourceConfig,
    )

    from ..cli.checkpoint_cli_configurator import CheckpointCliConfigurator

    Url = Union[RemoteURL, BasicLocalUrl]


logger = logging.getLogger(__name__)


class CheckpointConfigurationFlow(AbstractConfigurationFlow):
    def __init__(
        self,
        resource_config: FirewallResourceConfig,
        cli_configurator: CheckpointCliConfigurator,
    ):
        super().__init__(resource_config)
        self.cli_configurator = cli_configurator

    @property
    def file_system(self) -> str:
        return "local"

    def _save_flow(
        self,
        file_dst_url: Url,
        configuration_type: ConfigurationType,
        vrf_management_name: str | None,
    ) -> None:
        """Backup config.

        Backup 'startup-config' or 'running-config' from
        device to provided file_system [ftp|tftp].
        Also possible to backup config to localhost
        :param file_dst_url: destination url, remote or local, where file will be saved
        :param configuration_type: type of configuration
        that will be saved (StartUp or Running)
        :param vrf_management_name: Virtual Routing and
        Forwarding management name
        """
        with self.cli_configurator.enable_mode_service() as enable_cli_service:
            save_restore_actions = SaveRestoreActions(enable_cli_service)
            system_actions = SystemActions(enable_cli_service)

            # save config to local fs
            save_restore_actions.save_local(file_dst_url.filename)

            if file_dst_url.scheme != self.file_system:
                with enable_cli_service.enter_mode(self.cli_configurator.config_mode):
                    # Transfer config to remote
                    try:
                        system_actions.upload(file_dst_url)
                    finally:
                        # remove local file
                        save_restore_actions.remove_local_file(file_dst_url.filename)

    def _restore_flow(
        self,
        config_path: Url,
        configuration_type: ConfigurationType,
        restore_method: RestoreMethod,
        vrf_management_name: str | None,
    ) -> None:
        """Restore configuration on device from provided configuration file.

        Restore configuration from local file system or ftp/tftp
        server into 'running-config' or 'startup-config'.
        :param config_path: relative path to the file on the
        remote host tftp://server/sourcefile
        :param configuration_type: the configuration
        type to restore (StartUp or Running)
        :param restore_method: override current config or not
        :param vrf_management_name: Virtual Routing and
        Forwarding management name
        """
        with self.cli_configurator.enable_mode_service() as enable_cli_service:
            save_restore_actions = SaveRestoreActions(enable_cli_service)
            system_actions = SystemActions(enable_cli_service)

            if config_path.scheme != self.file_system:
                with enable_cli_service.enter_mode(self.cli_configurator.config_mode):
                    system_actions.download(config_path)

            # restore local
            save_restore_actions.restore(config_path.filename)

            # remove local file
            if config_path.scheme != self.file_system:
                with enable_cli_service.enter_mode(self.cli_configurator.config_mode):
                    save_restore_actions.remove_local_file(config_path.filename)
