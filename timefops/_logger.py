import logging
import colorama as clr


class LogFormatter(logging.Formatter):
    @staticmethod
    def _gen_msg(content, esc_code=""):
        """Generates either a colored or uncolored log message."""
        if esc_code:
            return getattr(clr.Fore, f"{esc_code}") + \
                    f"{content} %(msg)s" + clr.Style.RESET_ALL
        else:
            return f"{content} %(msg)s"


    def __init__(self, *custom_formats, color=True):
        super().__init__()
        if color:
            clr.init()

        self.FORMATS = {
            logging.ERROR: self._gen_msg("%(levelname)s:", esc_code="RED" \
                    if color else ""),
            logging.WARNING: self._gen_msg("%(levelname)s:", esc_code="YELLOW" \
                    if color else ""),
            logging.DEBUG: self._gen_msg("%(levelname)s:", esc_code="CYAN" \
                    if color else ""),
            logging.INFO: "%(msg)s",
            "DEFAULT": "%(levelname)s: %(msg)s",
        }

        for d in custom_formats:
            for k, v in d.items():
                self.FORMATS[k] = v

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.FORMATS["DEFAULT"])
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def init_logging(loglevel, name, color=True):
    logger = logging.getLogger(name)
    logger.setLevel(loglevel)
    logger.verbose = lambda msg, *args: logger._log(15, msg, args)
    logger.success = lambda msg, *args: logger._log(25, msg, args)
    log_stream = logging.StreamHandler()
    log_stream.setLevel(loglevel)
    log_stream.setFormatter(LogFormatter({
      15: "VERBOSE: %(msg)s", 
      25: LogFormatter._gen_msg("SUCCESS:", esc_code="GREEN" if color else "")
    }, color=color))
    logger.addHandler(log_stream)
    return logger
