import logging
import sys


class LogFormatter(logging.Formatter):
    def __init__(self, *custom_formats):
        super().__init__()
        self.FORMATS = {
            logging.ERROR: "ERROR: %(msg)s",
            logging.WARNING: "WARNING: %(msg)s",
            logging.DEBUG: "DEBUG: %(module)s: %(lineno)d: %(msg)s",
            "DEFAULT": "%(msg)s",
        }
        for d in custom_formats:
            for k, v in d.items():
                self.FORMATS[k] = v

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.FORMATS["DEFAULT"])
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def init_logging(loglevel, name=__name__):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.verbose = lambda msg, *args: logger._log(15, msg, args)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler = logging.StreamHandler(sys.stderr)

    # Set handler levels, formatters, filter(s) and add the handlers.
    # Log levels 20 (INFO) and below go to stdout, everything above to stderr. 
    stdout_handler.setLevel(loglevel)
    stdout_handler.setFormatter(LogFormatter({15: "INFO: %(msg)s"}))
    stdout_handler.addFilter(lambda x: x.levelno <= logging.INFO)
    logger.addHandler(stdout_handler)

    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(LogFormatter())
    logger.addHandler(stderr_handler)

    return logger
