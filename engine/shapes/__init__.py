from typing import TYPE_CHECKING

from engine.vector3 import Vector3
if TYPE_CHECKING:
    from cmu_graphics.shape_logic import RGB
from cmu_graphics import rgb
from engine import game
class Base3DShape:
    def __init__(self, position: Vector3, size: Vector3, fill: "RGB | None" = None) -> None:
        self.position: Vector3 = position
        self.size: Vector3 = size
        self.fill: "RGB" = fill or rgb(255,0,0)
        self.rotation: Vector3 = Vector3.zero()
        game._shapes.append(self)

    def draw(self):
        raise NotImplementedError