from engine.vector3 import Vector3
from cmu_graphics import rgb

lights: list["Light"] = []
class Light():
    __slots__ = ("position", "brightness", "color", "direction")
    def __init__(self, position: Vector3, direction: Vector3, brightness: float = 15, color=rgb(255,255,255)):
        self.position = position
        self.brightness = brightness
        self.color = color
        self.direction = direction
        lights.append(self)