from cloudshell.shell.flows.state.basic_flow import StateFlow


class ShutdownOkException(Exception):
    pass


class CheckpointStateFlow(StateFlow):
    def shutdown(self):
        def exit_with_exception(session, logger):
            raise ShutdownOkException()

        with self._cli_configurator.config_mode_service() as cli_service:
            try:
                return cli_service.send_command(
                    "shutdown -h now",
                    action_map={r"system is going down": exit_with_exception},
                )
            except ShutdownOkException:
                return "Shutdown process is running"
