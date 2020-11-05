#!/usr/bin/python
# -*- coding: utf-8 -*-
from cloudshell.devices.flows.action_flows import RestoreConfigurationFlow
from cloudshell.checkpoint.gaia.command_actions.file_fransfer_actions import FileTransferActions
from cloudshell.checkpoint.gaia.command_actions.save_restore_actions import SaveRestoreActions


class CheckpointRestoreFlow(RestoreConfigurationFlow):

    def __init__(self, cli_handler, logger):
        super(CheckpointRestoreFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, path, configuration_type, restore_method, vrf_management_name):
        """ Execute flow which save selected file to the provided destination

        :param path: the path to the configuration file, including the configuration file name
        :param restore_method: the restore method to use when restoring the configuration file.
                               Possible Values are append and override
        :param configuration_type: the configuration type to restore. Possible values are startup and running
        :param vrf_management_name: Virtual Routing and Forwarding Name
        """

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as cli_service:
            save_restore_actions = SaveRestoreActions(cli_service, self._logger)
            file_transfer_actions = FileTransferActions(cli_service, self._logger)

            url_obj = FileTransferActions.get_url_obj(path)

            if url_obj.scheme != url_obj.SCHEME.LOCAL:
                with cli_service.enter_mode(self._cli_handler.config_mode):
                    file_transfer_actions.download(path, url_obj.filename)

            # restore local
            save_restore_actions.restore(url_obj.filename)

            # remove local file
            if url_obj.scheme != url_obj.SCHEME.LOCAL:
                with cli_service.enter_mode(self._cli_handler.config_mode):
                    save_restore_actions.remove_local_file(url_obj.filename)
