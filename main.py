import sys,math
import time

from engine.cmu_utils import CMUtils
from engine.triangle import Triangle
from engine.vector3 import Vector3
from engine import game

IS_DESKTOP = (sys.implementation.name != "brython")
from cmu_graphics import * # pyright: ignore[reportWildcardImportFromLibrary]
app.stepsPerSecond = 9999999 
app.targetFPS = 30
MAX_AREA=180


POLYGON_POOL: list[Polygon] = [Polygon(0, 0, 0, 0, 0, 0) for _ in range(2000)]
pool_ind = 0

def begin_frame():
    global pool_ind
    pool_ind = 0
    for p in POLYGON_POOL:
        p.visible = False

def pool_polygon(*args, **kwargs) -> Polygon:
    global pool_ind

    if pool_ind >= len(POLYGON_POOL):
        raise RuntimeError("Polygon pool exhausted")

    poly = POLYGON_POOL[pool_ind]
    pool_ind += 1
    poly.visible = True

    return poly

def end_frame():
    for i in range(pool_ind, len(POLYGON_POOL)):
        POLYGON_POOL[i].visible = False




def setPoints(img: Image, points: list[list[float]]):
    p0, p1, p2 = points

    x0, y0 = p0
    x1, y1 = p1
    x2, y2 = p2

    img.left = x0
    img.top = y0  # assuming you meant .top, not .right

    w = img.width
    h = img.height

    if w == 0 or h == 0:
        return

    # local image x-axis maps to triangle edge p0 -> p1
    ax_x = (x1 - x0) / w
    ax_y = (y1 - y0) / w

    # local image y-axis maps to triangle edge p0 -> p2
    ay_x = (x2 - x0) / h
    ay_y = (y2 - y0) / h

    img.transformMatrix = [
        [ax_x, ay_x],
        [ax_y, ay_y],
    ]

    # IMPORTANT:
    # the matrix already contains rotation/shear/scale.
    # leaving rotateAngle active probably applies rotation twice.
    img.rotateAngle = 0





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
        Triangle(position, v1, v2, v3, fill=color, texture="/home/moakdoge/Downloads/downloads_extra_old/file.png")



app.inspectorEnabled = False
import math


    



app.lastPos = None
app.dt = 0.016
app.fpsLabel = Label("FPS: 0", 370, 20)
app.triangleLabel = Label("Triangles: 0", 360, 50)

posX = 0







fps_trend: list[float] = []
dt_ema = 1 / app.targetFPS
MAX = 600
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
    if len(fps_trend) > MAX:
        fps_trend.pop(0)

    target_dt = 1 / app.targetFPS
    dt_ema = (dt_ema * 0.9) + (app.dt * 0.1)
    performance_ratio = target_dt / dt_ema

    
    
    RANGE = 0.05

    if posX %4 == 0 :
        if performance_ratio < (1-RANGE): # below target FPS
            game.configuration.quality *= max(0.90, 1 - (0.985 - performance_ratio) * 0.18)
        elif performance_ratio > (1+RANGE): # above target FPS
            game.configuration.quality *= min(1.08, 1 + (performance_ratio - 1.015) * 0.12)

        game.configuration.quality = max(0.25, min(4.0, game.configuration.quality))

        print(f"Q:{game.configuration.quality:.3f} FPS:{(1 / dt_ema):.1f} TARGET:{app.targetFPS}")

    #okay.
    MAX_AREA = 180 / (game.configuration.quality*2)

    #print(MAX_AREA, min(fps_trend))
    app.fpsLabel.value = f"FPS: {rounded(1/app.dt)}"
    app.triangleLabel.value = f"Triangles: {game._triangle_count}"
    app.fpsLabel.toFront()
    app.triangleLabel.toFront()




game.utils.run()