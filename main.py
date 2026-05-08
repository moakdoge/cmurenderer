from operator import pos
import sys,math
import time
from engine.assets.asset import Asset
from engine.shapes.cube import Cube
from engine.sprite import Sprite
from engine.triangle import Triangle
from engine.vector3 import Vector3
from engine import game
from engine.ray import Ray


from cmu_graphics import * # pyright: ignore[reportWildcardImportFromLibrary]
app.stepsPerSecond = 120 

from engine.shapes.sphere import Sphere





app.spheres =[]
exCube: Cube
sp: Sprite
_points = []
@game.on_ready
def main():
    global exCube, sp, _points
    app.fpsLabel = Label("FPS: 0", 370, 20)
    app.triangleLabel = Label("Triangles: 0", 360, 50)

    #sphere1 = Sphere(position=Vector3.new(0,0,400), fill=rgb(255,0,0), radius=100)
    floor = Cube(position=Vector3.new(800,-270,400), size=Vector3.new(2500, 250, 2500), fill=rgb(0,255,0))
    exCube = Cube(position=Vector3.new(700,0,200), size=Vector3.new(400,100,100))
    #corcle = Sphere(position=Vector3.new(1000, 0, 500), radius=50, fill=rgb(0,0,255))
    tri = Triangle(Vector3.zero(), *(Vector3.zero(),Vector3.zero(),Vector3.zero()))
    v = Sprite(Asset(
        "/home/moakdoge/Desktop/bullcrapv4/995926089329874021.png",
        "cmu://881058/45181084/map.png"
    ), Vector3.new(200,0,200),(100, 100))
    
    sp = v
    sp.ai.target(game.player)
i=0
@game.register_tick
def step(dt):
    global i, _points
    #print(MAX_AREA, min(fps_trend))
    app.fpsLabel.value = f"FPS: {rounded(1/dt)}"
    app.triangleLabel.value = f"Triangles: {game._triangle_count}"
    app.fpsLabel.toFront()
    app.triangleLabel.toFront()
 #   exCube.rotation += Vector3.new(0.025,0.025,0.025)
    sp.ai.tick()

game.run()