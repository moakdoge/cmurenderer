import math
from typing import TYPE_CHECKING

from engine.vector3 import Vector3
from engine.camera import Camera
from cmu_graphics import app

if TYPE_CHECKING:
    from engine._game import Game

from engine.triangle import Triangle
from engine.ray import Ray

class Player():
    def __init__(self, camera: Camera) -> None:
        self.attached_camera = camera
        self.position: Vector3 = Vector3.zero()
        self.velocity: Vector3 = Vector3.new(0,0,0)
        self.max_health = 100
        self._game_parent: "Game"
        self.health = 100
        
    def __setattr__(self, name: str, value) -> None:
        if name == "position":
            self.attached_camera.position = value
        object.__setattr__(self, name, value)
    def on_floor(self):
        return (self.position.y <= 0)
    
    def check_collision(self, vel: Vector3) -> bool:
        dst = math.hypot(vel.x, vel.y, vel.z)
        if dst <= 0:
            return False

        dir = Vector3(
            vel.x / dst,
            vel.y / dst,
            vel.z / dst,
        )

        r = Ray(self.position, dir, dst*2)
        return r.cast() is not None
    
    def update(self):
        s = 48
        self.collider = Triangle(
            self.position,
            Vector3(-s, 0, 0),
            Vector3(s, 0, 0),
            Vector3(0, s * 2, 0),
            render_shadow=False,
            render_lights=False,
            opacity=1,
        )

        if abs(self.velocity.x > 0) or abs(self.velocity.y) > 0 or abs(self.velocity.z) > 0 and self._game_parent.configuration.current.collisions:
            move = self.velocity * app.dt
            for axis_move in (
                Vector3(move.x, 0, 0),
                Vector3(0, move.y, 0),
                Vector3(0, 0, move.z),
            ):
                if axis_move.magnitude <= 0:
                    continue

                if not self.check_collision(axis_move):
                    self.position += axis_move
                else:
                    if axis_move.x: self.velocity.x = 0
                    if axis_move.y: self.velocity.y = 0
                    if axis_move.z: self.velocity.z = 0

        
        self.velocity -= Vector3.new(0,32,0)
        self.velocity *= 0.95

        if self.position.y < 0:
            self.position.y = 0


    def jump(self):
        self.velocity += Vector3.new(0, 140, 0)


