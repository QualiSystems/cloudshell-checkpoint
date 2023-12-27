from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from attrs import define

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.cli.service.command_mode import CommandMode

from cloudshell.checkpoint.command_templates import system_templates
from cloudshell.checkpoint.helpers.errors import (
    NotSupportedCheckpointError,
    ShutdownOkCheckpointError,
)

if TYPE_CHECKING:
    from cloudshell.cli.service.cli_service import CliService
    from cloudshell.shell.flows.utils.url import RemoteURL

logger = logging.getLogger(__name__)


@define
class SystemActions:
    _cli_service: CliService

    def shutdown(self):
        """Shutdown the system."""
        try:
            return CommandTemplateExecutor(
                self._cli_service, system_templates.SHUTDOWN
            ).execute_command()
        except ShutdownOkCheckpointError:
            return "Shutdown process is running"

    def _get_transfer_obj(self, protocol: str):
        """Determine transfer protocol."""
        protocol_mapping = {
            "scp": ScpFileTransfer,
            "ftp": FtpFileTransfer,
        }
        try:
            transfer_class = protocol_mapping[protocol]
        except KeyError:
            raise NotSupportedCheckpointError(f"Protocol {protocol} is not supported.")

        return transfer_class(self._cli_service)

    def upload(self, remote_url: RemoteURL):
        """Upload file to remote storage."""
        transfer_obj = self._get_transfer_obj(remote_url.scheme)
        return transfer_obj.upload(remote_url)

    def download(self, remote_url: RemoteURL):
        """Download file from remote storage."""
        transfer_obj = self._get_transfer_obj(remote_url.scheme)
        return transfer_obj.download(remote_url)


@define
class ScpFileTransfer:
    _cli_service: CliService

    def upload(self, remote_url: RemoteURL):
        """Upload file to remote SCP server."""
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=system_templates.SCP_COPY,
            action_map=self._action_map(remote_url=remote_url),
        ).execute_command(
            scp_port=remote_url.port or "22",
            src_location=remote_url.filename,
            dst_location=self._get_scp_endpoint(remote_url=remote_url),
        )

    def download(self, remote_url: RemoteURL):
        """Download file from remote SCP server."""
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=system_templates.SCP_COPY,
            action_map=self._action_map(remote_url=remote_url),
        ).execute_command(
            scp_port=remote_url.port or "22",
            src_location=self._get_scp_endpoint(remote_url=remote_url),
            dst_location=remote_url.filename,
        )

    @staticmethod
    def _action_map(remote_url: RemoteURL) -> dict:
        return {
            r"[Pp]assword:": lambda s, l: s.send_line(remote_url.password, l),
            r"\(yes\/no\)\?": lambda s, l: s.send_line("yes", l),
        }

    @staticmethod
    def _get_scp_endpoint(remote_url: RemoteURL) -> str:
        return f"{remote_url.username}@{remote_url.host}:{remote_url.path}"


@define
class FtpFileTransfer:
    _cli_service: CliService

    def upload(self, remote_url: RemoteURL):
        """Upload file to remote FTP server."""
        ftp_command_mode = self._get_ftp_command_mode(remote_url=remote_url)
        try:
            with self._cli_service.enter_mode(ftp_command_mode):
                return CommandTemplateExecutor(
                    cli_service=self._cli_service,
                    command_template=system_templates.FTP_UPLOAD,
                ).execute_command(
                    src_location=remote_url.filename,
                    dst_location=remote_url.path,
                )
        finally:
            if self._cli_service.command_mode == ftp_command_mode:
                ftp_command_mode.step_down(self._cli_service, logger)

    def download(self, remote_url: RemoteURL):
        """Download file from remote FTP server."""
        ftp_command_mode = self._get_ftp_command_mode(remote_url=remote_url)
        try:
            with self._cli_service.enter_mode(ftp_command_mode):
                return CommandTemplateExecutor(
                    cli_service=self._cli_service,
                    command_template=system_templates.FTP_DOWNLOAD,
                ).execute_command(
                    src_location=remote_url.path,
                    dst_location=remote_url.filename,
                )
        finally:
            if self._cli_service.command_mode == ftp_command_mode:
                ftp_command_mode.step_down(self._cli_service, logger)

    @staticmethod
    def _get_ftp_command_mode(remote_url: RemoteURL) -> CommandMode:
        return CommandMode(
            r"ftp>",
            enter_command=f"ftp {remote_url.host} {remote_url.port or '21'}",
            exit_command="exit",
            enter_action_map={
                r"[Nn]ame|[Uu]sername|[Ll]ogin.*:": lambda s, l: s.send_line(
                    remote_url.username, l
                ),
                r"[Pp]assword.*:": lambda s, l: s.send_line(remote_url.password, l),
            },
            enter_error_map={
                r"[Ll]ogin incorrect|failed": "Login or Password is not correct.",
                r"[Cc]onnection timed out|[Nn]ot connected": "Cannot connect to ftp host.",  # noqa E501
            },
        )
