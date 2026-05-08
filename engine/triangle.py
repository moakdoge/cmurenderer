from engine.color_utils import set_brightness
from engine.extras import cached_property, dataclass
from typing import TYPE_CHECKING

from engine.light import Light, lights
from engine.vector3 import Vector3
from cmu_graphics import *
if TYPE_CHECKING:
    from engine._game import Game
    from cmu_graphics.shape_logic import RGB
    from engine.camera import Camera
    

existing_game: "Game"
class Triangle():
    __slots__ = (
        "shadow", "points", "position", "fill", "_count", "_real_fill",
        "opacity", "fogged", "z", "screen", "extracted", "_shape",
        "_sort_id", "average_screen_dist", "_og_points"
        # no "__dict__"
    )
    def __init__(
        self,
        position: Vector3,
        *points: Vector3,
        rotate: Vector3 | None = None,
        fill=rgb(255,255,255),
        pretransformed: bool = False,
        render_lights: bool = True,
        skip_near_clip: bool = False,
        opacity: int = 100,
        render_shadow: bool = True
    ):
        
        # input validation
        assert len(points) == 3
        assert isinstance(position, Vector3)
        assert all([isinstance(p, Vector3) for p in points])
        assert isinstance(opacity, int) and 0 <= opacity <= 100

        self.shadow = None
        self._og_points: list[Vector3] = [*points]
        self.points: list[Vector3] = [*points]
        self.position = position
        self.fill = fill
        self._count = len(points)
        self._real_fill= fill
        self.opacity = opacity
        
        self.fogged = False


        if render_lights and existing_game.configuration.current.shading:
            self._real_fill = self.get_fill(fill)
        
        
        if render_shadow and existing_game.configuration.current.shadows:
            self.render_shadow()
            
            
        if not pretransformed:
            pass
           # if rotate is not None:
            #    self.points = self.rotate_points(rotate) 
            #self.transform(existing_game.camera)
            

        clipped = self.get_clip(skip_near_clip)
        if not clipped:
            self.delete()
            return

        if len(clipped) > 1:
            existing_game.remove_triangle(self.shadow)
            self.shadow = None
            _, second = clipped
            Triangle(
                Vector3.zero(),
                *second,
                fill=self.fill,
                pretransformed=True,
                render_lights=True,
                skip_near_clip=True,
                opacity=opacity,
                render_shadow=False
            )

        self.points = list(clipped[0])
        self._count = len(self.points)


        
        #calculate z and screens
        self.z = self.get_z()
        self.screen = self.get_screens()
        self.extracted = self.get_extracted()
    

        existing_game.add_triangle(self)

        if not self.is_valid():
            self.delete()
            return
       
    
    def rotate_points(self, mat: Vector3):
        return [
            p.rotate(mat) for p in self.points
        ]
    def is_valid(self) -> bool:
        statements = [
            self.is_too_small(),
            self.is_foggy(),
            self.is_offscreen()
        ]
        return not any(statements)
    def get_z(self) -> float:
        z = max(_.z for _ in self.points)
        if self.opacity < 100:
            z -= 0.01
        return z
        
    def get_screens(self) -> list[tuple[int, int]]:
        return [_.screen for _ in self.points]
    
    def get_extracted(self):
        return [list(sublist) for sublist in self.screen]
    
    def is_foggy(self) -> bool:
        lowest = 140
        v = (self.screen_area < lowest) and (self.physical_area < existing_game.configuration.current.minimum_physical_area_cull)
        return v
    
    def is_too_small(self) -> bool:
        centScr = self.center.screen
        self.average_screen_dist = max(distance(_[0],_[1], centScr[0], centScr[1]) for _ in self.screen)
        
        ar = self.area(*self.screen)
        v=(ar < (50 / existing_game.configuration.current.quality)) and (self.physical_area < existing_game.configuration.current.minimum_physical_area_cull)
    
        return v
    

    def is_offscreen(self) -> bool:
        if all(_.offscreen for _ in self.points) and (self.physical_area < 1):
            return True
        
        return False
        
    
    def transform(self, camera: "Camera"):
        # calculate camera offset and rotate into view space
        for i, p in enumerate(self.points):
            self.points[i] = p + self.position - camera.position
            self.points[i] = self.points[i].rotate(
                Vector3.new(camera.pitch, camera.yaw, 0)
            )

    def get_fill(self, start: "RGB") -> "RGB":
        tmp_fill = set_brightness(start, 0.8)
        world_points = self.world_points
        world_center = self.world_center
        if existing_game.configuration.current.shading:
            face_normal = (world_points[1] - world_points[0]).cross(
                world_points[2] - world_points[0]
            ).normal
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
        _p = [
            Vector3.new(p.x, -50, p.z) for p in self.points
        ]
        self.shadow = Triangle(
            self.position - Vector3.new(0, 50, 0),
            *_p,
            fill=rgb(0,0,0),
            render_lights=False,
            skip_near_clip=False,
            opacity=25     ,
            render_shadow=False  
        )
        
    @property
    def center(self):
        return Vector3.new(
            sum(_.x for _ in self.points) / self._count,
            sum(_.y for _ in self.points) / self._count,
            sum(_.z for _ in self.points) / self._count
        )
        
    @property
    def world_points(self):
        return [
            p + self.position
            for p in self.points
        ]
        
    def get_clip(self, skip: bool = False):
        return [tuple(self.points)] if skip else self.clip_near()
        
        
    @property
    def world_center(self):
        world_points = self.world_points
        return Vector3.new(
            sum(p.x for p in world_points) / len(world_points),
            sum(p.y for p in world_points) / len(world_points),
            sum(p.z for p in world_points) / len(world_points),
        )
        
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
        if hasattr(self, "shadow"):
            existing_game.remove_triangle(self.shadow)        
        if hasattr(self, "_shape"):
            existing_game.polygon_factory.free(self._shape)
            self._shape.visible = False
            #del self._shape
        existing_game.remove_triangle(self)


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
