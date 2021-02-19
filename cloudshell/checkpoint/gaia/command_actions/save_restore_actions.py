from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)

import cloudshell.checkpoint.gaia.command_templates.save_restore_templates as command_templates  # noqa: E501


class SaveRestoreActions(object):
    def __init__(self, cli_service, logger):
        """Save restore actions.

        :param cli_service: config mode cli service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    def save_local(self, filename, action_map=None, error_map=None):
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=command_templates.SAVE_CONFIGURATION,
            action_map=action_map,
            error_map=error_map,
            timeout=300,
        ).execute_command(filename=filename)

    def remove_local_file(self, filepath):
        return CommandTemplateExecutor(
            cli_service=self._cli_service, command_template=command_templates.REMOVE
        ).execute_command(filename=filepath)

    def restore(self, filepath):
        out = ""
        out += CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=command_templates.ON_FAILURE_CONTINUE,
        ).execute_command()
        out += CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=command_templates.LOAD_CONFIGURATION,
            timeout=300,
        ).execute_command(filename=filepath)
        out += CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=command_templates.ON_FAILURE_STOP,
        ).execute_command()
        out += CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=command_templates.SAVE_CONFIG,
        ).execute_command()

        return out
