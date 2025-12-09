from dataclasses import dataclass
from typing import Optional, Callable
import logging

type LoggingProvider = Callable[[str, Optional[object]], logging.Logger]

@dataclass
class Pagination:
    limit: int
    offset: int