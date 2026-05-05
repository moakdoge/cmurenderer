from engine.triangle import Triangle
from engine.vector3 import Vector3

class Ray:
    __slots__ = ("position", "direction", "distance")
    def __init__(self, position: "Vector3", direction: "Vector3", distance: "float" = float("inf")) -> None:
        self.position = position
        self.direction = direction.normal
        self.distance = distance
        
    def intersects(self, tri: Triangle) -> Triangle | None:
        EPS = 1e-6

        p1, p2, p3 = tri.points
        edge1 = p2 - p1
        edge2 = p3 - p1

        h = self.direction.cross(edge2)
        a = edge1.dot(h)

        if -EPS < a < EPS:
            return None

        f = 1.0 / a
        s = self.position - p1
        u = f * s.dot(h)

        if u < 0.0 or u > 1.0:
            return None

        q = s.cross(edge1)
        v = f * self.direction.dot(q)

        if v < 0.0 or u + v > 1.0:
            return None

        t = f * edge2.dot(q)

        if t <= EPS:
            return None
        
        if t >= self.distance:
            return None

        return t
    
    def cast(self) -> Triangle | None:
        from engine import game
        for tri in game.triangles:
            if self.intersects(tri):
                return tri
        return None