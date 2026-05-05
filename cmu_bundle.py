### CREATED BY @MOAKDOGE ###
### CREATED ON: 05/05/26 ###


# ===== engine/vector3.py =====

import math


class Vector3():
    __slots__ = ("x", "y", "z")
    def __init__(self, x, y, z) -> None:
        self.x=x
        self.y=y
        self.z=z
    @classmethod
    def new(cls, x,y,z):
        return cls(x=x,y=y,z=z)
    @classmethod
    def zero(cls) -> "Vector3":
        return cls(x=0,y=0,z=0)

    @property
    def magnitude(self):
        return math.hypot(self.x, self.y, self.z)
    @property
    def normal(self):
        mag = math.sqrt((self.x*self.x)+ (self.y*self.y) + (self.z*self.z))
        if mag == 0:
            return Vector3(0,0,0)
        return Vector3.new(self.x/mag, self.y/mag, self.z/mag)
    @property
    def offscreen(self) -> bool:
        BUFFER=100
        if self.screen is None:
            return True
        x,y=self.screen if self.screen is not None else (-999999999999, -1)
        return (x < -BUFFER or x > 400+BUFFER) or (y < -BUFFER or y > 400+BUFFER)
    @property
    def screen(self, width=400, height=400) -> tuple[int, int]:
        focal = 180
        camera_offset = 0
        z = self.z + camera_offset
        aspect = height / width
        screen_x = (self.x / z) * focal + width / 2
        screen_y = -(self.y / z) * focal * aspect + height / 2  # flip Y
        return screen_x, screen_y

    #operators
    def __mul__(self, other):
        # v * number
        if isinstance(other, (int, float)):
            return Vector3(
                self.x * other,
                self.y * other,
                self.z * other
            )
        raise TypeError("Can only multiply Vector3 by scalar")
    def __add__(self, other: "Vector3") -> "Vector3":
        if isinstance(other, Vector3):
            return Vector3(
                self.x + other.x,
                self.y + other.y,
                self.z + other.z
            )
    def __sub__(self, other: "Vector3") -> "Vector3":
        if isinstance(other, Vector3):
            return Vector3(
                self.x - other.x,
                self.y - other.y,
                self.z - other.z
            )
        
    def __repr__(self) -> str:
        return f"({math.ceil(self.x)}, {math.ceil(self.y)}, {math.ceil(self.z)})"
    def __str__(self) -> str:
        return self.__repr__()
    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)
    

    #math functions
    def _qscos(self, angle):
        s = math.sin(angle)
        c = math.cos(angle)
        return s, c

    def rotate_x(self, angle):
        sin_theta, cos_theta = self._qscos(angle)
        y = self.y * cos_theta - self.z * sin_theta
        z = self.y * sin_theta + self.z * cos_theta
        return Vector3(self.x, y, z)

    def rotate_y(self, angle):
        sin_theta, cos_theta = self._qscos(angle)
        x = self.x * cos_theta + self.z * sin_theta
        z = -self.x * sin_theta + self.z * cos_theta
        return Vector3(x, self.y, z)

    def rotate_z(self, angle):
        sin_theta, cos_theta = self._qscos(angle)
        x = self.x * cos_theta - self.y * sin_theta
        y = self.x * sin_theta + self.y * cos_theta
        return Vector3(x, y, self.z)

    def rotate(self, angle: "Vector3"):
        m = self.rotate_y(angle.y)
        m = m.rotate_x(angle.x)
        m = m.rotate_z(angle.z)
        return m
    def rotate_xyz(self, angle):
        sin_theta, cos_theta = self._qscos(angle)

        #rotate x
        y = self.y * cos_theta - self.z * sin_theta
        z = self.y * sin_theta + self.z * cos_theta

        #rotate y
        x = self.x * cos_theta + z * sin_theta
        z = -self.x * sin_theta + z * cos_theta

        #rotate z
        x = x * cos_theta - y * sin_theta
        y = x * sin_theta + y * cos_theta

        return Vector3.new(x,y,z)
    
    def cross(self, other):
        return Vector3(
            self.y * other.z - self.z * other.y,  # i
            self.z * other.x - self.x * other.z,  # j
            self.x * other.y - self.y * other.x   # k
        )
    
    def distance(self, other):
        return math.sqrt((other.x-self.x)**2+(other.y-self.y)**2+(other.z-self.z)**2)
    
    def dot(self, b):
        return self.x * b.x + self.y * b.y + self.z * b.z


    def intersect_near(self, b: "Vector3") -> "Vector3":
        # edge a -> b crosses z = NEAR
        NEAR = 1.0
        a = self
        t = (NEAR - a.z) / (b.z - a.z)
        return a + (b - a) * t


# ===== engine/light.py =====

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


# ===== engine/camera.py =====

import math



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
        self.light.direction = Vector3.new(0, 0, self.yaw)
    @property
    def direction(self):
        return Vector3(
                math.sin(self.yaw) * math.cos(self.pitch),
                -math.sin(self.pitch),
                math.cos(self.yaw) * math.cos(self.pitch)
                ).normal
    def __setattr__(self, name: str, value) -> None:
        if name == "pitch":
            value = max(math.radians(-90), min(math.radians(90), value))
        object.__setattr__(self, name, value)

    def __repr__(self) -> str:
        st = f'Camera(position={self.position.__repr__()},yaw={math.ceil(math.degrees(self.yaw))},pitch={math.ceil(math.degrees(self.pitch))},roll={math.ceil(math.degrees(self.roll))})'
        return st


# ===== engine/player.py =====

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




# ===== engine/triangle.py =====

from typing import TYPE_CHECKING


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
        if existing_game.configuration.shading and render_lights:
            p1, p2, p3 = tuple(self.points)
            normal = (p2 - p1).cross(p3 - p1).normal

            ambient = 0.25
            brightness = ambient

            for light in lights:
                # Transform light position into view space for consistent lighting
                light_pos = light.position - existing_game.camera.position
                light_pos = light_pos.rotate(
                    Vector3.new(existing_game.camera.pitch, existing_game.camera.yaw, 0)
                )
                # Direction from surface to light
                light_dir = (light_pos - self.center).normal

                # Lambert diffuse
                diffuse = max(0.0, normal.dot(light_dir))

                # Optional distance falloff
                dist = light_pos.distance(self.center)
                attenuation = 1.0 / (1.0 + 0.001 * dist * dist)

                brightness += diffuse * light.brightness * attenuation

            brightness = min(1.0, brightness)

            self._real_fill = rgb(
                int(fill.red * brightness),
                int(fill.green * brightness),
                int(fill.blue * brightness),
            )




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


# ===== engine/cmu_utils.py =====


import sys
from typing import TYPE_CHECKING, Literal


if TYPE_CHECKING:
    from engine._game import Game
class CMUtils():
    _game: "Game"
    

    def __init__(self) -> None:
        self._globals: dict = {}
    @staticmethod
    def register_game(obj) -> "Game":
        CMUtils._game: "Game" = obj
        return obj

    def make_global(self, obj, name=None):
        def wrapper(*args, **kwargs):
            return CMUtils._game.__class__.__dict__[obj.__name__](
                CMUtils._game,
                *args,
                **kwargs
            )
        self._globals[name or obj.__name__] = wrapper
        return obj

    @staticmethod
    def is_web() -> Literal[False]:
        return (sys.implementation.name == "brython") # type: ignore

    @classmethod
    def is_desktop(cls) -> Literal[True]:
        return (sys.implementation.name == "cpython") # pyright: ignore[reportReturnType]
    
    def run(self):
        if self.is_desktop():
            main=sys.modules["__main__"]
            for glob, func in self._globals.items():
                setattr(main, glob, func)
            from cmu_graphics import cmu_graphics
            cmu_graphics.run() # type: ignore
        else:
    
            for glob, func in self._globals.items():
                globals()[glob] = func


# ===== engine/polygon_factory.py =====

import math
from re import L

from cmu_graphics import Polygon

class PolygonFactory:
    def __init__(self, size: int = 2000) -> None:
        self._pool: list[Polygon]
        self.regen(size)
        self._free: list[Polygon] = self._pool.copy()
        self._in_use: set[Polygon] = set()

    def regen(self, size: int):
        self._pool = [
            Polygon(0, 0, 0, 0, 0, 0, visible=False)
            for _ in range(size)
        ]
        self._free = self._pool.copy()
        self._in_use = set()

    def reserve(self) -> Polygon:
        if not self._free:
            self.regen(math.floor(len(self._pool) * 1.5))

        poly = self._free.pop()
        self._in_use.add(poly)

        
        return poly

    def free(self, poly: Polygon) -> None:
        if poly not in self._in_use:
            #poly.visible = False
            return
           # raise RuntimeError("Tried to free polygon that is not currently reserved")

        self._in_use.remove(poly)
        self._free.append(poly)

        #poly.visible = False


# ===== engine/_game.py =====

import math
import time
from typing import TYPE_CHECKING, Callable

from cmu_graphics import *



utils: "CMUtils" = CMUtils()
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
        quality: float = 0.4  #increase for worse quality
        cmu_quality: float = 0.125 #for CMU WEB only
        fps_target: int = 30
        min_quality: float = 0.25 if utils.is_desktop() else 0.01

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
        self.sun = Light(Vector3.new(900, 900, 900), direction=Vector3.new(-900, -900, -900), brightness=1500)
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

    @utils.make_global
    def onKeyHold(self, key):
        forward = self.camera.direction
        forward.x *= -1
        forward.y = 0
        right = Vector3(forward.z, 0, -forward.x).normal
        speed = 60
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

        ### DEBUG ###
        if not self.configuration.debug:
            return
    
        if "q" == key:
            self.configuration.wireframe = not self.configuration.wireframe

    @utils.make_global
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
    
    def remove_triangle(self, triangle):
        if triangle in self.triangles:
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
            key=lambda tri: tri.z + (tri._sort_id * 1e-6) # type: ignore
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
        self.utils.run()
        if self._main_function is not None:
            self._main_function()


# ===== engine/__init__.py =====

game = Game()

if not game.utils.is_web():
    import sys
    for name, mod in sys.modules.items():
        if name == "engine.triangle":
            mod.existing_game = game # type: ignore
            break
else:
    existing_game = game


# ===== engine/shapes/__init__.py =====

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cmu_graphics.shape_logic import RGB
from cmu_graphics import rgb
class Base3DShape:
    def __init__(self, position: Vector3, size: Vector3, fill: "RGB | None" = None) -> None:
        self.position: Vector3 = position
        self.size: Vector3 = size
        self.fill: "RGB" = fill or rgb(255,0,0)
        self.rotation: Vector3 = Vector3.zero()
        game._shapes.append(self)

    def draw(self):
        raise NotImplementedError


# ===== engine/shapes/cube.py =====

import math
from typing import TYPE_CHECKING

from cmu_graphics import rgb

if TYPE_CHECKING:
    from cmu_graphics.shape_logic import RGB

class Cube(Base3DShape):
    def draw(self):
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
                    attenuation = 1.0 / (1.0 + 0.00025 * dist * dist)
                    brightness += diffuse * light.brightness * attenuation
            else:
                brightness = 1.0

            brightness = min(1.0, brightness)
            face_fill = rgb(
                int(self.fill.red * brightness),
                int(self.fill.green * brightness),
                int(self.fill.blue * brightness),
            )

            Triangle(self.position, v1, v2, v3, fill=self.fill, render_lights=False)
            Triangle(self.position, v1, v3, v4, fill=self.fill, render_lights=False)


# ===== engine/shapes/sphere.py =====

import math
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from cmu_graphics.shape_logic import RGB

class Sphere(Base3DShape):
    def __init__(self, position: Vector3, radius: float, fill: "RGB") -> None:
        super().__init__(position, Vector3.new(radius*2, radius*2, radius*2), fill=fill)
        self.radius = radius
        
    def draw(self):
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


# ===== main.py =====

from operator import pos
import sys,math
import time



from cmu_graphics import * # pyright: ignore[reportWildcardImportFromLibrary]
app.stepsPerSecond = 120 







@game.on_ready
def main():
    app.fpsLabel = Label("FPS: 0", 370, 20)
    app.triangleLabel = Label("Triangles: 0", 360, 50)

    sphere1 = Sphere(position=Vector3.new(0,0,400), fill=rgb(255,0,0), radius=100)
    cube1 = Cube(position=Vector3.new(800,-270,400), size=Vector3.new(2500, 250, 2500), fill=rgb(0,255,0))



@game.register_tick
def step(dt):
    #print(MAX_AREA, min(fps_trend))
    app.fpsLabel.value = f"FPS: {rounded(1/dt)}"
    app.triangleLabel.value = f"Triangles: {game._triangle_count}"
    app.fpsLabel.toFront()
    app.triangleLabel.toFront()


game.run()