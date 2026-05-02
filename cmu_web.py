

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
    def normal(self):
        mag = math.sqrt((self.x*self.x)+ (self.y*self.y) + (self.z*self.z))
        if mag == 0:
            return Vector3(0,0,0)
        return Vector3.new(self.x/mag, self.y/mag, self.z/mag)
    @property
    def offscreen(self) -> bool:
        BUFFER=150
        if self.screen is None:
            return True
        x,y=self.screen if self.screen is not None else (-999999999999, -1)
        return (x < -BUFFER or x > 400+BUFFER) or (y < -BUFFER or y > 400+BUFFER)
    @property
    def screen(self, width=400, height=400) -> tuple[int, int]:
        focal = 150
        camera_offset = 0
        z = self.z + camera_offset
        if z <= 0:
            return (-1, -1)
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

    def rotate(self, angle):
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



# ===== engine/light.py =====

from cmu_graphics import rgb

lights: list["Light"] = []
class Light():
    __slots__ = ("position", "brightness", "color", "direction")
    def __init__(self, position: Vector3, direction: Vector3, brightness: float = 1, color=rgb(255,255,255)):
        self.position = position
        self.brightness = brightness
        self.color = color
        self.direction = direction
        lights.append(self)


# ===== engine/triangle.py =====

from typing import TYPE_CHECKING


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
                invalid_points += 1
                self.points[i].z = 1
        
        if invalid_points >= len(self.points):
            return
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
        if ar < 180:
            return
        #calculate color  
        self._real_fill = fill.darker().darker().darker().darker().darker()
        if existing_game.configuration.shading:
            normal = self.center.normal
            closest_light: Light | None = None
            closest_dist = 9999999999999999
            for light in lights:
                ds=light.position.distance(self.position)
                if ds < closest_dist:
                    closest_dist = ds
                    closest_light = light
            if closest_light is not None:
                light_dir = closest_light.position
                light_dir = light_dir.normal + closest_light.direction
                ambient = 0.4
                diffuse = max(0, normal.dot(existing_game.camera.direction))
                brightness = ambient + (1 - ambient) * diffuse
                self._real_fill = rgb(fill.red * brightness,fill.blue * brightness,fill.green* brightness)


        
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
            self.position += self.velocity
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

from cmu_graphics import Polygon

class PolygonFactory:
    def __init__(self, size: int = 2000) -> None:
        self._pool: list[Polygon] = [
            Polygon(0, 0, 0, 0, 0, 0, visible=False)
            for _ in range(size)
        ]

        self._free: list[Polygon] = self._pool.copy()
        self._in_use: set[Polygon] = set()

    def reserve(self) -> Polygon:
        if not self._free:
            raise RuntimeError("Polygon pool exhausted")

        poly = self._free.pop()
        self._in_use.add(poly)

        poly.visible = True
        return poly

    def free(self, poly: Polygon) -> None:
        if poly not in self._in_use:
            raise RuntimeError("Tried to free polygon that is not currently reserved")

        self._in_use.remove(poly)
        self._free.append(poly)

        poly.visible = False


# ===== engine/_game.py =====

import math
from typing import TYPE_CHECKING

from cmu_graphics import *



utils: "CMUtils" = CMUtils()
class Game():
    class GameConfiguration():
        wireframe: bool = False
        max_triangles: int = 1950
        shading: bool = True
        quality: float = 0.75  #increase for worse quality
        cmu_quality: float = 0.125 #for CMU WEB only
        fps_target: int = 30

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
        app.group.clear()
        for tri in self.triangles:
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
        self.player.update()


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


# ===== main.py =====

import sys,math
import time



from cmu_graphics import * # pyright: ignore[reportWildcardImportFromLibrary]
app.stepsPerSecond = 9999999 






def renderCube(position = Vector3.new(0,-50,100), size = Vector3.new(50, 50, 50), fill=rgb(0,0,0)):
    d=0
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
                v.x * size.x / 2,
                v.y * size.y / 2,
                v.z * size.z / 2
            )
        )

    faces = [
        (0,1,2), (0,2,3),  # back
        (4,5,6), (4,6,7),  # front
        (0,1,5), (0,5,4),  # bottom
        (2,3,7), (2,7,6),  # top
        (1,2,6), (1,6,5),  # right
        (0,3,7), (0,7,4),  # left
    ]



    for face in faces:
        scale = 1
    
        v1 = scaled_vertices[face[0]]*scale#.rotate_x(math.radians(posX)).rotate_y(math.radians(posX)).rotate_z(math.radians(posX)) * scale
        v2 = scaled_vertices[face[1]]*scale#.rotate_x(math.radians(posX)).rotate_y(math.radians(posX)).rotate_z(math.radians(posX)) * scale
        v3 = scaled_vertices[face[2]]*scale#.rotate_x(math.radians(posX)).rotate_y(math.radians(posX)).rotate_z(math.radians(posX)) * scale

        Triangle(position,v1,v2,v3,fill=fill)

def renderSphere(position = Vector3.new(100,100,0), radius=50, color=rgb(255,255,255)):
    vertices = []
    lat_steps = math.ceil(5 * game.configuration.quality)
    lon_steps = math.ceil(30 * (game.configuration.quality/8))



    for i in range(lat_steps + 1):
        theta = i / lat_steps * math.pi
        for j in range(lon_steps + 1):
            phi = j / lon_steps * 2 * math.pi

            x = radius * math.sin(theta) * math.cos(phi)
            y = radius * math.cos(theta)
            z = radius * math.sin(theta) * math.sin(phi)

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
        v1 = vertices[face[0]].rotate_x(math.radians((position.x / 400) * 360))
        v2 = vertices[face[1]].rotate_x(math.radians((position.x / 400) * 360))
        v3 = vertices[face[2]].rotate_x(math.radians((position.x / 400) * 360))
        Triangle(position, v1, v2, v3, fill=color)


app.dt = 0.016
app.fpsLabel = Label("FPS: 0", 370, 20)
app.triangleLabel = Label("Triangles: 0", 360, 50)

posX = 0





fps_trend: list[float] = []
dt_ema = 1 / game.configuration.fps_target
#i = Image("/home/moakdoge/Downloads/Pipoya RPG Tileset 32x32/LightShadow_pipo.png", 50, 50)
#print(i._shape.__dict__)
def onStep():
    global MAX_AREA, dt_ema
    start = time.perf_counter()
    game.camera.tick()
    global posX

    
    game.clear_screen()
    renderSphere(Vector3.new(0,0,100), color=rgb(255,0,0))
    renderSphere(Vector3.new(0,0,300), color=rgb(0,255,0),radius=100)
    renderSphere(Vector3.new(0,0,700), color=rgb(0,0,255),radius=200)
    #renderCube(size=Vector3.new(500, 50, 50))
    game.zlayer_screen()
    game.tick()
    posX += 1

    app.dt = max(0.0001, time.perf_counter() - start)
    game.fps = math.floor(1/app.dt)
    fps_trend.append(app.dt)
    if len(fps_trend) > 600:
        fps_trend.pop(0)

    target_dt = 1 / game.configuration.fps_target
    dt_ema = (dt_ema * 0.9) + (app.dt * 0.1)
    performance_ratio = target_dt / dt_ema

    
    
    RANGE = 0.05

    if posX %4 == 0 :
        if performance_ratio < (1-RANGE): # below target FPS
            game.configuration.quality *= max(0.90, 1 - (0.985 - performance_ratio) * 0.18)
        elif performance_ratio > (1+RANGE): # above target FPS
            game.configuration.quality *= min(1.08, 1 + (performance_ratio - 1.015) * 0.12)

        game.configuration.quality = max(0.25, min(4.0, game.configuration.quality))

        print(f"Q:{game.configuration.quality:.3f} FPS:{(1 / dt_ema):.1f} TARGET:{game.configuration.fps_target}")

    #okay.
    MAX_AREA = 180 / (game.configuration.quality*2)

    #print(MAX_AREA, min(fps_trend))
    app.fpsLabel.value = f"FPS: {rounded(1/app.dt)}"
    app.triangleLabel.value = f"Triangles: {game._triangle_count}"
    app.fpsLabel.toFront()
    app.triangleLabel.toFront()




game.utils.run()