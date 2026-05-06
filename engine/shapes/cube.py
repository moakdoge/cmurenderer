import math
from typing import TYPE_CHECKING

from engine.shapes import Base3DShape
from engine.triangle import Triangle
from engine.vector3 import Vector3
from engine.light import lights
from cmu_graphics import Circle, rgb

if TYPE_CHECKING:
    from cmu_graphics.shape_logic import RGB
from engine import game

class Cube(Base3DShape):
    def draw(self):
        if not self.valid:
            return
        vertices = [
            Vector3(-1, -1, -1),
            Vector3( 1, -1, -1),
            Vector3( 1,  1, -1),
            Vector3(-1,  1, -1),
            Vector3(-1, -1,  1),
            Vector3( 1, -1,  1),
            Vector3( 1,  1,  1),
            Vector3(-1,  1,  1),
        ]
        scaled_vertices = []

        for v in vertices:
            scaled_vertices.append(
                Vector3(
                    v.x * self.size.x / 2,
                    v.y * self.size.y / 2,
                    v.z * self.size.z / 2
                )
            )

        faces = [
            (0, 1, 2, 3),  # back
            (4, 5, 6, 7),  # front
            (0, 1, 5, 4),  # bottom
            (2, 3, 7, 6),  # top
            (1, 2, 6, 5),  # right
            (0, 3, 7, 4),  # left
        ]

        for face in faces:
            scale = 1

            v1 = (scaled_vertices[face[0]] * scale).rotate(self.rotation)
            v2 = (scaled_vertices[face[1]] * scale).rotate(self.rotation)
            v3 = (scaled_vertices[face[2]] * scale).rotate(self.rotation)
            v4 = (scaled_vertices[face[3]] * scale).rotate(self.rotation)

            normal = (v2 - v1).cross(v4 - v1).normal
            center = (v1 + v2 + v3 + v4) * 0.25 + self.position

            ambient = 0.45
            brightness = ambient
            if lights:
                for light in lights:
                    light_dir = (light.position - center).normal
                    diffuse = max(0.0, normal.dot(light_dir))
                    dist = light.position.distance(center)
                    attenuation = 1.0 / (1.0 + 0.0025 * dist * dist)
                    brightness += diffuse * light.brightness * attenuation
            else:
                brightness = 1.0

            brightness = min(1.0, brightness)
            face_fill = rgb(
                int(self.fill.red * brightness),
                int(self.fill.green * brightness),
                int(self.fill.blue * brightness),
            )

            Triangle(self.position, v1, v2, v3, fill=self.fill)
            Triangle(self.position, v1, v3, v4, fill=self.fill)
        