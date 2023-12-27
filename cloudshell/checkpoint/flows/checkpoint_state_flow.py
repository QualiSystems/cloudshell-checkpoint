from __future__ import annotations

from cloudshell.shell.flows.state.basic_flow import StateFlow

from cloudshell.checkpoint.command_actions.system_actions import SystemActions


class CheckpointStateFlow(StateFlow):
    def shutdown(self) -> str:
        with self._cli_configurator.config_mode_service() as config_cli_service:
            system_actions = SystemActions(config_cli_service)
            return system_actions.shutdown()
