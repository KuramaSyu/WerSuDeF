from typing import Optional, Callable
import logging

type LoggingProvider = Callable[[str, Optional[object]], logging.Logger]
