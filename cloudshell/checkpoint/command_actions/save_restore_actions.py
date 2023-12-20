from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)

from cloudshell.checkpoint.command_templates import save_restore_templates

if TYPE_CHECKING:
    from cloudshell.cli.service.cli_service import CliService


@define
class SaveRestoreActions:
    _cli_service: CliService

    def save_local(
        self, filename: str, action_map: dict = None, error_map: dict = None
    ) -> str:
        """Save configuration to local file."""
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=save_restore_templates.SAVE_CONFIGURATION,
            action_map=action_map,
            error_map=error_map,
            timeout=300,
        ).execute_command(filename=filename)

    def remove_local_file(self, filepath: str) -> str:
        """Remove local file."""
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=save_restore_templates.REMOVE,
        ).execute_command(filename=filepath)

    def restore(self, filepath: str) -> str:
        """Restore configuration from local file."""
        out = ""
        out += CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=save_restore_templates.ON_FAILURE_CONTINUE,
        ).execute_command()

        out += CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=save_restore_templates.LOAD_CONFIGURATION,
            timeout=300,
        ).execute_command(filename=filepath)

        out += CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=save_restore_templates.ON_FAILURE_STOP,
        ).execute_command()

        out += CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=save_restore_templates.SAVE_CONFIG,
        ).execute_command()

        return out
