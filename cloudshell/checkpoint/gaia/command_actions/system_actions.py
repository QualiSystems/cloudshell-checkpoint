#!/usr/bin/python
# -*- coding: utf-8 -*-


class SystemActions(object):
    def __init__(self, cli_service, logger):
        """Reboot actions.

        :param cli_service: default mode cli_service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger
