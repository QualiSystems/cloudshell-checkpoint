#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.shell.flows.configuration.basic_flow import AbstractConfigurationFlow

from cloudshell.checkpoint.gaia.command_actions.file_fransfer_actions import (
    FileTransferActions,
    Url,
)
from cloudshell.checkpoint.gaia.command_actions.save_restore_actions import (
    SaveRestoreActions,
)


class CheckpointConfigurationFlow(AbstractConfigurationFlow):
    def __init__(self, logger, resource_config, cli_configurator):
        super(CheckpointConfigurationFlow, self).__init__(logger, resource_config)
        self._cli_configurator = cli_configurator

    def _save_flow(self, folder_path, configuration_type, vrf_management_name):
        with self._cli_configurator.enable_mode_service() as cli_service:
            save_restore_actions = SaveRestoreActions(cli_service, self._logger)
            file_transfer_actions = FileTransferActions(cli_service, self._logger)

            url_obj = Url.get_url_obj(folder_path)

            # save config to local fs
            save_restore_actions.save_local(url_obj.filename)

            if url_obj.scheme == self._file_system:
                return

            with cli_service.enter_mode(self._cli_configurator.config_mode):
                # Transfer config to remote
                try:
                    file_transfer_actions.upload(url_obj.filename, folder_path)
                finally:
                    # remove local file
                    save_restore_actions.remove_local_file(url_obj.filename)

    def _restore_flow(
        self, path, configuration_type, restore_method, vrf_management_name
    ):
        with self._cli_configurator.enable_mode_service() as cli_service:
            save_restore_actions = SaveRestoreActions(cli_service, self._logger)
            file_transfer_actions = FileTransferActions(cli_service, self._logger)

            url_obj = Url.get_url_obj(path)

            if url_obj.scheme != url_obj.SCHEME.LOCAL:
                with cli_service.enter_mode(self._cli_configurator.config_mode):
                    file_transfer_actions.download(path, url_obj.filename)

            # restore local
            save_restore_actions.restore(url_obj.filename)

            # remove local file
            if url_obj.scheme != url_obj.SCHEME.LOCAL:
                with cli_service.enter_mode(self._cli_configurator.config_mode):
                    save_restore_actions.remove_local_file(url_obj.filename)

    @property
    def _file_system(self):
        return Url.SCHEME.LOCAL
