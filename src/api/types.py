from typing import Optional, Callable
import logging

type loggingProvider = Callable[[str, Optional[object]], logging.Logger]
