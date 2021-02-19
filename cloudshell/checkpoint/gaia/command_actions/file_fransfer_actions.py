from collections import OrderedDict
from functools import lru_cache

from cloudshell.cli.command_template.command_template import CommandTemplate
from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.cli.service.command_mode import CommandMode
from cloudshell.shell.flows.utils.networking_utils import UrlParser


class Url:
    class SCHEME:
        FTP = "ftp"
        SCP = "scp"
        LOCAL = "local"
        TFTP = "tftp"

    def __init__(self, url):
        self._url_object = UrlParser.parse_url(url)

    @staticmethod
    @lru_cache()
    def get_url_obj(url):
        return Url(url)

    @property
    def scheme(self):
        return self._url_object.get(UrlParser.SCHEME)

    @property
    def netloc(self):
        return self._url_object.get(UrlParser.NETLOC)

    @property
    def path(self):
        return self._url_object.get(UrlParser.PATH)

    @property
    def filename(self):
        return self._url_object.get(UrlParser.FILENAME)

    @property
    def username(self):
        return self._url_object.get(UrlParser.USERNAME)

    @property
    def password(self):
        return self._url_object.get(UrlParser.PASSWORD)

    @property
    def hostname(self):
        return self._url_object.get(UrlParser.HOSTNAME)

    @property
    def port(self):
        return self._url_object.get(UrlParser.PORT)

    def get_scp_endpoint(self):
        return "{username}@{hostname}:{path}/{filename}".format(**self._url_object)

    def get_ftp_path(self):
        path = self.path
        if path and path.startswith("/"):
            path = path[1:]
        return "{}/{}".format(path, self.filename) if path else self.filename


class FileTransferActions(object):
    def __init__(self, cli_service, logger):
        """Transfer file actions init.

        :param cloudshell.cli.cli_service.CliServiceImpl cli_service:
            config mode cli service
        :param logger:
        """
        self._cli_service = cli_service
        self._logger = logger

    def upload(self, filepath, remote_url):
        scheme = Url.get_url_obj(remote_url).scheme
        upload_method = getattr(self, "{}_{}".format(scheme, "upload"))
        if not upload_method:
            raise Exception("Upload protocol {} is not supported".format(scheme))
        return upload_method(filepath, remote_url)

    def download(self, remote_url, filepath):
        scheme = Url.get_url_obj(remote_url).scheme
        download_method = getattr(self, "{}_{}".format(scheme, "download"))
        if not download_method:
            raise Exception("Download protocol {} is not supported".format(scheme))
        return download_method(remote_url, filepath)

    def _run_scp_template(
        self, url_obj, command_template, action_map=None, error_map=None, **kwargs
    ):
        """Run scp template.

        :param Url url_obj:
        :param cloudshell.cli.command_template.command_template.
            CommandTemplate command_template:
        :param action_map:
        :param error_map:
        :param kwargs:
        """
        scp_actions = OrderedDict(
            [
                (r"[Pp]assword:", lambda s, l: s.send_line(url_obj.password, l)),
                (r"\(yes\/no\)\?", lambda s, l: s.send_line("yes", l)),
            ]
        )
        scp_errors = OrderedDict(
            [
                ("[Nn]o such file or directory", "No such file or directory."),
                ("[Nn]ame or service not known", "Name or service not known"),
                ("[Nn]etwork is unreachable", "Network is unreachable"),
                ("[Pp]ermission denied", "Permission denied"),
            ]
        )
        action_map and scp_actions.update(action_map)
        error_map and scp_errors.update(error_map)

        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=command_template,
            action_map=scp_actions,
            error_map=scp_errors,
        ).execute_command(**kwargs)

    def scp_upload(self, filepath, remote_url):
        url_obj = Url.get_url_obj(remote_url)
        command_template = CommandTemplate(
            "scp -P {scp_port} {src_location} {dst_location}"
        )
        return self._run_scp_template(
            url_obj,
            command_template,
            scp_port=url_obj.port or "22",
            src_location=filepath,
            dst_location=url_obj.get_scp_endpoint(),
        )

    def scp_download(self, remote_url, filepath):
        url_obj = Url.get_url_obj(remote_url)
        command_template = CommandTemplate(
            "scp -P {scp_port} {src_location} {dst_location}"
        )
        return self._run_scp_template(
            url_obj,
            command_template,
            scp_port=url_obj.port or "22",
            src_location=url_obj.get_scp_endpoint(),
            dst_location=filepath,
        )

    @staticmethod
    def _exception(message):
        raise Exception(message)

    def _run_ftp_template(
        self, url_obj, command_template, action_map=None, error_map=None, **kwargs
    ):
        ftp_action_map = OrderedDict(
            [
                (
                    r"[Nn]ame|[Uu]sername|[Ll]ogin.*:",
                    lambda s, l: s.send_line(url_obj.username, l),
                ),
                (r"[Pp]assword.*:", lambda s, l: s.send_line(url_obj.password, l)),
                (
                    r"[Ll]ogin incorrect|failed",
                    lambda s, l: self._exception("Login or Password is not correct."),
                ),
                (
                    r"[Cc]onnection timed out|[Nn]ot connected",
                    lambda s, l: self._exception("Cannot connect to ftp host."),
                ),
            ]
        )
        ftp_error_map = OrderedDict(
            [
                (r"[Ll]ogin incorrect|failed", "Login or Password is not correct."),
                (
                    r"[Cc]onnection timed out|[Nn]ot connected",
                    "Cannot connect to ftp host.",
                ),
            ]
        )

        ftp_command_mode = CommandMode(
            r"ftp>",
            enter_command="ftp {} {}".format(url_obj.hostname, url_obj.port or "21"),
            exit_command="exit",
            enter_action_map=ftp_action_map,
            enter_error_map=ftp_error_map,
        )
        try:
            with self._cli_service.enter_mode(ftp_command_mode):
                return CommandTemplateExecutor(
                    cli_service=self._cli_service,
                    error_map=error_map,
                    action_map=action_map,
                    command_template=command_template,
                ).execute_command(**kwargs)
        finally:
            # Fix for https://github.com/QualiSystems/cloudshell-cli/issues/113
            if self._cli_service.command_mode == ftp_command_mode:
                ftp_command_mode.step_down(self._cli_service, self._logger)

    def ftp_upload(self, filepath, remote_url):
        url_obj = Url.get_url_obj(remote_url)
        command_template = CommandTemplate(
            "put {src_location} {dst_location}",
            error_map=OrderedDict(
                [(r"Could not create file", "FTP: Could not create file.")]
            ),
        )
        return self._run_ftp_template(
            url_obj,
            command_template,
            src_location=filepath,
            dst_location=url_obj.get_ftp_path(),
        )

    def ftp_download(self, remote_url, filepath):
        url_obj = Url.get_url_obj(remote_url)
        command_template = CommandTemplate(
            "get {src_location} {dst_location}", error_map=OrderedDict([])
        )
        return self._run_ftp_template(
            url_obj,
            command_template,
            src_location=url_obj.get_ftp_path(),
            dst_location=filepath,
        )

    def curl_ftp_upload(self, filepath, remote_url):
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=CommandTemplate(r"curl -Ss -T {local_file} {remote_url}"),
        ).execute_command(local_file=filepath, remote_url=remote_url)

    def curl_ftp_download(self, remote_url, filepath):
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=CommandTemplate(r"curl -Ss -o {local_file} {remote_url}"),
        ).execute_command(local_file=filepath, remote_url=remote_url)

    def tftp_upload(self, filepath, remote_url):
        raise Exception("Tftp protocol is not implemented")

    def tftp_download(self, remote_url, filepath):
        raise Exception("Tftp protocol is not implemented")
