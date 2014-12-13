""" OpenGl gravity simulation n4

    context:
    - use numpy to calculate distances between objects.

    basic euler approximation of newtons gravity.
    approximation:
    - linear steps with length p_dt

    known issues:
    - singulaties when objects are close
    - no collision check
    - very slow due to big amout of python
      high level invocations

    author keksnicoh@googlemail.com
"""
from OpenGLContext.arrays import *
from OpenGL.GL import *
from keyboard.fluent import fluent as kbCntrlFluent
from keyboard.flyaroundHandler import flyaroundHandler

from objects.cube import cube as objCube
from objects.arrow import arrow as objArrow

import time
import math
from world import world as World
import numpy
global circleObjN
global drawRelativeVectors
global drawVelocity
global objects
global obj_phys
global arrow
global phys_dt
global attachCenter
global physCalsPerRender
global externalEField
global obj_physOriginal
global obj_physSaved

def initContext(world):
	global arrow
	global obj_physOriginal
	global obj_phys
	r = 3.0
	main_mass = 80000
	sat_mass = 1.0
	sat_v = sqrt(main_mass/r);
	dphi = 2*pi / circleObjN
	physics = []
	for obj in range(0,circleObjN):
		objects.append((objCube(0.1), r*cos(dphi*obj), -r*sin(dphi*obj), 0))

		physics.append([
			obj,
			r*cos(dphi*obj), #x
			-r*sin(dphi*obj),
			0,
			sin(dphi*obj)*sat_v, #v
			cos(dphi*obj)*sat_v,
			0,
			1.,1. #m,q
		])

	objects.append((objCube(0.1), 0,0,0))
	physics.append([circleObjN, 0,0,0, 0,0,0, main_mass,1.])

	obj_phys = numpy.array(physics)

	arrow = objArrow()

	print "opengl simulation of bla"
	print "main control"
	print " - hold left mouse button to look around"
	print " - use w,a,s,d to fly around"
	print "   [ESC] exit"
	print "   [o]   toggle between shaders"

	print "physics manipulations:"
	print "   [+]   increase dt by 0.0001"
	print "   [-]   decreate dt by 0.0001"
	print "   [9]   decrease center mass by 1000"
	print "   [0]   increase center mass by 1000"
	print "   [1-6] to activate homoge e-field in axes"
	print "   [v]   draw velocity vectors for physical objects"
	print "   [r]   draw relative vectors for physical objects"

def calculateDv():


	e0 = 5.
	pos = obj_phys[:, [1, 2, 3]]
	dpos =  pos[numpy.newaxis, :] - pos[:, numpy.newaxis]
	d = numpy.sqrt(numpy.sum((pos[:, numpy.newaxis] - pos[numpy.newaxis, :])**2, axis=-1))
	d_15 = d**3
	m = obj_phys[:,7]
	q = obj_phys[:,8]
	n = len(d[0])
	dv = numpy.zeros((n,3))
	o1i = 0
	while o1i < n:
		o2i = o1i+1
		while o2i < n:
			if d_15[o1i][o2i] and m[o2i]:
				f_g = dpos[o1i][o2i]/d_15[o1i][o2i]

				dv[o1i][0] += f_g[0] * m[o2i] * phys_dt
				dv[o1i][1] += f_g[1] * m[o2i] * phys_dt
				dv[o1i][2] += f_g[2] * m[o2i] * phys_dt
				dv[o2i][0] -= f_g[0] * m[o1i] * phys_dt
				dv[o2i][1] -= f_g[1] * m[o1i] * phys_dt
				dv[o2i][2] -= f_g[2] * m[o1i] * phys_dt
			o2i += 1

		if m[o1i]:
			dv[o1i][0] -= (e0*q[o1i]/m[o1i]) * externalEField[0]
			dv[o1i][1] -= (e0*q[o1i]/m[o1i]) * externalEField[1]
			dv[o1i][2] += (e0*q[o1i]/m[o1i]) * externalEField[2]
		o1i += 1
	return dv


def convertPhysicsState():
	dv = calculateDv()
	objN = len(obj_phys)
	oi = 0
	#pc = obj_phys.copy()
	while oi < objN:
		obj_phys[oi][4] += dv[oi][0]
		obj_phys[oi][5] += dv[oi][1]
		obj_phys[oi][6] += dv[oi][2]

		obj_phys[oi][1] += obj_phys[oi][4]*phys_dt
		obj_phys[oi][2] += obj_phys[oi][5]*phys_dt
		obj_phys[oi][3] += obj_phys[oi][6]*phys_dt

		oi += 1

def physics():

	convertPhysicsState()
	for obj in obj_phys:
		(glObj,x,y,z) = objects[int(obj[0])]
		objects[int(obj[0])] = (glObj, obj[1],obj[2],obj[3])


def renderContext():

	obj = 0
	while obj < len(objects):
#		if not attachCenter or obj != circleObjN:
		(o, x, y, z) = objects[obj]
		glPushMatrix()
		glTranslatef(x,y,z)
		o.render()
		glPopMatrix()
		obj += 1
	if drawRelativeVectors:
		for obji in obj_phys:
			if obji[1] > 0:
				glPushMatrix()
				glTranslatef(obji[1],obji[2],obji[3])
				objj = obj_phys[circleObjN]
				arrow.color = [0.0,0.0,1.0,0]
				rel = [objj[1] - obji[1],objj[2] - obji[2],objj[3] - obji[3]]
				urel = sqrt(rel[0]**2+rel[1]**2+rel[2]**2)
				arrow.x = [rel[0]/urel,rel[1]/urel,rel[2]/urel]
				arrow.generateVBO()
				arrow.render()
				glPopMatrix()

	if drawVelocity:
		for obj in obj_phys:
			glPushMatrix()
			glTranslatef(obj[1],obj[2],obj[3])
			arrow.color = [1.0,1.0,0.0,0.0]
			arrow.x = [.005*obj[4],.005*obj[5],.005*obj[6]]
			arrow.generateVBO()
			arrow.render()
			glPopMatrix()


def handleMovement(world, kbCntrl):
	global phys_dt
	global drawRelativeVectors
	global drawVelocity
	global attachCenter
	global physCalsPerRender
	global externalEField
	global obj_physOriginal
	global obj_physSaved

	"""Keyboard controlling, uses keyboard.flyaroundHandler
	   to provide basic interaction"""
	flyaroundHandler(world, kbCntrl)

	externalEField[0] = 1 if '1' in kbCntrl.active else 0
	externalEField[1] = 1 if '2' in kbCntrl.active else 0
	externalEField[2] = 1 if '3' in kbCntrl.active else 0

	externalEField[0] = -1 if '4' in kbCntrl.active else externalEField[0]
	externalEField[1] = -1 if '5' in kbCntrl.active else externalEField[1]
	externalEField[2] = -1 if '6' in kbCntrl.active else externalEField[2]

	if '9' in kbCntrl.active:
		obj_phys[circleObjN+0][7] -= 1000
		print "central mass -1000"
	if '0' in kbCntrl.active:
		obj_phys[circleObjN+0][7] += 1000
		print "central mass +1000"
	if 'n' in kbCntrl.active:
		print "reset physics"
		for oi,obj in enumerate(obj_physOriginal):
			obj_phys[oi] = list(obj)
	if 'p' in kbCntrl.active:
		print "persist physics"
		obj_physSaved = []
		for obj in obj_phys:
			obj_physSaved.append(list(obj))
	if 'l' in kbCntrl.active:
		print "load physics"
		for oi,obj in enumerate(obj_physSaved):
			obj_phys[oi] = list(obj)

	externalEField_l = sqrt(externalEField[0]**2+externalEField[1]**2+externalEField[2]**2)
	if externalEField_l:
		externalEField[0] /= externalEField_l
		externalEField[1] /= externalEField_l
		externalEField[2] /= externalEField_l
	for key in kbCntrl.stack:

		if key == 'r':
			drawRelativeVectors = False if drawRelativeVectors else True
		if key == 'v':
			drawVelocity = False if drawVelocity else True
		if key == 'o':
			world.useShader = 1 if world.useShader == 0 else 0
			print "switch shader"
		if key == '+':
			phys_dt += 0.0001
		#	physCalsPerRender+=1
		if key == '-':
			phys_dt -= 0.0001
		#	if(physCalsPerRender > 0):
		#		physCalsPerRender-=1

		if key == 'c':
			attachCenter = False if attachCenter else True

	kbCntrl.stack = []

if __name__ == "__main__":
	circleObjN = 120

	externalEField = [0.,0.,0.]
	drawRelativeVectors = False
	drawVelocity = False
	objects = []
	obj_phys = numpy.array([], dtype=float)
	obj_physOriginal = []
	obj_physSaved= []
	physCalsPerRender = 1
	phys_dt = 0.0001
	attachCenter = False
	world = World()
	world.rotation        = [34, 50]
	world.camera_position = [7.0675604969805788, -12.974440539426263, -9.4667938872866237]
	world.mouseData       = [0,0,0,0,world.rotation[0],world.rotation[1]]
	# keyboard control
	kbCntrl = kbCntrlFluent()
	kbCntrl.activate()
	world.keyboardTriggerCallback = lambda : handleMovement(world, kbCntrl)
	world.sceneContext = physics
	world.renderContext = renderContext

	initContext(world)
#	physics()
	world.run()

