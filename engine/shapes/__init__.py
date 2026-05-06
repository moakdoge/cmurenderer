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
        self.valid = True
        game._shapes.append(self)
    





        
    def _draw(self):
        size, position = self.size, self.position
        ds = position.distance(game.camera.position)
        sz = ds - (max(size.x, size.y, size.z))
        if sz > (800*game.configuration.current.quality):
            return
        self.draw()
        
    def draw(self):
        raise NotImplementedError