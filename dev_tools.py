from dataclasses import dataclass
from typing import List

@dataclass
class MousePositions:
    positions: List[tuple]
    is_dragging: bool = False
