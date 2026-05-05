from operator import pos
import sys,math
import time
from engine.shapes.cube import Cube
from engine.triangle import Triangle
from engine.vector3 import Vector3
from engine import game



from cmu_graphics import * # pyright: ignore[reportWildcardImportFromLibrary]
app.stepsPerSecond = 120 

from engine.shapes.sphere import Sphere








app.dt = 0.016
app.fpsLabel = Label("FPS: 0", 370, 20)
app.triangleLabel = Label("Triangles: 0", 360, 50)

posX = 0
pool_size = 400
min_pool = 120
max_pool = 1600



sphere1 = Sphere(position=Vector3.new(0,0,400), fill=rgb(255,0,0), radius=100)
cube1 = Cube(position=Vector3.new(800,-270,400), size=Vector3.new(2500, 250, 2500), fill=rgb(0,255,0))

fps_trend: list[float] = []
dt_ema = 1 / game.configuration.fps_target
#i = Image("/home/moakdoge/Downloads/Pipoya RPG Tileset 32x32/LightShadow_pipo.png", 50, 50)
#print(i._shape.__dict__)

@game.register_tick
def step(dt):
    MAX_AREA = 180 / (game.configuration.quality*2)

    #print(MAX_AREA, min(fps_trend))
    app.fpsLabel.value = f"FPS: {rounded(1/dt)}"
    app.triangleLabel.value = f"Triangles: {game._triangle_count}"
    app.fpsLabel.toFront()
    app.triangleLabel.toFront()


game.utils.run()