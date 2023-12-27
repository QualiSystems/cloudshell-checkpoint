from __future__ import annotations

from cloudshell.cli.command_template.command_template import CommandTemplate

from cloudshell.checkpoint.helpers.errors import ShutdownOkCheckpointError

SCP_ERROR_MAP = {
    "[Nn]o such file or directory": "No such file or directory.",
    "[Nn]ame or service not known": "Name or service not known",
    "[Nn]etwork is unreachable": "Network is unreachable",
    "[Pp]ermission denied": "Permission denied",
}

FTP_ERROR_MAP = {r"Could not create file": "FTP: Could not create file."}


SCP_COPY = CommandTemplate(
    command="scp -P {scp_port} {src_location} {dst_location}", error_map=SCP_ERROR_MAP
)
FTP_UPLOAD = CommandTemplate(
    command="put {src_location} {dst_location}", error_map=FTP_ERROR_MAP
)
FTP_DOWNLOAD = CommandTemplate(
    command="get {src_location} {dst_location}", error_map=FTP_ERROR_MAP
)

SHUTDOWN = CommandTemplate(
    command="shutdown -h now",
    action_map={
        r"system is going down": lambda: (_ for _ in ()).throw(
            ShutdownOkCheckpointError()
        )
    },
)
