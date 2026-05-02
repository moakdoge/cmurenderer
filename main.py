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
def onStep():
    global MAX_AREA, dt_ema, pool_size
    start = time.perf_counter()
    global posX
    game.tick()
    posX += 1

    app.dt = max(0.0001, time.perf_counter() - start)
    game.fps = math.floor(1/app.dt)
    if game.configuration.enable_auto_quality:
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
                pool_size = max(min_pool, int(pool_size * 0.90))
            elif performance_ratio > (1+RANGE): # above target FPS
                game.configuration.quality *= min(1.08, 1 + (performance_ratio - 1.015) * 0.12)
                pool_size = min(max_pool, int(pool_size * 1.08))
            game.configuration.quality = max(game.configuration.min_quality, min(4.0, game.configuration.quality))

            if pool_size != len(game.polygon_factory._pool):
                game.polygon_factory.regen(pool_size)

            print(f"Q:{game.configuration.quality:.3f} FPS:{(1 / dt_ema):.1f} TARGET:{game.configuration.fps_target}")

    #okay.
    MAX_AREA = 180 / (game.configuration.quality*2)

    #print(MAX_AREA, min(fps_trend))
    app.fpsLabel.value = f"FPS: {rounded(1/app.dt)}"
    app.triangleLabel.value = f"Triangles: {game._triangle_count}"
    app.fpsLabel.toFront()
    app.triangleLabel.toFront()




game.utils.run()