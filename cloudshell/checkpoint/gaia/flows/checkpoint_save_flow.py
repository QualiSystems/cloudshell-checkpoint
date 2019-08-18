#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.flows.action_flows import SaveConfigurationFlow


class CheckpointSaveFlow(SaveConfigurationFlow):
    def __init__(self, cli_handler, logger):
        super(CheckpointSaveFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, folder_path, configuration_type, vrf_management_name=None):
        """ Execute flow which save selected file to the provided destination

        :param folder_path: destination path where file will be saved
        :param configuration_type: source file, which will be saved
        :param vrf_management_name: Virtual Routing and Forwarding Name
        :return: saved configuration file name
        """

        pass
