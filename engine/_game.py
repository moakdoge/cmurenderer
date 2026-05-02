import math
from typing import TYPE_CHECKING

from cmu_graphics import *

from engine.camera import Camera
from engine.light import Light
from engine.player import Player
from engine.triangle import Triangle
from engine.vector3 import Vector3


from engine.cmu_utils import CMUtils
utils: "CMUtils" = CMUtils()
from engine.polygon_factory import PolygonFactory
if TYPE_CHECKING:
    from engine.shapes import Base3DShape
class Game():
    class GameConfiguration():
        wireframe: bool = False
        max_triangles: int = 1950
        shading: bool = True
        quality: float = 0.75  #increase for worse quality
        cmu_quality: float = 0.125 #for CMU WEB only
        fps_target: int = 30
        enable_auto_quality: bool = False

    def __init__(self):
        global utils
        self.utils = utils
        utils.register_game(self)
        self.camera = Camera()
        self.player = Player(self.camera)
        self.configuration = self.GameConfiguration()
        self.triangles: list[Triangle] = []
        self._triangle_count = 0
        self.polygon_factory: "PolygonFactory" = PolygonFactory()
        self.fps = 30
        self._shapes: list["Base3DShape"] = []
        self.sun = Light(Vector3.new(900, 900, 900), direction=Vector3.new(-900, -900, -900), brightness=1500)
        app.inspectorEnabled = False
        if utils.is_web():
            self.configuration.quality = self.configuration.cmu_quality



    @utils.make_global
    def onKeyHold(self, key):
        forward = self.camera.direction
        forward.x *= -1
        forward.y = 0
        right = Vector3(forward.z, 0, -forward.x).normal
        speed = 2
        if "w" in key: self.player.velocity += forward * speed * 1
        if "s" in key: self.player.velocity += forward * speed * -1
        if "a" in key: self.player.velocity += right * speed * -1
        if "d" in key: self.player.velocity += right * speed * 1
    
    @utils.make_global
    def onKeyPress(self,key):
        speed=math.radians(30)
        #camera

        if "up" == key: self.camera.pitch += speed
        if "down" == key: self.camera.pitch -= speed
        if "right"== key: self.camera.yaw -= speed
        if "left" == key: self.camera.yaw += speed
        
        if "space" == key:
            self.player.jump()


        
    def add_triangle(self, triangle):
        if self._triangle_count > self.configuration.max_triangles * self.configuration.quality:
            return
        if not triangle in self.triangles:
            self.triangles.append(triangle)
            self._triangle_count += 1
    
    def remove_triangle(self, triangle):
        if triangle in self.triangles:
            self.triangles.remove(triangle)
            self._triangle_count -= 1
    
    def clear_screen(self):
        for tri in self.triangles[:]:
            tri.delete()
        self._triangle_count = 0
    
    def zlayer_screen(self):
        ci=min(self._triangle_count, math.floor(self._triangle_count*(self.configuration.quality*1.125)))
        
        sorted_triangles = sorted(
            self.triangles,
            reverse=True,
            key=lambda tri: tri.z + tri.screen_area * 0.35
        )

        sorted_triangles.sort(reverse=True, key=lambda tri: tri.z)
        for tri in sorted_triangles:
            tri._shape.toFront()
        
    def tick(self):
        self.clear_screen()
        self.camera.tick()
        for shape in self._shapes:
            shape.draw()
        self.player.update()
        self.zlayer_screen()
