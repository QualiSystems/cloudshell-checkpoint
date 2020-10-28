#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
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

            local_file = datetime.datetime.now().strftime("%Y%m%d%H%M%S-remote.conf")

            with cli_service.enter_mode(self._cli_handler.config_mode):
                # Transfer config from remote
                file_transfer_actions = FileTransferActions(cli_service, self._logger)
                if path.startswith("scp"):
                    transfer_func = file_transfer_actions.scp_download
                elif path.startswith("ftp"):
                    transfer_func = file_transfer_actions.ftp_download
                elif path.startswith("tftp"):
                    transfer_func = file_transfer_actions.tftp_download
                else:
                    raise Exception("Url is not correct.")

                transfer_func(path, local_file)

            # restore local
            save_restore_actions.restore(local_file)

            # remove local file
            with cli_service.enter_mode(self._cli_handler.config_mode):
                save_restore_actions.remove_local_file(local_file)
