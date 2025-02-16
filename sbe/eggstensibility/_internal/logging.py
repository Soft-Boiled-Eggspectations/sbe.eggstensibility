from typing import Protocol


class Logger(Protocol):
    """
    LoggerProtocol defines the logger used within Builders and Validators. The protocol
    follows the default logger implementation provided in logging.
    """

    def debug(self, msg, *args, **kwargs): ...

    def info(self, msg, *args, **kwargs): ...

    def warning(self, msg, *args, **kwargs): ...

    def error(self, msg, *args, **kwargs): ...


class IdentityLogger:
    """Default logger if no custom-logger is provided. Ignore all messages."""

    def debug(self, msg, *args, **kwargs):
        return

    def info(self, msg, *args, **kwargs):
        return

    def warning(self, msg, *args, **kwargs):
        return

    def error(self, msg, *args, **kwargs):
        return
