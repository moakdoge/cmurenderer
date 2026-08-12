from operator import pos
import sys,math
import time
from typing import Any
from engine.assets.asset import Asset
from engine.shapes.cube import Cube
from engine.sprite import Sprite
from engine.triangle import Triangle
from engine.vector3 import Vector3
from engine import make_game

game = make_game()

from engine.ray import Ray


from cmu_graphics import * # pyright: ignore[reportWildcardImportFromLibrary]
app.stepsPerSecond = 120 

from engine.shapes.sphere import Sphere





app.spheres =[]
exCube: Cube
sp: Sprite
_points = []

if game.utils.is_desktop() and False:
    #stub the shit out of that stupid type checker
    import cmu_graphics.shape_logic as sl
    import cmu_graphics.cmu_graphics as cmgrph
    
    def slSetWithTypeCheck(obj, attr, val):
        object.__setattr__(obj, attr, val)
        return val

    
    def _setattr(self, attr, val):
        if attr[0] == '_':
            self.__dict__[attr] = val
        else:
            object.__setattr__(self._shape, attr, val)
        return val
    
    def get_children(self: sl.Group):
        ls=list(map(lambda s: s.studentShape, self._shapes))
        return ls#list(map(lambda s: s.studentShape, self._shapes))
    cmgrph.sli.slSetWithTypeCheck = slSetWithTypeCheck
    cmgrph.Shape.__setattr__  = _setattr
    old = sl.Shape.draw
    
    calls = 0
    def new_draw(self, ctx):
        if self.isGroup:
            try:
                ctx.save()
                for s in self._shapes:
                    if not getattr(s, "_skip", False):
                        s.draw(ctx)
                return
            finally:
                ctx.restore()
        else:
            #self.isGroup = False
            old(self, ctx)
            #self.isGroup = True
    sl.Shape.draw = new_draw
    sl.Group.children = property(get_children)
    

    
@game.on_ready
def main():
    global exCube, sp, _points
    #app.fpsLabel = Label("FPS: 0", 370, 20)
    #app.triangleLabel = Label("Triangles: 0", 360, 50)

    #sphere1 = Sphere(position=Vector3.new(0,0,400), fill=rgb(255,0,0), radius=100)
    floor = Cube(position=Vector3.new(800,-270,400), size=Vector3.new(2500, 250, 2500), fill=rgb(0,255,0))
    exCube = Cube(position=Vector3.new(700,0,200), size=Vector3.new(400,100,100))   
    
    
    #corcle = Sphere(position=Vector3.new(1000, 0, 500), radius=50, fill=rgb(0,0,255))
   # tri = Triangle(Vector3.zero(), *(Vector3.zero(),Vector3.zero(),Vector3.zero()))
   # print(type(app._app._tlg._shape).children.fget)

i=0
@game.register_tick
def step(dt):
    print(f"FPS: {rounded(1/dt)}")
    pass
    global i, _points
    #print(MAX_AREA, min(fps_trend))
    #app.fpsLabel.value = f"FPS: {rounded(1/dt)}"
    #app.triangleLabel.value = f"Triangles: {game._triangle_count}"
    #app.fpsLabel.toFront()
    #sp.ai.target(game.player)
 #  # exCube.rotation += Vector3.new(0.025,0.025,0.025)
    #sp.ai.tick()

#print(app._app._tlg._shape)



game.run()