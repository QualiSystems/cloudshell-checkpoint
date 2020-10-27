from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.devices.networking_utils import UrlParser


class FileTransferActions(object):
    def __init__(self, cli_service, logger):
        """

        :param cli_service: config mode cli service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    def scp_transfer(self, src_location, dst_location, password, scp_port=None, action_map=None, error_map=None):
        """
        :param str src_location:
        :param str dst_location:
        :param str password:
        :param str scp_port:
        :param collections.OrderedDict action_map:
        :param collections.OrderedDict error_map:
        """
        scp_port = scp_port or "22"
        scp_actions = OrderedDict([(r"[Pp]assword:", lambda s, l: s.send_line(password, l)),
                                   (r"\(yes\/no\)\?", lambda s, l: s.send_line("yes", l))])
        scp_errors = OrderedDict([("[Nn]o such file or directory", "No such file or directory.")])
        action_map and scp_actions.update(action_map)
        error_map and scp_errors.update(error_map)

        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=CommandTemplate(
                                           "scp -P {scp_port} {src_location} {dst_location}"),
                                       action_map=scp_actions, error_map=scp_errors).execute_command(
            scp_port=scp_port,
            src_location=src_location,
            dst_location=dst_location)

    def scp_upload(self, filepath, remote_url):
        url_obj = Url(remote_url)
        return self.scp_transfer(filepath, url_obj.get_scp_endpoint(), url_obj.password, url_obj.port)

    def scp_download(self, remote_url, filepath):
        url_obj = Url(remote_url)
        return self.scp_transfer(url_obj.get_scp_endpoint(), filepath, url_obj.password, url_obj.port)


class Url:
    def __init__(self, url):
        self._url_object = UrlParser.parse_url(url)

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
