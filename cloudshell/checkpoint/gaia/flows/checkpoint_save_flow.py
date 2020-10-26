#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.flows.action_flows import SaveConfigurationFlow
from cloudshell.devices.networking_utils import UrlParser

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
            url = UrlParser.parse_url(folder_path)
            scheme = url.get(UrlParser.SCHEME)
            if scheme.lower() != "scp":
                raise Exception("SCP only supported")
            filename = url.get(UrlParser.FILENAME)

            # save config to local fs
            save_restore_actions.save_local(filename)

            password = url.get(UrlParser.PASSWORD)
            scp_target = "{user}@{hostname}:{filepath}/{filename}".format(
                user=url.get(UrlParser.USERNAME),
                hostname=url.get(UrlParser.HOSTNAME),
                filepath=url.get(UrlParser.PATH),
                filename=filename)

            with cli_service.enter_mode(self._cli_handler.config_mode):
                # transfer to remote by scp
                save_restore_actions.scp_transfer(filename, scp_target, password)
                # remove local file
                save_restore_actions.remove_local_file(filename)
