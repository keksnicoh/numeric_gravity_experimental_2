from OpenGLContext.arrays import *
from OpenGL.GL import *
from keyboard.fluent import fluent as kbCntrlFluent
from keyboard.flyaroundHandler import flyaroundHandler

from objects.cube import cube as objCube
from objects.arrow import arrow as objArrow

import time
import math
from world import world as World


def init(world):
	return
def scene():
	return
def render():
	return
def handleMovement(world, kbCntrl):
	"""Keyboard controlling, uses keyboard.flyaroundHandler
	   to provide basic interaction"""
	flyaroundHandler(world, kbCntrl)

if __name__ == "__main__":
	world = World()

	kbCntrl = kbCntrlFluent()
	kbCntrl.activate()

	world.keyboardTriggerCallback = lambda : handleMovement(world, kbCntrl)
	world.sceneContext = scene
	world.renderContext = render

	init(world)
	world.run()
