import math
from typing import TYPE_CHECKING

from engine.cmu_utils import CMUtils
from engine.vector3 import Vector3
if TYPE_CHECKING:
    from engine.sprite import Sprite
from engine.player import Player
class SpriteAI:
    def __init__(self, parent: "Sprite") -> None:
        self.parent = parent
        self._active_target: Vector3 | None = None
        self._track_player: "Player | None" = None
        self.speed = 2
        pass
    
    def tick(self):
        if self._track_player:
            self._active_target = self._track_player.position
        if self._active_target is None:
            return
        
        movement_vector = (self._active_target - self.parent.position).normal * self.speed
        collide_player = self.parent.is_touching_player()
        collide_wall = self.parent.is_colliding(movement_vector)
        collide = collide_player or collide_wall
        
        if collide:
          self.parent.position -= movement_vector
          new = self.find_open_move(movement_vector)
          movement_vector = new


        self.parent.position += movement_vector
    def find_open_move(self, movement_vector: Vector3) -> Vector3:
        for dg in (30, -30, 60, -60, 90, -90, 135, -135, 180):
            test = movement_vector.rotate_x(math.radians(dg))
            if not self.parent.is_colliding(test):
                return test

        return Vector3.zero()
    def target(self, object: "Vector3 | Player"):
        if isinstance(object, Player):
            self._track_player = object
        else:
            self._active_target = object 
        