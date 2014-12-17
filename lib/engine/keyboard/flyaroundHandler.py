from OpenGLContext.arrays import *
import math
import time

def flyaroundHandler(world):
	a = world.camera_rotation[1]
	b = world.camera_rotation[0]
	s = 0.8
	if 256 in world.keyboardActive:
		world.exit = True
	if ord('W') in world.keyboardActive:
		world.translateCameraRelative([sin(b)*cos(a)*s,-sin(a)*s,cos(a)*cos(b)*s])
	if ord('S') in world.keyboardActive:
		world.translateCameraRelative([-sin(b)*cos(a)*s,+sin(a)*s,-cos(a)*cos(b)*s])
	if ord('A') in world.keyboardActive:
		world.translateCameraRelative([cos(b)*s,0,-sin(b)*s])
	if ord('D') in world.keyboardActive:
		world.translateCameraRelative([-cos(b)*s,0,sin(b)*s])
