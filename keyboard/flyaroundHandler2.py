from OpenGLContext.arrays import *
import math
import time

def flyaroundHandler2(world):
	a = world.camera_rotation[1]*pi / 180
	b = world.camera_rotation[0]*pi / 180
	s = 0.8
	if 256 in world.keyboardActive:
		world.exit = True
	if ord('W') in world.keyboardActive:
		print "move w"
		world.camera_position[0] -= sin(b)*cos(a)*s
		world.camera_position[1] += sin(a)*s
		world.camera_position[2] += cos(a)*cos(b)*s
	if ord('S') in world.keyboardActive:
		world.camera_position[0] += sin(b)*cos(a)*s
		world.camera_position[1] -= sin(a)*s
		world.camera_position[2] -= cos(a)*cos(b)*s
	if ord('A') in world.keyboardActive:
		world.camera_position[0] += cos(b)*s
		world.camera_position[2] += sin(b)*s
	if ord('D') in world.keyboardActive:
		world.camera_position[0] -= cos(b)*s
		world.camera_position[2] -= sin(b)*s
