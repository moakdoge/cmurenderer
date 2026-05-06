import math
import time
from typing import TYPE_CHECKING, Callable

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
        debug: bool = True
        backface_cull: bool = False
        zbuffer: bool = True
        zbuffer_scale: int = 6 if utils.is_desktop() else 18
        fog: float = 1.25 #the strength of the fog
        max_triangles: int = 1950
        shading: bool = True
        quality: float = 0.8  #increase for worse quality
        cmu_quality: float = 0.125 #for CMU WEB only
        fps_target: int = 30
        min_quality: float = 0.25 if utils.is_desktop() else 0.01
        shadows: bool = utils.is_desktop()

    def __init__(self):
        global utils
        self.utils = utils
        utils.register_game(self)
        self.camera = Camera()
        self.player = Player(self.camera)
        self.configuration = self.GameConfiguration()
        self.triangles: list[Triangle] = []
        self._triangle_count = 0
        self._triangle_seq = 0
        self.polygon_factory: "PolygonFactory" = PolygonFactory(300)
        self.fps = 30
        self._shapes: list["Base3DShape"] = []
        self.sun = Light(Vector3.new(900, 900, 900), direction=Vector3.new(-900, -900, -900), brightness=15)
        self._last_dt = time.perf_counter()
        self._events: dict[str, list] = {}
        self._main_function: Callable | None = None
        self.frames = 0
        app.inspectorEnabled = False
        if utils.is_web():
            self.configuration.quality = self.configuration.cmu_quality

    def register_tick(self, func):
        if not "tick" in self._events:
            self._events["tick"] = []
        self._events["tick"].append(func)
        return func
    
    def on_ready(self, func: Callable):
        self._main_function = func
        return func

    def warning(self):
        lines = [
            '''WARNING! You are on CMU Web!''',
            "",
            "Performance is much, much worse then on the desktop version and some features may be unsupported!"
        ]
        print("\n".join(lines))

    @utils.make_global(web=False)
    def onMouseMove(self, x, y):
        if self.utils.locked_mouse:
            import pygame
            pygame.event.pump()
            rx, ry = pygame.mouse.get_rel()
            self.camera.yaw += rx * app.dt * -1
            self.camera.pitch += ry * app.dt * -1
        
    @utils.make_global()
    def onKeyHold(self,keys):
        
        #movmement
        forward = self.camera.direction
        forward.x *= -1
        forward.y = 0
        right = Vector3(forward.z, 0, -forward.x).normal
        speed = 60
        if "w" in keys: self.player.velocity += forward * speed * 1
        if "s" in keys: self.player.velocity += forward * speed * -1
        if "a" in keys: self.player.velocity += right * speed * -1
        if "d" in keys: self.player.velocity += right * speed * 1
        
        
        #camera
        speed=math.radians(60)*2
        for key in keys:
            if "up" == key: self.camera.pitch += speed * app.dt
            if "down" == key: self.camera.pitch -= speed* app.dt
            if "right"== key: self.camera.yaw -= speed* app.dt
            if "left" == key: self.camera.yaw += speed* app.dt
            


            if "space" == key:
                self.player.jump()

    @utils.make_global()
    def onKeyPress(self, key: str):
        ### DEBUG ###
        if not self.configuration.debug:
            return
    
        if "q" == key:
            self.configuration.wireframe = not self.configuration.wireframe

        if "z" == key:
            self.utils.unlock_mouse()
            
        if "x" == key:
            self.utils.lock_mouse()
    @utils.make_global()
    def onStep(self):
        _dt = time.perf_counter() - self._last_dt
        self._last_dt = time.perf_counter()
        self.tick()
        self.fps = 1/_dt
        app.dt = _dt
        for fn in self._events.get("tick", []):
            fn(_dt)
        self.frames += 1
        pass
        
    def add_triangle(self, triangle):
        self._triangle_seq += 1
        triangle._sort_id = self._triangle_seq
        self.triangles.append(triangle)
        self._triangle_count += 1
    
    def remove_triangle(self, triangle: "Triangle | None"):
        if triangle in self.triangles:
            if hasattr(triangle, "_shape"):
                self.polygon_factory.free(triangle._shape)
                triangle._shape.visible = False
                del triangle._shape
            self.triangles.remove(triangle)
            self._triangle_count -= 1
    
    def clear_screen(self):
        for tri in self.triangles[:]:
            tri.delete()
        self._triangle_count = 0
        self._triangle_seq = 0
    
    def zlayer_screen(self):
        ci=min(self._triangle_count, math.floor(self._triangle_count*(self.configuration.quality*1.125)))
        
        sorted_triangles = sorted(
            self.triangles,
            reverse=True,
            key=lambda tri: tri.z + (tri._sort_id * 1e-6) + 4*(tri.opacity == 100) # type: ignore
        )

        for tri in sorted_triangles:
            if not hasattr(tri, "_shape"):
                continue
            tri._shape.toFront()
            
    def render_triangles(self):
        zbuffer = None
        zwidth = 0
        zheight = 0
        zscale = max(1, int(self.configuration.zbuffer_scale))
        if self.configuration.zbuffer:
            zwidth = max(1, 400 // zscale)
            zheight = max(1, 400 // zscale)
            zbuffer = [[float("inf")] * zwidth for _ in range(zheight)]

        sorted_triangles = sorted(
            self.triangles,
            reverse=True,
            key = lambda tri: tri.physical_area * tri.screen_area
        )#[0:math.floor(self.configuration.quality*2*(len(self.triangles)-1))]


        if utils.is_desktop():
            import cmu_graphics.cmu_graphics as cmp
            cmp.DRAWING_LOCK.__enter__()
        try:
            for triangle in sorted_triangles:
                if zbuffer is not None and not self._zbuffer_test(triangle, zbuffer, zwidth, zheight, zscale):
                    continue
                triangle.draw()

        finally:
            if utils.is_desktop():
                import cmu_graphics.cmu_graphics as cmp
                cmp.DRAWING_LOCK.__exit__(None, None, None)

    def _zbuffer_test(
        self,
        triangle: Triangle,
        zbuffer: list[list[float]],
        zwidth: int,
        zheight: int,
        zscale: int
    ) -> bool:

        x0, y0 = triangle.screen[0]
        x1, y1 = triangle.screen[1]
        x2, y2 = triangle.screen[2]

        min_x = max(0, int(min(x0, x1, x2) // zscale))
        max_x = min(zwidth - 1, int(max(x0, x1, x2) // zscale))
        min_y = max(0, int(min(y0, y1, y2) // zscale))
        max_y = min(zheight - 1, int(max(y0, y1, y2) // zscale))

        if min_x > max_x or min_y > max_y:
            return False

        z0 = triangle.points[0].z
        z1 = triangle.points[1].z
        z2 = triangle.points[2].z

        def edge(ax, ay, bx, by, cx, cy):
            return (cx - ax) * (by - ay) - (cy - ay) * (bx - ax)

        sx0 = x0 / zscale
        sy0 = y0 / zscale
        sx1 = x1 / zscale
        sy1 = y1 / zscale
        sx2 = x2 / zscale
        sy2 = y2 / zscale

        area = edge(sx0, sy0, sx1, sy1, sx2, sy2)
        if area == 0:
            return False

        visible = False
        for y in range(min_y, max_y + 1):
            row = zbuffer[y]
            py = y + 0.5
            for x in range(min_x, max_x + 1):
                px = x + 0.5
                w0 = edge(sx1, sy1, sx2, sy2, px, py)
                w1 = edge(sx2, sy2, sx0, sy0, px, py)
                w2 = edge(sx0, sy0, sx1, sy1, px, py)

                if (w0 >= 0 and w1 >= 0 and w2 >= 0) or (w0 <= 0 and w1 <= 0 and w2 <= 0):
                    w0 /= area
                    w1 /= area
                    w2 /= area
                    z = (z0 * w0) + (z1 * w1) + (z2 * w2)
                    if z < row[x]:
                        row[x] = z
                        visible = True

        return visible

    def tick(self):
        self.clear_screen()
        self.camera.tick()
        for shape in self._shapes:
            shape.draw()
        self.render_triangles()
        self.player.update()
        self.zlayer_screen()

    def run(self):
        if self._main_function is not None:
            self._main_function()
        self.utils.run()
        if self.utils.is_web():
            self.warning()
