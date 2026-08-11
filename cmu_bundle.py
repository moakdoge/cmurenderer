### CREATED BY @MOAKDOGE ###
### CREATED ON: 08/11/26 ###


# ===== engine/extras.py =====

from __future__ import annotations
from types import GenericAlias
from typing import Any, Callable, Generic, Type, TypeVar, dataclass_transform, overload
T = TypeVar('T')
R = TypeVar('R')
_NOT_FOUND = object()
class cached_property(Generic[T, R]):
    func: Callable[[T], R]
    attrname: str | None
    __doc__: str | None
    __module__: str
    def __init__(self, func: Callable[[T], R]) -> None:
        self.func = func
        self.attrname = None
        self.__doc__ = func.__doc__
        self.__module__ = func.__module__
    def __set_name__(self, owner: type[T], name: str) -> None:
        if self.attrname is None:
            self.attrname = name
        elif name != self.attrname:
            raise TypeError(f'Cannot assign the same cached_property to two different names ({self.attrname!r} and {name!r}).')
    @overload
    def __get__(self, instance: None, owner: type[T] | None=None) -> 'cached_property[T, R]':
        ...
    @overload
    def __get__(self, instance: T, owner: type[T] | None=None) -> R:
        ...
    def __get__(self, instance: T | None, owner: type[T] | None=None) -> 'R | cached_property[T, R]':
        if instance is None:
            return self
        if self.attrname is None:
            raise TypeError('Cannot use cached_property instance without calling __set_name__ on it.')
        try:
            cache: dict[str, Any] = instance.__dict__
        except AttributeError:
            msg = f"No '__dict__' attribute on {type(instance).__name__!r} instance to cache {self.attrname!r} property."
            raise TypeError(msg) from None
        val = cache.get(self.attrname, _NOT_FOUND)
        if val is _NOT_FOUND:
            val = self.func(instance)
            try:
                cache[self.attrname] = val
            except TypeError:
                msg = f"The '__dict__' attribute on {type(instance).__name__!r} instance does not support item assignment for caching {self.attrname!r} property."
                raise TypeError(msg) from None
        return val
    __class_getitem__ = classmethod(GenericAlias)
from typing import TypeVar, Type, Callable, Any
T = TypeVar('T')
@dataclass_transform()
def dataclass(init: bool=True, frozen: bool=False, slots: bool=False, repr: bool=True):
    def decorator(cls):
        nonlocal frozen, slots, repr
        annotations = getattr(cls, '__annotations__', {})
        fields = tuple(annotations.keys())
        defaults = {}
        if slots:
            namespace = dict(cls.__dict__)
            namespace.pop('__dict__', None)
            namespace.pop('__weakref__', None)
            for name in fields:
                if name in namespace:
                    defaults[name] = namespace.pop(name)
            f = list(fields)
            f.append('_frozen')
            namespace['__slots__'] = tuple(f)
            class DataMeta(type):
                def __repr__(cls):
                    pretty = []
                    tags = ['[FROZEN]' if frozen else '', '[SLOTS]' if slots else '', '[REPR]' if repr else '', '[INIT]' if init else '']
                    for k, v in annotations.items():
                        pretty.append(f'{k}: {v.__name__} = {defaults[k]}' if k in defaults else f"{k}: {getattr(v, '__name__', v)}")
                    return f"<dataclass {cls.__name__}({','.join(pretty)}) {' '.join(tags)}>"
            if repr:
                k = DataMeta
            else:
                k = type
            new_cls = k(cls.__name__, cls.__bases__, namespace)
            new_cls.__module__ = cls.__module__
            new_cls.__qualname__ = cls.__qualname__
            cls = new_cls
        annotations = getattr(cls, '__annotations__', {})
        fields = list(annotations.keys())
        def __init__(self, *args, **kwargs):
            for name, value in zip(fields, args):
                setattr(self, name, value)
            for name in fields[len(args):]:
                if name in kwargs:
                    setattr(self, name, kwargs[name])
                elif hasattr(cls, name):
                    if slots:
                        setattr(self, name, defaults[name])
                    else:
                        setattr(self, name, getattr(cls, name))
                else:
                    raise TypeError(f'Missing required argument: {name}')
            setattr(self, '_frozen', True)
            if hasattr(self, '__post_init__') and callable(getattr(self, '__post_init__', None)):
                self.__post_init__()
        def __repr__(self):
            values = ', '.join((f'{name}={getattr(self, name)!r}' for name in fields))
            return f'{cls.__name__}({values})'
        if init:
            cls.__init__ = __init__
        if repr:
            cls.__repr__ = __repr__
        if frozen:
            def __setattr__(self, k, v):
                if hasattr(self, '_frozen'):
                    raise AttributeError(f'{self.__class__.__name__} is frozen!')
                object.__setattr__(self, k, v)
            cls.__setattr__ = __setattr__
        return cls
    return decorator


# ===== engine/assets/asset_type.py =====

from enum import Enum
class AssetType(Enum):
    IMAGE = 0


# ===== engine/assets/asset.py =====

@dataclass(frozen=True, slots=True)
class Asset:
    desktop_path: str
    cmu_path: str
    asset_type: AssetType = AssetType.IMAGE


# ===== engine/_types.py =====

from typing import TypeAlias
Vector3Number: TypeAlias = float | int


# ===== engine/vector3.py =====

import math
_ZERO_VECTOR: 'Vector3 | None' = None
@dataclass(slots=True)
class Vector3:
    x: int | float
    y: int | float
    z: int | float
    @classmethod
    def new(cls, x, y, z):
        return cls(x=x, y=y, z=z)
    @classmethod
    def zero(cls) -> 'Vector3':
        return cls(x=0, y=0, z=0)
    @property
    def magnitude(self):
        return math.hypot(self.x, self.y, self.z)
    @property
    def normal(self):
        mag = self.magnitude
        if mag == 0:
            return Vector3(0, 0, 0)
        return Vector3.new(self.x / mag, self.y / mag, self.z / mag)
    @property
    def offscreen(self) -> bool:
        BUFFER = 100
        if self.screen is None:
            return True
        x, y = self.screen if self.screen is not None else (-999999999999, -1)
        return (x < -BUFFER or x > 400 + BUFFER) or (y < -BUFFER or y > 400 + BUFFER)
    @property
    def screen(self, width=400, height=400) -> tuple[int, int]:
        focal = 180
        camera_offset = 0
        z = self.z + camera_offset
        aspect = height / width
        screen_x = self.x / z * focal + width / 2
        screen_y = -(self.y / z) * focal * aspect + height / 2
        return (math.floor(screen_x), math.floor(screen_y))
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vector3(self.x * other, self.y * other, self.z * other)
        else:
            return Vector3(self.x * other.x, self.y * other.y, self.z * other.z)
        raise TypeError('Can only multiply Vector3 by scalar')
    def __add__(self, other: 'Vector3') -> 'Vector3':
        if isinstance(other, Vector3):
            return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    def __sub__(self, other: 'Vector3') -> 'Vector3':
        if isinstance(other, Vector3):
            return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    def __iadd__(self, other: 'Vector3'):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self
    def __isub__(self, other: 'Vector3'):
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self
    def __imult__(self, other: 'Vector3 | float | int'):
        if isinstance(other, Vector3):
            self.x *= other.x
            self.y *= other.y
            self.z *= other.z
        else:
            self.x *= other
            self.y *= other
            self.z *= other
        return self
    def __repr__(self) -> str:
        return f'Vector3({math.ceil(self.x)}, {math.ceil(self.y)}, {math.ceil(self.z)})'
    def __str__(self) -> str:
        return self.__repr__()
    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)
    def __pos__(self):
        return Vector3(+self.x, +self.y, +self.z)
    def _qscos(self, angle):
        s = math.sin(angle)
        c = math.cos(angle)
        return (s, c)
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
    def rotate(self, angle: 'Vector3'):
        x, y, z = (self.x, self.y, self.z)
        sx, cx = self._qscos(angle.x)
        sy, cy = self._qscos(angle.y)
        sz, cz = self._qscos(angle.z)
        x, z = (x * cy + z * sy, -x * sy + z * cy)
        y, z = (y * cx - z * sx, y * sx + z * cx)
        x, y = (x * cz - y * sz, x * sz + y * cz)
        return Vector3(x, y, z)
    def rotate_xyz(self, angle):
        sin_theta, cos_theta = self._qscos(angle)
        y = self.y * cos_theta - self.z * sin_theta
        z = self.y * sin_theta + self.z * cos_theta
        x = self.x * cos_theta + z * sin_theta
        z = -self.x * sin_theta + z * cos_theta
        x = x * cos_theta - y * sin_theta
        y = x * sin_theta + y * cos_theta
        return Vector3.new(x, y, z)
    def cross(self, other):
        return Vector3(self.y * other.z - self.z * other.y, self.z * other.x - self.x * other.z, self.x * other.y - self.y * other.x)
    def distance(self, other):
        return math.sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2 + (other.z - self.z) ** 2)
    def dot(self, b):
        return self.x * b.x + self.y * b.y + self.z * b.z
    def intersect_near(self, b: 'Vector3') -> 'Vector3':
        NEAR = 1.0
        a = self
        t = (NEAR - a.z) / (b.z - a.z)
        return a + (b - a) * t


# ===== engine/assets/asset_subsystem.py =====

from typing import TYPE_CHECKING
from cmu_graphics import Image
pass
@dataclass()
class AssetSubsystem:
    parent: 'Game'
    def load_asset(self, asset: Asset) -> str:
        return asset.cmu_path
        return asset.desktop_path
    def verify_asset(self, asset: Asset) -> bool:
        try:
            with open(f'{self.parent.utils.backend_url}{self.load_asset(asset)}', 'rb') as f:
                pass
        except FileNotFoundError as e:
            return False
        return True


# ===== engine/light.py =====

from cmu_graphics import rgb
lights: list['Light'] = []
class Light:
    __slots__ = ('position', 'brightness', 'color', 'direction')
    def __init__(self, position: Vector3, direction: Vector3, brightness: float=15, color=rgb(255, 255, 255)):
        self.position = position
        self.brightness = brightness
        self.color = color
        self.direction = direction
        lights.append(self)


# ===== engine/camera.py =====

import math
class Camera:
    def __init__(self, position: Vector3=Vector3(0, 0, 0)) -> None:
        self.position = position
        self.pitch: float = 0
        self.yaw: float = 0
        self.roll: float = 0
        self._x = 0
        self.light = Light(self.position, self.direction, brightness=60)
        pass
    def tick(self):
        self.light.position = self.position
        self.light.direction = Vector3.new(self.pitch, 0, self.yaw)
    @property
    def direction(self):
        return Vector3(math.sin(self.yaw) * math.cos(self.pitch), -math.sin(self.pitch), math.cos(self.yaw) * math.cos(self.pitch)).normal
    @property
    def ddir(self):
        yaw, pitch = (self.yaw, self.pitch)
        return Vector3(-math.sin(yaw) * math.cos(pitch), -math.sin(pitch), math.cos(yaw) * math.cos(pitch)).normal
    def __setattr__(self, name: str, value) -> None:
        if name == 'pitch':
            value = max(math.radians(-90), min(math.radians(90), value))
        object.__setattr__(self, name, value)
    def __repr__(self) -> str:
        st = f'Camera(position={self.position.__repr__()},yaw={math.ceil(math.degrees(self.yaw))},pitch={math.ceil(math.degrees(self.pitch))},roll={math.ceil(math.degrees(self.roll))})'
        return st


# ===== engine/color_utils.py =====

from typing import TYPE_CHECKING
from cmu_graphics import rgb
pass
def set_brightness(color: 'RGB', brightness: float) -> 'RGB':
    return rgb(color.red * brightness, color.green * brightness, color.blue * brightness)


# ===== engine/triangle.py =====

from typing import TYPE_CHECKING
from cmu_graphics import *
pass
existing_game: 'Game'
class Triangle:
    __slots__ = ('shadow', 'points', 'position', 'fill', '_count', '_real_fill', 'opacity', 'fogged', 'z', 'screen', 'extracted', '_shape', '_sort_id', 'average_screen_dist', '_og_points')
    def __init__(self, position: Vector3, *points: Vector3, rotate: Vector3 | None=None, fill=rgb(255, 255, 255), pretransformed: bool=False, render_lights: bool=True, skip_near_clip: bool=False, opacity: int=100, render_shadow: bool=True):
        self.shadow = None
        self._og_points: list[Vector3] = [*points]
        self.points: list[Vector3] = [*points]
        self.position = position
        self.fill = fill
        self._count = len(points)
        self._real_fill = fill
        self.opacity = opacity
        self.fogged = False
        if render_lights and existing_game.configuration.current.shading:
            self._real_fill = self.get_fill(fill)
        if render_shadow and existing_game.configuration.current.shadows:
            self.render_shadow()
        if not pretransformed:
            if rotate is not None:
                self.points = self.rotate_points(rotate)
            self.transform(existing_game.camera)
        clipped = self.get_clip(skip_near_clip)
        if not clipped:
            self.delete()
            return
        if len(clipped) > 1:
            existing_game.remove_triangle(self.shadow)
            self.shadow = None
            _, second = clipped
            Triangle(Vector3.zero(), *second, fill=self.fill, pretransformed=True, render_lights=True, skip_near_clip=True, opacity=opacity, render_shadow=False)
        self.points = list(clipped[0])
        self._count = len(self.points)
        self.z = self.get_z()
        self.screen = self.get_screens()
        self.extracted = self.get_extracted()
        existing_game.add_triangle(self)
        if not self.is_valid():
            self.delete()
            return
    def rotate_points(self, mat: Vector3):
        return [p.rotate(mat) for p in self.points]
    def is_valid(self) -> bool:
        statements = [self.is_too_small(), self.is_foggy(), self.is_offscreen()]
        return not any(statements)
    def get_z(self) -> float:
        z = max((_.z for _ in self.points))
        if self.opacity < 100:
            z -= 0.01
        return z
    def get_screens(self) -> list[tuple[int, int]]:
        return [_.screen for _ in self.points]
    def get_extracted(self):
        return [list(sublist) for sublist in self.screen]
    def is_foggy(self) -> bool:
        lowest = 140
        v = self.screen_area < lowest and self.physical_area < existing_game.configuration.current.minimum_physical_area_cull
        return v
    def is_too_small(self) -> bool:
        centScr = self.center.screen
        self.average_screen_dist = max((distance(_[0], _[1], centScr[0], centScr[1]) for _ in self.screen))
        ar = self.area(*self.screen)
        v = ar < 50 / existing_game.configuration.current.quality and self.physical_area < existing_game.configuration.current.minimum_physical_area_cull
        return v
    def is_offscreen(self) -> bool:
        if all((_.offscreen for _ in self.points)) and self.physical_area < 1:
            return True
        return False
    def transform(self, camera: 'Camera'):
        for i, p in enumerate(self.points):
            self.points[i] = p + self.position - camera.position
            self.points[i] = self.points[i].rotate(Vector3.new(camera.pitch, camera.yaw, 0))
    def get_fill(self, start: 'RGB') -> 'RGB':
        tmp_fill = set_brightness(start, 0.8)
        world_points = self.world_points
        world_center = self.world_center
        if existing_game.configuration.current.shading:
            face_normal = (world_points[1] - world_points[0]).cross(world_points[2] - world_points[0]).normal
            ambient = 0.35
            brightness = ambient
            for light in lights:
                light_dir = (light.position - world_center).normal
                diffuse = abs(face_normal.dot(light_dir))
                dist = light.position.distance(world_center)
                attenuation = 1.0 / (1.0 + 0.0025 * dist * dist)
                brightness += diffuse * light.brightness * attenuation
            brightness = max(0.0, min(1.0, brightness))
            tmp_fill = set_brightness(start, brightness)
        return tmp_fill
    def render_shadow(self):
        _p = [Vector3.new(p.x, -50, p.z) for p in self.points]
        self.shadow = Triangle(self.position - Vector3.new(0, 50, 0), *_p, fill=rgb(0, 0, 0), render_lights=False, skip_near_clip=False, opacity=25, render_shadow=False)
    @property
    def center(self):
        return Vector3.new(sum((_.x for _ in self.points)) / self._count, sum((_.y for _ in self.points)) / self._count, sum((_.z for _ in self.points)) / self._count)
    @property
    def world_points(self):
        return [p + self.position for p in self.points]
    def get_clip(self, skip: bool=False):
        return [tuple(self.points)] if skip else self.clip_near()
    @property
    def world_center(self):
        world_points = self.world_points
        return Vector3.new(sum((p.x for p in world_points)) / len(world_points), sum((p.y for p in world_points)) / len(world_points), sum((p.z for p in world_points)) / len(world_points))
    def draw(self):
        self._shape = existing_game.polygon_factory.reserve()
        self._shape.pointList = self.extracted
        self._shape.fill = self._real_fill
        self._shape.zindex = self.z
        if self.opacity == 100:
            self._shape.border = self._real_fill
        else:
            self._shape.border = None
        if existing_game.configuration.debug.wireframe:
            self._shape.fill = None
        self._shape.opacity = self.opacity
        self._shape.visible = True
        self._sort_id = 1 if self.opacity == 100 else -9
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
        a, b = inside
        c = outside[0]
        ac = a.intersect_near(c)
        bc = b.intersect_near(c)
        return [(a, b, ac), (b, bc, ac)]
    def delete(self):
        if hasattr(self, 'shadow'):
            existing_game.remove_triangle(self.shadow)
        if hasattr(self, '_shape'):
            existing_game.polygon_factory.free(self._shape)
            self._shape.visible = False
        existing_game.remove_triangle(self)
    def area(self, p1, p2, p3):
        return abs((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0]))
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

import random
import sys
from typing import TYPE_CHECKING, Literal
from cmu_graphics import rgb
pass
class CMUtils:
    _game: 'Game'
    def __init__(self) -> None:
        self._globals: dict = {}
        self.locked_mouse = False
    @staticmethod
    def register_game(obj) -> 'Game':
        CMUtils._game: 'Game' = obj
        return obj
    @property
    def cmu_graphics(self):
        pass
        return None
    @property
    def version(self):
        with open('https://s3.amazonaws.com/cmu-cs-academy.lib.prod/desktop-cmu-graphics/version.txt', 'r') as f:
            return f.read()
    def make_global(self, name=None, desktop: bool=True, web: bool=True):
        def decorator(func):
            def wrapper(*args, **kwargs):
                return CMUtils._game.__class__.__dict__[func.__name__](CMUtils._game, *args, **kwargs)
            if not desktop and False:
                return func
            if not web and True:
                return func
            self._globals[name or func.__name__] = wrapper
            return func
        return decorator
    @staticmethod
    def is_web() -> Literal[False]:
        return sys.implementation.name == 'brython' or '__BRYTHON__' in globals()
    @staticmethod
    def is_desktop() -> Literal[True]:
        return sys.implementation.name == 'cpython'
    def run(self):
        for glob, func in self._globals.items():
            globals()[glob] = func
    def lock_mouse(self):
        pass
        self.locked_mouse = True
    def unlock_mouse(self):
        pass
        self.locked_mouse = False
    def random_color(self) -> 'RGB':
        rng1, rng2, rng3 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        return rgb(rng1, rng2, rng3)
    @property
    def backend_url(self):
        return 'https://backend.academy.cs.cmu.edu/get-image/?url='
        return ''


# ===== engine/ray.py =====

@dataclass(frozen=True, slots=True)
class Ray:
    position: 'Vector3'
    direction: 'Vector3'
    distance: float = float('inf')
    def intersects(self, tri: Triangle) -> float | None:
        EPS = 1e-06
        p1, p2, p3 = tri._og_points
        p1 = p1 + tri.position
        p2 = p2 + tri.position
        p3 = p3 + tri.position
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
        if t <= EPS or t > self.distance:
            return None
        return t
    def cast(self) -> Triangle | None:
        game = CMUtils._game
        for tri in game.triangles:
            if self.intersects(tri):
                return tri
        return None


# ===== engine/player.py =====

import math
from typing import TYPE_CHECKING
from cmu_graphics import app
pass
class Player:
    def __init__(self, camera: Camera) -> None:
        self.attached_camera = camera
        self.position: Vector3 = Vector3.zero()
        self.velocity: Vector3 = Vector3.new(0, 0, 0)
        self.max_health = 100
        self._game_parent: 'Game'
        self.health = 100
    def __setattr__(self, name: str, value) -> None:
        if name == 'position':
            self.attached_camera.position = value
        object.__setattr__(self, name, value)
    def on_floor(self):
        return self.position.y <= 0
    def check_collision(self, vel: Vector3) -> bool:
        dst = math.hypot(vel.x, vel.y, vel.z)
        if dst <= 0:
            return False
        dir = Vector3(vel.x / dst, vel.y / dst, vel.z / dst)
        r = Ray(self.position, dir, dst * 2)
        return r.cast() is not None
    def update(self):
        s = 48
        self.collider = Triangle(self.position, Vector3(-s, 0, 0), Vector3(s, 0, 0), Vector3(0, s * 2, 0), render_shadow=False, render_lights=False, opacity=1)
        if abs(self.velocity.x > 0) or abs(self.velocity.y) > 0 or (abs(self.velocity.z) > 0 and self._game_parent.configuration.current.collisions):
            move = self.velocity * app.dt
            for axis_move in (Vector3(move.x, 0, 0), Vector3(0, move.y, 0), Vector3(0, 0, move.z)):
                if axis_move.magnitude <= 0:
                    continue
                if not self.check_collision(axis_move):
                    self.position += axis_move
                else:
                    if axis_move.x:
                        self.velocity.x = 0
                    if axis_move.y:
                        self.velocity.y = 0
                    if axis_move.z:
                        self.velocity.z = 0
        self.velocity -= Vector3.new(0, 32, 0)
        self.velocity *= 0.95
        if self.position.y < 0:
            self.position.y = 0
    def jump(self):
        self.velocity += Vector3.new(0, 140, 0)


# ===== engine/polygon_factory.py =====

import math
from re import L
from cmu_graphics import Polygon
class PolygonFactory:
    def __init__(self, size: int=200) -> None:
        self._pool: list[Polygon]
        self.regen(size)
        self._free: list[Polygon] = self._pool.copy()
        self._in_use: set[Polygon] = set()
    def regen(self, size: int):
        self._pool = []
        for _ in range(size):
            new_poly = Polygon(0, 0, 0, 0, 0, 0, visible=False)
            new_poly._shape._skip = True
            self._pool.append(new_poly)
        self._free = self._pool.copy()
        self._in_use = set()
    def reserve(self) -> Polygon:
        if not self._free:
            self.regen(math.floor(len(self._pool) * 1.5))
        poly = self._free.pop()
        self._in_use.add(poly)
        poly._shape._skip = False
        return poly
    def free(self, poly: Polygon) -> None:
        if poly not in self._in_use:
            return
        self._in_use.remove(poly)
        self._free.append(poly)
        poly._shape._skip = True


# ===== engine/_game.py =====

import math
import time
from typing import TYPE_CHECKING, Callable
from cmu_graphics import *
utils: 'CMUtils' = CMUtils()
pass
class Game:
    def __init__(self):
        global utils
        pass
        self.utils = utils
        utils.register_game(self)
        self.camera = Camera()
        self.player = Player(self.camera)
        self.player._game_parent = self
        self.configuration: 'GameConfiguration'
        self.triangles: list[Triangle] = []
        self.renderables: list = []
        self._triangle_count = 0
        self._triangle_seq = 0
        self.assets = AssetSubsystem(self)
        self.polygon_factory: 'PolygonFactory' = PolygonFactory(3)
        self.fps = 30
        self._shapes: list['Base3DShape'] = []
        self.sun = Light(Vector3.new(900, 900, 900), direction=Vector3.new(-900, -900, -900), brightness=15)
        self._last_dt = time.perf_counter()
        self._events: dict[str, list] = {}
        self._main_function: Callable | None = None
        self.frames = 0
        app.inspectorEnabled = False
    def register_tick(self, func):
        if not 'tick' in self._events:
            self._events['tick'] = []
        self._events['tick'].append(func)
        return func
    def on_ready(self, func: Callable):
        self._main_function = func
        return func
    def warning(self):
        lines = ['WARNING! You are on CMU Web!', '', 'Performance is much, much worse then on the desktop version and some features may be unsupported!']
        print('\n'.join(lines))
    @utils.make_global(web=False)
    def onMouseMove(self, x, y):
        if self.utils.locked_mouse:
            import pygame
            pygame.event.pump()
            rx, ry = pygame.mouse.get_rel()
            self.camera.yaw += rx * app.dt * -1
            self.camera.pitch += ry * app.dt * -1
    @utils.make_global()
    def onKeyHold(self, keys):
        forward = self.camera.direction
        forward.x *= -1
        forward.y = 0
        right = Vector3(forward.z, 0, -forward.x).normal
        speed = 16
        if 'w' in keys:
            self.player.velocity += forward * speed * 1
        if 's' in keys:
            self.player.velocity += forward * speed * -1
        if 'a' in keys:
            self.player.velocity += right * speed * -1
        if 'd' in keys:
            self.player.velocity += right * speed * 1
        speed = math.radians(60) * 2
        for key in keys:
            if 'up' == key:
                self.camera.pitch += speed * app.dt
            if 'down' == key:
                self.camera.pitch -= speed * app.dt
            if 'right' == key:
                self.camera.yaw -= speed * app.dt
            if 'left' == key:
                self.camera.yaw += speed * app.dt
            if 'space' == key:
                self.player.jump()
    @utils.make_global()
    def onKeyPress(self, key: str):
        if not self.configuration.debug:
            return
        if 'q' == key:
            self.configuration.debug.wireframe = not self.configuration.debug.wireframe
        if 'z' == key:
            self.utils.unlock_mouse()
        if 'x' == key:
            self.utils.lock_mouse()
    @utils.make_global()
    def onStep(self):
        _dt = time.perf_counter() - self._last_dt
        self._last_dt = time.perf_counter()
        self.tick()
        self.fps = 1 / _dt
        app.dt = _dt
        for fn in self._events.get('tick', []):
            start = time.perf_counter()
            fn(_dt)
            end = time.perf_counter()
            print(f'{fn.__name__} took {(end - start) * 1000:.2f}ms')
            pass
        self.frames += 1
        pass
    def add_triangle(self, triangle):
        self._triangle_seq += 1
        triangle._sort_id = self._triangle_seq
        self.triangles.append(triangle)
        self._triangle_count += 1
    def remove_triangle(self, triangle: 'Triangle | None'):
        if triangle in self.triangles:
            if hasattr(triangle, '_shape'):
                self.polygon_factory.free(triangle._shape)
                triangle._shape.visible = False
            self.triangles.remove(triangle)
            self._triangle_count -= 1
    def clear_screen(self):
        for tri in self.triangles[:]:
            tri.delete()
        self._triangle_count = 0
        self._triangle_seq = 0
    def zlayer_screen(self):
        tri = self.triangles.copy()
        tri.extend(self.renderables)
        sorted_triangles = sorted(tri, reverse=True, key=lambda tri: tri.z + tri._sort_id * 1e-06 + 4 * (tri.opacity == 100))
        for tri in sorted_triangles:
            if not hasattr(tri, '_shape'):
                continue
            tri._shape.toFront()
    def render_triangles(self):
        zbuffer = None
        zwidth = 0
        zheight = 0
        zscale = max(1, int(self.configuration.current.zbuffer_size))
        if self.configuration.current.zbuffer_enabled:
            zwidth = max(1, 400 // zscale)
            zheight = max(1, 400 // zscale)
            zbuffer = [[float('inf')] * zwidth for _ in range(zheight)]
        sorted_triangles = sorted(self.triangles, reverse=True, key=lambda tri: tri.physical_area * tri.screen_area)
        pass
        try:
            for triangle in sorted_triangles:
                if zbuffer is not None and (not self._zbuffer_test(triangle, zbuffer, zwidth, zheight, zscale)):
                    continue
                triangle.draw()
        finally:
            pass
    def _zbuffer_test(self, triangle: Triangle, zbuffer: list[list[float]], zwidth: int, zheight: int, zscale: int) -> bool:
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
                if w0 >= 0 and w1 >= 0 and (w2 >= 0) or (w0 <= 0 and w1 <= 0 and (w2 <= 0)):
                    w0 /= area
                    w1 /= area
                    w2 /= area
                    z = z0 * w0 + z1 * w1 + z2 * w2
                    if z < row[x]:
                        row[x] = z
                        visible = True
        return visible
    def tick_renderables(self):
        for renderable in self.renderables:
            if hasattr(renderable, 'tick'):
                renderable.tick()
    def tick(self):
        self.clear_screen()
        self.camera.tick()
        for shape in self._shapes:
            shape._draw()
        self.render_triangles()
        if self.configuration.current.process_sprites:
            self.tick_renderables()
        self.player.update()
        self.zlayer_screen()
    def run(self):
        if self._main_function is not None:
            self._main_function()
        self.utils.run()
        self.warning()


# ===== engine/config.py =====

@dataclass(slots=True)
class DebugConfiguration:
    debug: bool = True
    wireframe: bool = False
@dataclass(slots=True)
class PerformanceConfiguration:
    minimum_physical_area_cull: int = 5000
    zbuffer_enabled: bool = True
    zbuffer_size: int = 4
    max_triangles: int = 195
    shading: bool = True
    quality: float = 0.8
    shadows: bool = False
    collisions: bool = True
    process_sprites: bool = False
@dataclass(slots=True)
class GameConfiguration:
    debug: DebugConfiguration = DebugConfiguration()
    web: PerformanceConfiguration = PerformanceConfiguration(zbuffer_size=8, max_triangles=400, shading=False, quality=0.25, shadows=False, collisions=False)
    desktop: PerformanceConfiguration = PerformanceConfiguration()
    @property
    def current(self) -> PerformanceConfiguration:
        pass
        return self.web
    '\n    min_physical_area_cull: int = 50_000\n    backface_cull: bool = False\n    zbuffer: bool = True\n    zbuffer_scale: int = 6 if utils.is_desktop() else 18\n    fog: float = 1.25 #the strength of the fog\n    max_triangles: int = 1950\n    shading: bool = True\n    quality: float = 0.8  #increase for worse quality\n    cmu_quality: float = 0.125 #for CMU WEB only\n    fps_target: int = 30\n    min_quality: float = 0.25 if utils.is_desktop() else 0.01\n    shadows: bool = utils.is_desktop()\n    '


# ===== engine/__init__.py =====

game = Game()
if not True:
    import sys
    for name, mod in sys.modules.items():
        if name == 'engine.triangle':
            mod.existing_game = game
            break
else:
    existing_game = game
game.configuration = GameConfiguration()


# ===== engine/shapes/__init__.py =====

from typing import TYPE_CHECKING
pass
from cmu_graphics import rgb
class Base3DShape:
    def __init__(self, position: Vector3, size: Vector3, fill: 'RGB | None'=None) -> None:
        self.position: Vector3 = position
        self.size: Vector3 = size
        self.fill: 'RGB' = fill or rgb(255, 0, 0)
        self.rotation: Vector3 = Vector3.zero()
        self.valid = True
        game._shapes.append(self)
    def _draw(self):
        size, position = (self.size, self.position)
        ds = position.distance(game.camera.position)
        sz = ds - max(size.x, size.y, size.z)
        if sz > 800 * game.configuration.current.quality:
            return
        self.draw()
    def draw(self):
        raise NotImplementedError


# ===== engine/shapes/cube.py =====

import math
from typing import TYPE_CHECKING
from cmu_graphics import Circle, rgb
pass
class Cube(Base3DShape):
    def draw(self):
        if not self.valid:
            return
        vertices = [Vector3(-1, -1, -1), Vector3(1, -1, -1), Vector3(1, 1, -1), Vector3(-1, 1, -1), Vector3(-1, -1, 1), Vector3(1, -1, 1), Vector3(1, 1, 1), Vector3(-1, 1, 1)]
        scaled_vertices = []
        for v in vertices:
            scaled_vertices.append(Vector3(v.x * self.size.x / 2, v.y * self.size.y / 2, v.z * self.size.z / 2))
        faces = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (1, 2, 6, 5), (0, 3, 7, 4)]
        for face in faces:
            scale = 1
            v1 = scaled_vertices[face[0]] * scale
            v2 = scaled_vertices[face[1]] * scale
            v3 = scaled_vertices[face[2]] * scale
            v4 = scaled_vertices[face[3]] * scale
            Triangle(self.position, v1, v2, v3, fill=self.fill, rotate=self.rotation)
            Triangle(self.position, v1, v3, v4, fill=self.fill, rotate=self.rotation)


# ===== engine/sprite_ai.py =====

import math
from typing import TYPE_CHECKING
pass
class SpriteAI:
    def __init__(self, parent: 'Sprite') -> None:
        self.parent = parent
        self._active_list: list[Vector3] = []
        self._active_target: Vector3 | None = None
        self._path_target: Vector3 | None = None
        self._track_player: 'Player | None' = None
        self._last_position = parent.position
        self._stuck_ticks = 0
        self.speed = 2
        pass
    def tick(self):
        moved = self.parent.position.distance(self._last_position)
        if moved < 0.5:
            self._stuck_ticks += 1
        else:
            self._stuck_ticks = 0
        self._last_position = self.parent.position
        if self._track_player and self._path_target is None:
            self._path_target = self._track_player.position
        if self._track_player and self._stuck_ticks > 20:
            self._active_list = []
            self._active_target = None
            self._path_target = self._track_player.position
            self._stuck_ticks = 0
        if self._active_target is None and self._active_list:
            self._active_target = self._active_list.pop(0)
        if self._active_target is None and self._path_target is not None:
            self._active_list = self.pathfind(self.parent.position, self._path_target)
            self._path_target = None
            if self._active_list:
                self._active_target = self._active_list.pop(0)
        if self._active_target is None:
            return
        if self.parent.position.distance(self._active_target) < 40:
            self._active_target = None
            return
        movement_vector = (self._active_target - self.parent.position).normal * self.speed
        if self.parent.is_touching_player():
            return
        if self.parent.is_colliding(movement_vector):
            move_x = Vector3.new(movement_vector.x, 0, 0)
            move_z = Vector3.new(0, 0, movement_vector.z)
            can_move_x = move_x.magnitude > 0 and (not self.parent.is_colliding(move_x))
            can_move_z = move_z.magnitude > 0 and (not self.parent.is_colliding(move_z))
            if can_move_x:
                movement_vector = move_x
            elif can_move_z:
                movement_vector = move_z
            else:
                self._stuck_ticks += 1
                return
        self.parent.position += movement_vector
    def target(self, object: 'Vector3 | Player'):
        if isinstance(object, Player):
            self._track_player = object
            self._path_target = object.position
        else:
            self._track_player = None
            self._path_target = object
        self._active_list = []
        self._active_target = None
        self._stuck_ticks = 0
    def valid_point(self, origin: Vector3, point: Vector3) -> bool:
        movement = point - origin
        if self.parent.is_colliding_from(origin, movement):
            return False
        return True
    def next_point(self, start: Vector3, end: Vector3) -> Vector3:
        direction = (end - start).normal
        step_size = 50
        direct = start + direction * step_size
        if self.valid_point(start, direct):
            return direct
        for angle in (30, -30, 60, -60, 90, -90, 135, -135, 180):
            rotated = direction.rotate_y(math.radians(angle))
            candidate = start + rotated * step_size
            if self.valid_point(start, candidate):
                return candidate
        return start
    def pathfind(self, start: Vector3, end: Vector3) -> list[Vector3]:
        steps = 28
        diff = end - start
        pts: list[Vector3] = []
        current = start
        for i in range(steps):
            target = start + diff * ((i + 1) / steps)
            current = self.next_point(current, target)
            pts.append(current)
        return pts


# ===== engine/sprite.py =====

import math
from cmu_graphics import Image, rgb
class Sprite:
    def __init__(self, sprite: Asset, position: Vector3, size: tuple[int, int]) -> None:
        self.sprite = sprite
        self.position = position
        self.game = CMUtils._game
        asset = self.game.assets.load_asset(sprite)
        self._shape = Image(asset, 100, 100)
        self.game.renderables.append(self)
        self.z = self.position.z
        self._sort_id = 1
        self.opacity = 100
        self.size = size
        self.ai = SpriteAI(self)
        pass
    def tick(self):
        self._shape.visible = False
        self._sort_id = 1
        s = math.hypot(*self.size)
        self.ai.tick()
        self._proxy = Triangle(self.position, Vector3(-s, 0, 0), Vector3(s, 0, 0), Vector3(0, s * 2, 0), render_shadow=False, render_lights=False, fill=rgb(128, 128, 128), opacity=0)
        self._proxy_b = Triangle(self.position, Vector3(0, 0, -s), Vector3(0, 0, s), Vector3(0, s * 2, 0), render_shadow=False, render_lights=False, fill=rgb(128, 128, 128), opacity=0)
        self.z = self.position.z
        scale = 300 / self.position.distance(self.game.camera.position)
        self.z = self.position.z / scale
        if scale < 0.25:
            return
        self._shape.width = self.size[0] * scale
        self._shape.height = self.size[1] * scale
        self._shape.opacity = max(0, min(100, scale * 100))
        if not hasattr(self._proxy, 'screen'):
            return
        cX = self._proxy.screen[0][0]
        cY = self._proxy.screen[0][1]
        self._shape.centerX = cX
        self._shape.centerY = cY
        self._shape.visible = True
        if not self.game:
            return
    def is_colliding(self, mov: Vector3):
        return self.is_colliding_from(self.position, mov)
    def is_colliding_from(self, origin: Vector3, mov: Vector3) -> bool:
        if mov.magnitude <= 0:
            return False
        launch = Ray(origin, mov.normal, mov.magnitude)
        c = launch.cast()
        return c is not None
    def is_touching_player(self):
        return self.position.distance(self.game.player.position) < 40


# ===== engine/shapes/sphere.py =====

import math
from typing import TYPE_CHECKING
pass
class Sphere(Base3DShape):
    def __init__(self, position: Vector3, radius: float, fill: 'RGB') -> None:
        super().__init__(position, Vector3.new(radius * 2, radius * 2, radius * 2), fill=fill)
        self.radius = radius
    def draw(self):
        if not self.valid:
            return
        vertices: list[Vector3] = []
        lat_steps = 5 if True else 15
        lon_steps = 5 if True else 15
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
            v2 = vertices[face[1]].rotate(self.rotation)
            v3 = vertices[face[2]].rotate(self.rotation)
            Triangle(self.position, v1, v2, v3, fill=self.fill)


# ===== main.py =====

from operator import pos
import sys, math
import time
from typing import Any
from cmu_graphics import *
app.stepsPerSecond = 120
app.spheres = []
exCube: Cube
sp: Sprite
_points = []
pass
@game.on_ready
def main():
    global exCube, sp, _points
    floor = Cube(position=Vector3.new(800, -270, 400), size=Vector3.new(2500, 250, 2500), fill=rgb(0, 255, 0))
    exCube = Cube(position=Vector3.new(700, 0, 200), size=Vector3.new(400, 100, 100))
i = 0
@game.register_tick
def step(dt):
    print(f'FPS: {rounded(1 / dt)}')
    pass
    global i, _points
game.run()