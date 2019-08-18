#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from cloudshell.devices.flows.action_flows import LoadFirmwareFlow
from cloudshell.devices.networking_utils import UrlParser


class CheckpointLoadFirmwareFlow(LoadFirmwareFlow):
    def __init__(self, cli_handler, logger):
        super(CheckpointLoadFirmwareFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, path, vrf, timeout):
        """Load a firmware onto the device

        :param path: The path to the firmware file, including the firmware file name
        :param vrf: Virtual Routing and Forwarding Name
        :param timeout:
        :return:
        """

        pass
