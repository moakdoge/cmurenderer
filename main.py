import sys,math
import time
from engine.triangle import Triangle
from engine.vector3 import Vector3
from engine import game



from cmu_graphics import * # pyright: ignore[reportWildcardImportFromLibrary]
app.stepsPerSecond = 9999999 

from engine.shapes.sphere import Sphere





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



app.dt = 0.016
app.fpsLabel = Label("FPS: 0", 370, 20)
app.triangleLabel = Label("Triangles: 0", 360, 50)

posX = 0



sphere1 = Sphere(position=Vector3.new(0,0,100), fill=rgb(255,0,0), radius=100)


fps_trend: list[float] = []
dt_ema = 1 / game.configuration.fps_target
#i = Image("/home/moakdoge/Downloads/Pipoya RPG Tileset 32x32/LightShadow_pipo.png", 50, 50)
#print(i._shape.__dict__)
def onStep():
    global MAX_AREA, dt_ema
    start = time.perf_counter()
    global posX
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