from typing import TYPE_CHECKING


from engine.light import Light, lights
from engine.vector3 import Vector3
from cmu_graphics import *
if TYPE_CHECKING:
    from engine._game import Game
existing_game: "Game"

class Triangle():
    def __init__(
        self,
        position: Vector3,
        *points: Vector3,
        fill=rgb(255,255,255),
        texture: str | None = None,
        pretransformed: bool = False,
        render_lights: bool = True,
        skip_near_clip: bool = False
    ):
        
        self.points: list[Vector3] = [*points]
        self.position = position
        self.fill = fill
        self._count = len(points)
        self._real_fill= fill
        self.fogged = False


        if not pretransformed:
            # calculate camera offset and rotate into view space
            for i, p in enumerate(self.points):
                self.points[i] = p + position - existing_game.camera.position
                self.points[i] = self.points[i].rotate(
                    Vector3.new(existing_game.camera.pitch, existing_game.camera.yaw, 0)
                )

        clipped = [tuple(self.points)] if skip_near_clip else self.clip_near()
        if not clipped:
            return

        if len(clipped) > 1:
            _, second = clipped
            Triangle(
                Vector3.zero(),
                *second,
                fill=fill,
                texture=texture,
                pretransformed=True,
                render_lights=render_lights,
                skip_near_clip=True
            )

        self.points = list(clipped[0])
        self._count = len(self.points)
        
        

        #check offscreen
        if all(_.offscreen for _ in self.points):
            return
        

        #calculate z and screens
        self.z = sum(_.z for _ in self.points) / self._count
        screens: list[tuple[int, int]] = [_.screen for _ in self.points]
        self.screen = screens
        

        
        #check hidden
        if None in screens:
            self.screen = screens

        self.extracted = [list(sublist) for sublist in self.screen]
        lowest = 140 * existing_game.configuration.fog
        if (self.screen_area < lowest):
            return
        
        if (self.screen_area > lowest and self.screen_area < lowest * 1.25):
            fill = fill.darker().darker().darker()
            self.fogged = True

        self.center = Vector3.new(
            sum(_.x for _ in self.points) / self._count,
            sum(_.y for _ in self.points) / self._count,
            sum(_.z for _ in self.points) / self._count
        )
        if existing_game.configuration.backface_cull:
            p1, p2, p3 = tuple(self.points)
            normal = (p2 - p1).cross(p3 - p1).normal
            view_dir = (-self.center).normal
            if normal.dot(view_dir) <= 0:
                return

        existing_game.add_triangle(self)
        centScr = self.center.screen
        self.average_screen_dist = max(distance(_[0],_[1], centScr[0], centScr[1]) for _ in self.screen)
        
        ar = self.area(*self.screen)
        if ar < (50 / existing_game.configuration.quality):
            return
        #calculate color  
        
        self._real_fill = fill.darker().darker().darker().darker().darker()
        normal = self.center.normal
        if existing_game.configuration.shading and render_lights:
            ambient = 0.35
            brightness = ambient

            for light in lights:
                if getattr(light, "directional", False):
                    light_dir = (-light.direction).normal
                    diffuse = max(0.0, normal.dot(light_dir))
                    brightness += diffuse * light.brightness
                else:
                    light_pos = light.position - existing_game.camera.position
                    light_pos = light_pos.rotate(
                        Vector3.new(existing_game.camera.pitch, existing_game.camera.yaw, 0)
                    )

                    light_dir = (light_pos - self.center).normal
                    diffuse = max(0.0, normal.dot(light_dir))

                    dist = light_pos.distance(self.center)
                    attenuation = 1.0 / (1.0 + 0.00001 * dist * dist)

                    brightness += diffuse * light.brightness * attenuation

            brightness = max(0.0, min(1.0, brightness))




    def draw(self):
        self._shape = existing_game.polygon_factory.reserve()
        if self._shape.pointList != self.extracted:
            self._shape.pointList = self.extracted
        #self._shape.pointList = self.extracted
        if self._shape.fill != self._real_fill:
            self._shape.fill = self._real_fill
        try:
            if getattr(self._shape, "zindex", -1) != self.z:
                self._shape.zindex = self.z
        except Exception as e:    
            self._shape.zindex = self.z
        if existing_game.configuration.wireframe:
            self._shape.fill = None
            self._shape.border = self.fill
        else:
            self._shape.border = None
        if self.fogged:
            self._shape.opacity = 50
        else:
            self._shape.opacity = 100
        self._shape.visible = True

    

    def clip_near(self):
        points = self.points
        NEAR = 1.0
        inside = [p for p in points if p.z >= NEAR]
        outside = [p for p in points if p.z < NEAR]

        if len(inside) == 3:
            return [(points[0], points[1], points[2])]

        if len(inside) == 0:
            return []

        if len(inside) == 1:
            a = inside[0]
            b, c = outside

            ab = a.intersect_near(b)
            ac = a.intersect_near(c)

            return [(a, ab, ac)]

        # len(inside) == 2
        a, b = inside
        c = outside[0]

        ac = a.intersect_near(c)
        bc = b.intersect_near(c)

        return [
            (a, b, ac),
            (b, bc, ac),
        ]
    def delete(self):
        if hasattr(self, "_shape"):
            existing_game.polygon_factory.free(self._shape)
            self._shape.visible = False
            del self._shape
        existing_game.remove_triangle(self)

    def get_bounding_box(self): 
        min_x = rounded(min(self.screen[0][0], self.screen[1][0], self.screen[2][0]))
        max_x = rounded(max(self.screen[0][0], self.screen[1][0], self.screen[2][0]))
        min_y = rounded(min(self.screen[0][1], self.screen[1][1], self.screen[2][1]))
        max_y = rounded(max(self.screen[0][1], self.screen[1][1], self.screen[2][1])) 
        return min_x, min_y, max_x, max_y
    def is_covered(self):
        success = 0
        total_points = self._count
        dis = 250 ** 2
        for _t in existing_game.triangles:
            if _t.z < self.z:
                continue

            left, bottom, right, top = _t.get_bounding_box()
            inside_points = 0
            for x, y in self.screen:
                if left < x < right and bottom < y < top:
                    inside_points += 1

            if inside_points / total_points >= 0.5:
                return True 
        
        return False


    def area(self, p1, p2, p3):
        return abs(
            (p2[0] - p1[0]) * (p3[1] - p1[1])
        - (p2[1] - p1[1]) * (p3[0] - p1[0])
        )
    @property
    def rendered(self):
        return self._shape

    @property
    def screen_area(self):
        return self.area(*self.extracted)
    
    @property
    def physical_area(self):
        p1, p2, p3 = tuple(self.points)
        v1 = p2 - p1
        v2 = p3 - p1
        cross_product = v1.cross(v2)
        return 0.5 * cross_product.magnitude
