""" OpenGl gravity simulation n2

    context:
    - optimization of force calculation by
      using newtons third law, the force A-B
      is the same as B-A.

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
global physicalObjects
global arrow
global phys_dt
global attachCenter
global physCalsPerRender
def initContext(world):
	global arrow

	r = 3.0
	main_mass = 80000
	sat_mass = 1.0
	sat_v = sqrt(main_mass/r);
	dphi = 2*pi / circleObjN
	for obj in range(0,circleObjN):
		objects.append((objCube(0.1), r*cos(dphi*obj), -r*sin(dphi*obj), 0))
		physicalObjects.append([obj,1,r*cos(dphi*obj),-r*sin(dphi*obj),0,sin(dphi*obj)*sat_v,cos(dphi*obj)*sat_v,0])

	objects.append((objCube(0.1), 0,0,0))
	physicalObjects.append([circleObjN, main_mass, 0,0,0, 0,0,0])

	objects.append((objCube(0.1), r,r,r))
	physicalObjects.append([circleObjN+1, 0, r,r,r, 0,0,0])

	objects.append((objCube(0.1), -r,r,r))
	physicalObjects.append([circleObjN+2, 0, -r,r,r, 0,0,0])

	objects.append((objCube(0.1), r,r,-r))
	physicalObjects.append([circleObjN+3, 0, r,r,-r, 0,0,0])

	objects.append((objCube(0.1), -r,r,-r))
	physicalObjects.append([circleObjN+4, 0, -r,r,-r, 0,0,0])

	objects.append((objCube(0.1), 0,0,r))
	physicalObjects.append([circleObjN+5, 0, 0,0,r, 0,0,0])

	objects.append((objCube(0.1), 0,0,-r))
	physicalObjects.append([circleObjN+6, 0, 0,0,-r, 0,0,0])


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

def calculateDv():
	objN = len(physicalObjects)
	dv = numpy.zeros((objN,3))
	d2_calc = 0
	obj_with_mass = len(filter(lambda obj: obj[1], physicalObjects));
	exp_d2_calc = obj_with_mass*(obj_with_mass-1.0)/2.0

	oia = 0
	while oia < objN:
		obja = physicalObjects[oia]
		if obja[1] > 0:
			oib = oia+1
			while oib < objN:
				objb = physicalObjects[oib]
				if objb[1] > 0:
					rel_ab = [objb[2]-obja[2],objb[3]-obja[3],objb[4]-obja[4]]
					d_2 = rel_ab[0]**2 + rel_ab[1]**2 + rel_ab[2]**2
					d_1 = sqrt(d_2)
					d2_calc += 1
					if d_2 != 0:
						f =  1.0/d_2
						normal_rel_ab = [rel_ab[0]/d_1, rel_ab[1]/d_1, rel_ab[2]/d_1]
						dv[oia][0] +=  f * objb[1] * normal_rel_ab[0] * phys_dt
						dv[oia][1] +=  f * objb[1] * normal_rel_ab[1] * phys_dt
						dv[oia][2] +=  f * objb[1] * normal_rel_ab[2] * phys_dt
						dv[oib][0] += -f * obja[1] * normal_rel_ab[0] * phys_dt
						dv[oib][1] += -f * obja[1] * normal_rel_ab[1] * phys_dt
						dv[oib][2] += -f * obja[1] * normal_rel_ab[2] * phys_dt
				oib+=1
		oia += 1

	if(d2_calc != exp_d2_calc):
		print(
			("SIMWARN calculateDv(): d2_calc=%d "
			+ "differ from exp_d2_calc: %d") %
			(d2_calc,exp_d2_calc));
	return dv


def convertPhysicsState():
	dv = calculateDv()

	objN = len(physicalObjects)
	oi = 0
	while oi < objN:
		physicalObjects[oi][5] += dv[oi][0]
		physicalObjects[oi][6] += dv[oi][1]
		physicalObjects[oi][7] += dv[oi][2]

		#print "v", sqrt(physicalObjects[oi][5]**20+physicalObjects[oi][6]**2+physicalObjects[oi][7]**2)

		physicalObjects[oi][2] += physicalObjects[oi][5]*phys_dt
		physicalObjects[oi][3] += physicalObjects[oi][6]*phys_dt
		physicalObjects[oi][4] += physicalObjects[oi][7]*phys_dt

		oi += 1


def physics():
	global circleObjN
	if attachCenter:
		world.camera_position[0] = -physicalObjects[circleObjN][2]
		world.camera_position[1] = -physicalObjects[circleObjN][3]
		world.camera_position[2] = -physicalObjects[circleObjN][4] #wuuu...

	i = 0
	while i < physCalsPerRender:
		convertPhysicsState()
		for obj in physicalObjects:
			(glObj,x,y,z) = objects[obj[0]]
			objects[obj[0]] = (glObj, obj[2],obj[3],obj[4])

		i+=1
def renderContext():
	obj = 0
	while obj < len(objects):
		if not attachCenter or obj != circleObjN:
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
			arrow.x = [.005*obj[5],.005*obj[6],.005*obj[7]]
			arrow.generateVBO()
			arrow.render()
			glPopMatrix()

def handleMovement(world, kbCntrl):
	global phys_dt
	global drawRelativeVectors
	global drawVelocity
	global attachCenter
	global physCalsPerRender

	"""Keyboard controlling, uses keyboard.flyaroundHandler
	   to provide basic interaction"""
	flyaroundHandler(world, kbCntrl)

	if '9' in kbCntrl.active:
		physicalObjects[circleObjN+0][1] -= 1000
		print "central mass -1000"
	if '0' in kbCntrl.active:
		physicalObjects[circleObjN+0][1] += 1000
		print "central mass +1000"

	physicalObjects[circleObjN+1][1] = 5000 if '1' in kbCntrl.active else 0
	physicalObjects[circleObjN+2][1] = 5000 if '2' in kbCntrl.active else 0
	physicalObjects[circleObjN+3][1] = 5000 if '3' in kbCntrl.active else 0
	physicalObjects[circleObjN+4][1] = 5000 if '4' in kbCntrl.active else 0
	physicalObjects[circleObjN+5][1] = 5000 if '5' in kbCntrl.active else 0
	physicalObjects[circleObjN+6][1] = 5000 if '6' in kbCntrl.active else 0

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
	circleObjN = 80

	drawRelativeVectors = False
	drawVelocity = False
	objects = []
	physicalObjects = []
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

	world.run()

