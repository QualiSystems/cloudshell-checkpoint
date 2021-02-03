#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.shell.flows.firmware.basic_flow import AbstractFirmwareFlow


class CheckpointLoadFirmwareFlow(AbstractFirmwareFlow):
    def _load_firmware_flow(self, path, vrf_management_name, timeout):
        raise NotImplementedError("Load firmware is not implemented")
