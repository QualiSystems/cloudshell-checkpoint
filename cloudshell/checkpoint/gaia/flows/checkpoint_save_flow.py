#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

from cloudshell.devices.flows.action_flows import SaveConfigurationFlow

from cloudshell.checkpoint.gaia.command_actions.file_fransfer_actions import FileTransferActions
from cloudshell.checkpoint.gaia.command_actions.save_restore_actions import SaveRestoreActions


class CheckpointSaveFlow(SaveConfigurationFlow):
    def __init__(self, cli_handler, logger):
        super(CheckpointSaveFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, folder_path, configuration_type, vrf_management_name=None):
        """ Execute flow which save selected file to the provided destination

        :param str folder_path: destination path where file will be saved
        :param configuration_type: source file, which will be saved
        :param vrf_management_name: Virtual Routing and Forwarding Name
        :return: saved configuration file name
        """

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as cli_service:
            save_restore_actions = SaveRestoreActions(cli_service, self._logger)
            local_file = datetime.datetime.now().strftime("%Y%m%d%H%M%S-local.conf")

            # save config to local fs
            save_restore_actions.save_local(local_file)

            with cli_service.enter_mode(self._cli_handler.config_mode):
                # Transfer config to remote
                file_transfer_actions = FileTransferActions(cli_service, self._logger)
                if folder_path.startswith("scp"):
                    transfer_func = file_transfer_actions.scp_upload
                elif folder_path.startswith("ftp"):
                    transfer_func = file_transfer_actions.ftp_upload
                elif folder_path.startswith("tftp"):
                    transfer_func = file_transfer_actions.tftp_upload
                else:
                    raise Exception("Url is not correct.")

                try:
                    transfer_func(local_file, folder_path)
                finally:
                    # remove local file
                    save_restore_actions.remove_local_file(local_file)
