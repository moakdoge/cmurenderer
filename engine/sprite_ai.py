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
        if self.parent.is_touching_player():
            return

        if self.parent.is_colliding(movement_vector):
            move_x = Vector3.new(movement_vector.x, 0, 0)
            move_z = Vector3.new(0, 0, movement_vector.z)

            if not self.parent.is_colliding(move_x):
                movement_vector = move_x
            elif not self.parent.is_colliding(move_z):
                movement_vector = move_z
            else:
                return

        self.parent.position += movement_vector
    def target(self, object: "Vector3 | Player"):
        if isinstance(object, Player):
            self._track_player = object
        else:
            self._active_target = object 
        
    def valid_point(self, origin: Vector3, point: Vector3) -> bool:
        movement = point - origin

        if self.parent.is_colliding_from(origin, movement):
            return False
        return True
    
    def next_point(self, start: Vector3, end: Vector3) -> Vector3:
        direction = (end - start).normal
        step_size = 50
        

        direct = start + direction * step_size

        if self.valid_point(start, direct):
            return direct

        for angle in (30, -30, 60, -60, 90, -90, 135, -135, 180):
            rotated = direction.rotate_y(math.radians(angle))
            candidate = start + rotated * step_size
            
            if self.valid_point(start, candidate):
                #print("yeppers")
                return candidate

        return start
    def pathfind(self, start: Vector3, end: Vector3) -> list[Vector3]:
        steps = 28
        diff = (end - start)
        pts: list[Vector3] = []
        current = start
        for i in range(steps):
            target = start + (diff * ((i + 1) / steps))
            current = self.next_point(current, target)
            pts.append(current)
        return pts