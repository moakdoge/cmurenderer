import math

from engine.vector3 import Vector3
from engine.light import Light


class Camera():
    def __init__(self, position: Vector3 = Vector3(0,0,0)) -> None:
        self.position = position
        self.pitch: float = 0
        self.yaw: float = 0
        self.roll: float = 0
        self._x = 0
        self.light = Light(self.position, self.direction)
        pass
    def tick(self):
        self.light.position = self.position
        self.light.direction = Vector3.new(self.pitch, 0, self.yaw)
    @property
    def direction(self):
        return Vector3(
                math.sin(self.yaw) * math.cos(self.pitch),
                -math.sin(self.pitch),
                math.cos(self.yaw) * math.cos(self.pitch)
                ).normal
        
    @property
    def ddir(self):
        yaw, pitch = self.yaw, self.pitch
        return Vector3(
            -math.sin(yaw) * math.cos(pitch),
            -math.sin(pitch),
            math.cos(yaw) * math.cos(pitch)
        ).normal
    def __setattr__(self, name: str, value) -> None:
        if name == "pitch":
            value = max(math.radians(-90), min(math.radians(90), value))
        object.__setattr__(self, name, value)

    def __repr__(self) -> str:
        st = f'Camera(position={self.position.__repr__()},yaw={math.ceil(math.degrees(self.yaw))},pitch={math.ceil(math.degrees(self.pitch))},roll={math.ceil(math.degrees(self.roll))})'
        return st