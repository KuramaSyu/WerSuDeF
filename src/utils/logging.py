import logging
from logging import getLogger
from typing import Optional
from colorama import Fore, Style
import sys

def logging_provider(file: str, cls_instance: Optional[object] = None) -> logging.Logger:
    """provides a logger for the given file and class name"""
    logger_name = f"{file}"
    if cls_instance:
        logger_name += f".{cls_instance.__class__.__qualname__}"
    log = getLogger(logger_name)
    log.setLevel(logging.DEBUG)

        # Colored formatter for stdout
    class ColoredFormatter(logging.Formatter):
        COLORS = {
            'DEBUG': Fore.CYAN,
            'INFO': Fore.GREEN,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRITICAL': Fore.MAGENTA,
        }
        
        def format(self, record):
            levelname = record.levelname[0]  # First letter only
            color = self.COLORS.get(record.levelname, '')
            
            # For DEBUG, use thin text for message
            if record.levelname == 'DEBUG':
                record.levelname = f"{Style.BRIGHT}{color}{levelname}{Style.RESET_ALL}"
                formatted = super().format(record)
                # Apply dim white to message only (after the last ": ")
                parts = formatted.split(': ', 1)
                if len(parts) == 2:
                    return Style.BRIGHT + parts[0] + Style.RESET_ALL + ': ' + Style.DIM + Fore.WHITE + parts[1] + Style.RESET_ALL
                return formatted
            else:
                record.levelname = f"{Style.BRIGHT}{color}{levelname}{Style.RESET_ALL}"
                formatted = super().format(record)
                # Make everything before message bright, message grey
                parts = formatted.split(': ', 1)
                if len(parts) == 2:
                    return Style.BRIGHT + parts[0] + Style.RESET_ALL + ': ' + Fore.LIGHTBLACK_EX + parts[1] + Style.RESET_ALL
                return formatted


    # common format
    formatter = logging.Formatter(
        "%(asctime)s %(name)s %(levelname)s: %(message)s"
    )

    # file handler
    file_handler = logging.FileHandler("grpc_server.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # stdout handler (with colors)
    stdout_formatter = ColoredFormatter(
        "%(levelname)s %(asctime)s %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(stdout_formatter)

    # attach both
    log.addHandler(file_handler)
    log.addHandler(stdout_handler)
    return log