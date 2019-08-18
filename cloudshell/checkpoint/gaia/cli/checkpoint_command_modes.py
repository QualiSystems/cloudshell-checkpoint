#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import OrderedDict

from cloudshell.cli.command_mode import CommandMode


class DefaultCommandMode(CommandMode):
    PROMPT = r'(?:(?!\)).)#\s*$'
    ENTER_COMMAND = ''
    EXIT_COMMAND = ''

    def __init__(self):
        """
        Initialize Default command mode, only for cases when session started not in enable mode

        :param context:
        """

        CommandMode.__init__(self,
                             DefaultCommandMode.PROMPT,
                             DefaultCommandMode.ENTER_COMMAND,
                             DefaultCommandMode.EXIT_COMMAND)


class EnableCommandMode(CommandMode):
    PROMPT = r'>\s*$'
    ENTER_COMMAND = 'clish'
    EXIT_COMMAND = ''

    def __init__(self):
        """
        Initialize Enable command mode - default command mode for Cisco Shells

        :param context:
        """

        CommandMode.__init__(self,
                             EnableCommandMode.PROMPT,
                             EnableCommandMode.ENTER_COMMAND,
                             EnableCommandMode.EXIT_COMMAND)


CommandMode.RELATIONS_DICT = {
    DefaultCommandMode: {
        EnableCommandMode: {}
    }
}
