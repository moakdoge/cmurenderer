import math
from typing import TYPE_CHECKING

from engine.shapes import Base3DShape
from engine.triangle import Triangle
from engine.vector3 import Vector3

if TYPE_CHECKING:
    from cmu_graphics.shape_logic import RGB
from engine import game

class Sphere(Base3DShape):
    def __init__(self, position: Vector3, radius: float, fill: "RGB") -> None:
        super().__init__(position, Vector3.new(radius*2, radius*2, radius*2), fill=fill)
        self.radius = radius
        
    def draw(self):
        if not self.valid:
            return
        vertices: list[Vector3] = []
        lat_steps =5 if game.utils.is_web() else 15#math.ceil(5 * game.configuration.quality)
        lon_steps =5 if game.utils.is_web() else 15#math.ceil(30 * (game.configuration.quality/8))



        for i in range(lat_steps + 1):
            theta = i / lat_steps * math.pi
            for j in range(lon_steps + 1):
                phi = j / lon_steps * 2 * math.pi

                x = self.size.x * math.sin(theta) * math.cos(phi)
                y = self.size.y * math.cos(theta)
                z = self.size.z * math.sin(theta) * math.sin(phi)

                vertices.append(Vector3(x, y, z))
        faces = []

        for i in range(lat_steps):
            for j in range(lon_steps):
                p1 = i * (lon_steps + 1) + j
                p2 = p1 + lon_steps + 1
                p3 = p2 + 1
                p4 = p1 + 1

                faces.append((p1, p2, p3))
                faces.append((p1, p3, p4))
        for face in faces:
            v1 = vertices[face[0]].rotate(self.rotation)
            v2 = vertices[face[1]].rotate(self.rotation)#.rotate_x(math.radians((self.position.x / 400) * 360))
            v3 = vertices[face[2]].rotate(self.rotation)#.rotate_x(math.radians((self.position.x / 400) * 360))
            Triangle(self.position, v1, v2, v3, fill=self.fill)
