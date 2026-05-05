from operator import pos
import sys,math
import time
from engine.shapes.cube import Cube
from engine.triangle import Triangle
from engine.vector3 import Vector3
from engine import game
from engine.ray import Ray


from cmu_graphics import * # pyright: ignore[reportWildcardImportFromLibrary]
app.stepsPerSecond = 120 

from engine.shapes.sphere import Sphere





app.spheres =[]
exCube: Cube

@game.on_ready
def main():
    print(game.utils.version)
    global exCube
    app.fpsLabel = Label("FPS: 0", 370, 20)
    app.triangleLabel = Label("Triangles: 0", 360, 50)

    #sphere1 = Sphere(position=Vector3.new(0,0,400), fill=rgb(255,0,0), radius=100)
    floor = Cube(position=Vector3.new(800,-270,400), size=Vector3.new(2500, 250, 2500), fill=rgb(0,255,0))
    exCube = Cube(position=Vector3.new(0,0,500), size=Vector3.new(100,100,100))


def onMousePress(x, y):
    r = Ray(game.camera.position, game.camera.direction)
    hit = r.cast()
    if hit is None:
        return
    print(hit)

@game.register_tick
def step(dt):
    #print(MAX_AREA, min(fps_trend))
    app.fpsLabel.value = f"FPS: {rounded(1/dt)}"
    app.triangleLabel.value = f"Triangles: {game._triangle_count}"
    app.fpsLabel.toFront()
    app.triangleLabel.toFront()
    exCube.rotation += Vector3.new(0.025,0.025,0.025)


game.run()