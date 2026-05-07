import math

from engine.assets.asset import Asset
from engine.sprite_ai import SpriteAI
from engine.triangle import Triangle
from engine.vector3 import Vector3
from engine.cmu_utils import  CMUtils
from cmu_graphics import Image, rgb
from engine.ray import Ray
class Sprite(): #NOTE - This is horrible.
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
        s=math.hypot(*self.size)
        self.ai.tick()
        self._proxy = Triangle(
            self.position,
            Vector3(-s, 0, 0),
            Vector3( s, 0, 0),
            Vector3(0, s * 2, 0),
            render_shadow=False,
            render_lights=False,
            fill=rgb(128,128,128),
            opacity=0
        )

        self._proxy_b = Triangle(
            self.position,
            Vector3(0, 0, -s),
            Vector3(0, 0,  s),
            Vector3(0, s * 2, 0),
            render_shadow=False,
            render_lights=False,
            fill=rgb(128,128,128),
            opacity=0
        )
        self.z = self.position.z
        scale = 300 / self.position.distance(self.game.camera.position)
        self.z = self.position.z / scale
        if scale < 0.25:
            return

        self._shape.width = self.size[0] * scale
        self._shape.height = self.size[1] * scale
        self._shape.opacity = max(0,min(100,scale * 100))
        if not hasattr(self._proxy, "screen"):
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

        launch = Ray(
            origin,
            mov.normal,
            mov.magnitude
        )

        c = launch.cast()
        return c is not None
    
    def is_touching_player(self):
        return self.position.distance(self.game.player.position) < 40