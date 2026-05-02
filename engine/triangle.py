from typing import TYPE_CHECKING


from engine.light import Light, lights
from engine.vector3 import Vector3
from cmu_graphics import *
if TYPE_CHECKING:
    from engine._game import Game
existing_game: "Game"

class Triangle():
    def __init__(self, position: Vector3, *points: Vector3, fill=rgb(255,255,255), texture: str | None = None):
        self.points: list[Vector3] = [*points]
        self.position = position
        self.fill = fill
        self._count = len(points)


        invalid_points = 0
        #calculate camera offset
        for i, p in enumerate(self.points):
            self.points[i] = p + position -existing_game.camera.position
            self.points[i] = self.points[i].rotate(Vector3.new(existing_game.camera.pitch,existing_game.camera.yaw,0))
            if self.points[i].z < 0:
                #print(self.points[i].screen)
                #self.points[i].z = -self.points[i].z
                pass
        

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

        self.center = Vector3.new(sum(_.x for _ in self.points)/self._count,sum(_.y for _ in self.points)/self._count,sum(_.z for _ in self.points)/self._count)
        centScr = self.center.screen
        self.average_screen_dist = max(distance(_[0],_[1], centScr[0], centScr[1]) for _ in self.screen)
        
        ar = self.area(*self.screen)
        if ar < (180 / existing_game.configuration.quality):
            return
        #calculate color  
        self._real_fill = fill.darker().darker().darker().darker().darker()
        if existing_game.configuration.shading:
            normal = self.center.normal  # polygon/triangle face normal, normalized

            ambient = 0.25
            brightness = ambient

            for light in lights:
                # Direction from surface to light
                light_dir = (light.position - self.center).normal

                # Lambert diffuse
                diffuse = max(0.0, normal.dot(light_dir))

                # Optional distance falloff
                dist = light.position.distance(self.center)
                attenuation = 1.0 / (1.0 + 0.001 * dist * dist)

                brightness += diffuse * light.brightness * attenuation

            brightness = min(1.0, brightness)

            self._real_fill = rgb(
                int(fill.red * brightness),
                int(fill.green * brightness),
                int(fill.blue * brightness),
            )

        
        self.extracted = [list(sublist) for sublist in screens]

        self._shape = existing_game.polygon_factory.reserve()
        self._shape.pointList = self.extracted
        #self._shape.pointList = self.extracted
        self._shape.fill = self._real_fill
        self._shape.zindex = self.z
        if existing_game.configuration.wireframe:
            self._shape.fill = None
            self._shape.border = fill
        existing_game.add_triangle(self)
    
    def delete(self):
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