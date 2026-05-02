from engine.vector3 import Vector3
from engine.camera import Camera
from cmu_graphics import app
class Player():
    def __init__(self, camera: Camera) -> None:
        self.attached_camera = camera
        self.position: Vector3 = Vector3.zero()
        self.velocity: Vector3 = Vector3.new(0,0,0)
        self.max_health = 100
        self.health = 100
        
    def __setattr__(self, name: str, value) -> None:
        if name == "position":
            self.attached_camera.position = value
        object.__setattr__(self, name, value)
    def on_floor(self):
        return (self.position.y <= 0)
    
    def update(self):
        if abs(self.velocity.x > 0) or abs(self.velocity.y) > 0 or abs(self.velocity.z) > 0:
            self.position += (self.velocity*app.dt)
        if not self.on_floor():
            self.velocity -= Vector3.new(0,1.75,0)
        else:
            self.velocity.y = 0
        self.velocity *= 0.8

        if self.position.y < 0:
            self.position.y = 0


    def jump(self):
        if self.on_floor():
            self.velocity += Vector3.new(0, 12, 0)


