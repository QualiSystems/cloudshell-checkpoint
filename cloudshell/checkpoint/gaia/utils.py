class LogCommand(object):
    def __init__(self, logger, command_name):
        self.logger = logger
        self.command_message = "Command {} ".format(command_name)

    def __enter__(self):
        self.logger.info(self.command_message + "started")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_val:
            self.logger.info(self.command_message + "completed")
