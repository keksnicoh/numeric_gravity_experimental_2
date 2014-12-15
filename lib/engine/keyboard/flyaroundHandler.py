from OpenGLContext.arrays import *
import math
import time

def flyaroundHandler(world, kbCntrl):
	a = world.rotation[1]*pi / 180
	b = world.rotation[0]*pi / 180
	s = 0.8

	if '\x1b' in kbCntrl.active:
		world.exit = True
	if 'w' in kbCntrl.active:
		world.camera_position[0] -= sin(b)*cos(a)*s
		world.camera_position[1] += sin(a)*s
		world.camera_position[2] += cos(a)*cos(b)*s
	if 's' in kbCntrl.active:
		world.camera_position[0] += sin(b)*cos(a)*s
		world.camera_position[1] -= sin(a)*s
		world.camera_position[2] -= cos(a)*cos(b)*s
	if 'a' in kbCntrl.active:
		world.camera_position[0] += cos(b)*s
		world.camera_position[2] += sin(b)*s
	if 'd' in kbCntrl.active:
		world.camera_position[0] -= cos(b)*s
		world.camera_position[2] -= sin(b)*s
