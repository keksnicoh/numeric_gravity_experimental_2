""" OpenGl gravity simulation n1

    context:
    - simulate basic newton law of gravity with
      correlation on each particle

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

global objN
global drawRelativeVectors
global drawVelocity
global objects
global physicalObjects
global arrow
global phys_dt
global attachCenter

def initContext(world):
	global arrow

	r = 3
	v = 200
	dphi = 2*pi / objN
	for obj in range(0,objN):
		objects.append((objCube(0.1), r*cos(dphi*obj), -r*sin(dphi*obj), 0))
		physicalObjects.append([obj,2,r*cos(dphi*obj),-r*sin(dphi*obj),0,sin(dphi*obj)*v,cos(dphi*obj)*v,0])

	objects.append((objCube(0.1), 0,0,0))
	physicalObjects.append([objN, 80000, 0,0,0, 0,0,0])

	objects.append((objCube(0.1), r,r,r))
	physicalObjects.append([objN+1, 0, r,r,r, 0,0,0])

	objects.append((objCube(0.1), -r,r,r))
	physicalObjects.append([objN+2, 0, -r,r,r, 0,0,0])

	objects.append((objCube(0.1), r,r,-r))
	physicalObjects.append([objN+3, 0, r,r,-r, 0,0,0])

	objects.append((objCube(0.1), -r,r,-r))
	physicalObjects.append([objN+4, 0, -r,r,-r, 0,0,0])

	objects.append((objCube(0.1), 0,0,r))
	physicalObjects.append([objN+5, 0, 0,0,r, 0,0,0])

	objects.append((objCube(0.1), 0,0,-r))
	physicalObjects.append([objN+6, 0, 0,0,-r, 0,0,0])

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
	print "   [1-6] to activate test masses"
	print "   [v]   draw velocity vectors for physical objects"
	print "   [r]   draw relative vectors for physical objects"

def getLengthSquared(v):
	return v[0]**2+v[1]**2+v[2]**2

def getRelativeVector(x1,x2):
	return [x2[0]-x1[0],x2[1]-x1[1],x2[2]-x1[2]]

def normalize(x):
	l = sqrt(getLengthSquared(x))
	return map(lambda x : x/l, x)

def calculateDv(obji):
	objects = filter(lambda objj: objj[2:5] != obji[2:5], physicalObjects)
	dv = [.0,.0,.0]
	for objj in objects:
		dvj = caclculateDvj(obji,objj)
		dv[0] += dvj[0]
		dv[1] += dvj[1]
		dv[2] += dvj[2]
	return dv

def caclculateDvj(obj1, obj2):
	if obj1[1]:
		rel = getRelativeVector(obj1[2:5],obj2[2:5])
		acc1 = 1*obj2[1] / getLengthSquared(rel)*phys_dt
		return map(lambda x: acc1*x, normalize(rel))
	else:
		return [0,0,0]

def convertPhysicsState():
	objDv = []
	for obj in physicalObjects:
		objDv.append(calculateDv(obj))

	objCount = len(objDv)
	objIndex = 0
	while objIndex < objCount:
		dv = objDv[objIndex]

		physicalObjects[objIndex][5] += dv[0]
		physicalObjects[objIndex][6] += dv[1]
		physicalObjects[objIndex][7] += dv[2]

		physicalObjects[objIndex][2] += 0.5*physicalObjects[objIndex][5]*phys_dt
		physicalObjects[objIndex][3] += 0.5*physicalObjects[objIndex][6]*phys_dt
		physicalObjects[objIndex][4] += 0.5*physicalObjects[objIndex][7]*phys_dt

		objIndex += 1


def physics():
	if attachCenter:
		world.camera_position[0] = -physicalObjects[objN][2]
		world.camera_position[1] = -physicalObjects[objN][3]
		world.camera_position[2] = -physicalObjects[objN][4] #wuuu...

	convertPhysicsState()
	for obj in physicalObjects:
		(glObj,x,y,z) = objects[obj[0]]
		objects[obj[0]] = (glObj, obj[2],obj[3],obj[4])

def renderContext():
	obj = 0
	while obj < len(objects):
		if not attachCenter or obj != objN:
			(o, x, y, z) = objects[obj]
			glPushMatrix()
			glTranslatef(x,y,z)
			o.render()
			glPopMatrix()
		obj += 1

	if drawRelativeVectors:
		for obji in physicalObjects:
			if obji[1] > 0:
				glPushMatrix()
				glTranslatef(obji[2],obji[3],obji[4])
				for objj in physicalObjects:
					if objj[1] > 0:
						arrow.color = [0.0,0.0,1.0,0]
						arrow.x = normalize(getRelativeVector(obji[2:5],objj[2:5]))
						arrow.generateVBO()
						arrow.render()
				glPopMatrix()

	if drawVelocity:
		for obj in physicalObjects:
			glPushMatrix()
			glTranslatef(obj[2],obj[3],obj[4])
			arrow.color = [1.0,1.0,0.0,0.0]
			arrow.x = [.01*obj[5],.01*obj[6],.01*obj[7]]
			arrow.generateVBO()
			arrow.render()
			glPopMatrix()

def handleMovement(world, kbCntrl):
	global phys_dt
	global drawRelativeVectors
	global drawVelocity
	global attachCenter

	"""Keyboard controlling, uses keyboard.flyaroundHandler
	   to provide basic interaction"""
	flyaroundHandler(world, kbCntrl)

	if '9' in kbCntrl.active:
		physicalObjects[objN+0][1] -= 1000
		print "central mass -1000"
	if '0' in kbCntrl.active:
		physicalObjects[objN+0][1] += 1000
		print "central mass +1000"

	physicalObjects[objN+1][1] = 5000 if '1' in kbCntrl.active else 0
	physicalObjects[objN+2][1] = 5000 if '2' in kbCntrl.active else 0
	physicalObjects[objN+3][1] = 5000 if '3' in kbCntrl.active else 0
	physicalObjects[objN+4][1] = 5000 if '4' in kbCntrl.active else 0
	physicalObjects[objN+5][1] = 5000 if '5' in kbCntrl.active else 0
	physicalObjects[objN+6][1] = 5000 if '6' in kbCntrl.active else 0

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
		if key == '-':
			phys_dt -= 0.0001
		if key == 'c':
			attachCenter = False if attachCenter else True

	kbCntrl.stack = []

if __name__ == "__main__":
	objN = 40

	drawRelativeVectors = False
	drawVelocity = False
	objects = []
	physicalObjects = []
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

	world.run()

