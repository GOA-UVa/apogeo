import logging
import os
from datetime import datetime

_FORMAT = "%(asctime)s | %(levelname)s: [%(filename)s:%(lineno)s - %(funcName)10s() ] %(message)s"
_DATEFORMAT = "%H:%M:%S"
_LOGPATH = "./logs"
DEBUG_ENV_NAME = "APOGEO_DEBUG"
DEV_LOGOUT_ENV_NAME = "APOGEO_DEV_LOG"

# Singleton

_logger = None
_logger_date: datetime = None


def get_logger() -> logging.Logger:
    """Returns the logger, used for logging messages.

    Returns:
    --------
    logging.Logger:
        Apogeo logger.
    """
    global _logger, _logger_date
    dtnow = datetime.now()
    if _logger_date and _logger_date.day < dtnow.day:
        _logger = None
    if _logger == None:
        _logger_date = dtnow
        logname = dtnow.strftime("%Y%m%d")
        os.makedirs(_LOGPATH, exist_ok=True)
        logname = os.path.join(_LOGPATH, f"log_{logname}.txt")
        logging.basicConfig(
            filename=logname, filemode="a", format=_FORMAT, datefmt=_DATEFORMAT
        )
        _logger = logging.getLogger(__name__)
        debug_value = "INFO"
        if DEBUG_ENV_NAME in os.environ:
            debug_value = os.environ[DEBUG_ENV_NAME]
        if isinstance(debug_value, str) and debug_value.upper() == "DEBUG":
            _logger.setLevel(logging.DEBUG)
        else:
            _logger.setLevel(logging.INFO)
        if DEV_LOGOUT_ENV_NAME in os.environ:
            # to print logs in terminal screen add environment variable named "APOGEO_DEV_LOG"
            _logger.addHandler(logging.StreamHandler())
    return _logger
