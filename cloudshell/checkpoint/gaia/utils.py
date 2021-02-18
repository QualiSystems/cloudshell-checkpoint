class LogCommand(object):
    START_MSG = "started"
    COMPLETE_MSG = "completed"

    def __init__(self, logger, command_name):
        self.logger = logger
        self.command_name = command_name

    def get_message(self, status_message):
        return "Command {} {}".format(self.command_name, status_message)

    def __enter__(self):
        self.logger.info(self.get_message(self.START_MSG))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_val:
            self.logger.info(self.get_message(self.COMPLETE_MSG))
