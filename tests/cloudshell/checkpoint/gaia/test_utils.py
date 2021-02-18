from unittest import TestCase, mock
from unittest.mock import call, patch

from cloudshell.checkpoint.gaia.utils import LogCommand


class TestUtils(TestCase):
    def setUp(self):
        self.logger = mock.Mock()
        self.command_name = "test command"
        self.instance = LogCommand(self.logger, self.command_name)

    def test_init(self):
        self.assertIs(self.instance.logger, self.logger)
        self.assertEqual(self.instance.command_name, self.command_name)

    def test_get_status_message(self):
        self.assertTrue(
            self.command_name in self.instance.get_message(self.instance.START_MSG)
        )
        self.assertTrue(
            self.instance.START_MSG
            in self.instance.get_message(self.instance.START_MSG)
        )

    @patch("cloudshell.checkpoint.gaia.utils.LogCommand.get_message")
    def test_context_manager(self, get_message):
        start_msg = mock.Mock()
        stop_msg = mock.Mock()
        get_message.side_effect = [start_msg, stop_msg]
        with self.instance:
            pass
        get_message.assert_has_calls(
            [call(self.instance.START_MSG), call(self.instance.COMPLETE_MSG)]
        )
        self.logger.info.assert_has_calls([call(start_msg), call(stop_msg)])

    @patch("cloudshell.checkpoint.gaia.utils.LogCommand.get_message")
    def test_context_manager_with_exception(self, get_message):
        start_msg = mock.Mock()
        stop_msg = mock.Mock()
        get_message.side_effect = [start_msg, stop_msg]

        with self.assertRaises(Exception), self.instance:
            raise Exception()
        get_message.assert_called_once_with(self.instance.START_MSG)
        self.logger.info.assert_called_once_with(start_msg)
