""" OpenGl gravity simulation n3

    context:
    - apply coulomb law as global field in one
      direction. try to generalize the concept
      of a general force between objects.

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
global externalEField
global physicalObjectsOriginal
global physicalObjectsSaved

def initContext(world):
	global arrow
	global physicalObjectsOriginal
	r = 3.0
	main_mass = 80000
	sat_mass = 1.0
	sat_v = sqrt(main_mass/r);
	dphi = 2*pi / circleObjN

	for obj in range(0,circleObjN):
		objects.append((objCube(0.1), r*cos(dphi*obj), -r*sin(dphi*obj), 0))
		physicalObjects.append([obj,[1.,1.],r*cos(dphi*obj),-r*sin(dphi*obj),0,sin(dphi*obj)*sat_v,cos(dphi*obj)*sat_v,0])
		physicalObjectsOriginal.append([obj,[1.,1.],r*cos(dphi*obj),-r*sin(dphi*obj),0,sin(dphi*obj)*sat_v,cos(dphi*obj)*sat_v,0])

	objects.append((objCube(0.1), 0,0,0))
	physicalObjects.append([circleObjN, [main_mass,0.], 0,0,0, 0,0,0])
	physicalObjectsOriginal.append([circleObjN, [main_mass,0.], 0,0,0, 0,0,0])


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

def accelleration(obja,objb):
	e0 = 25.
	dv = numpy.zeros((2,3))
	rel_ab = [objb[2]-obja[2],objb[3]-obja[3],objb[4]-obja[4]]
	d_2 = rel_ab[0]**2 + rel_ab[1]**2 + rel_ab[2]**2
	d_1 = sqrt(d_2)
	if d_2 != 0:
		fg = 1/d_2 if obja[1][0] and objb[1][0] else 0
		normal_rel_ab = [rel_ab[0]/d_1, rel_ab[1]/d_1, rel_ab[2]/d_1]

		dv[0][0] +=  (fg*objb[1][0]) * normal_rel_ab[0]
		dv[0][1] +=  (fg*objb[1][0]) * normal_rel_ab[1]
		dv[0][2] +=  (fg*objb[1][0]) * normal_rel_ab[2]
		dv[1][0] +=  (-fg*obja[1][0]) * normal_rel_ab[0]
		dv[1][1] +=  (-fg*obja[1][0]) * normal_rel_ab[1]
		dv[1][2] +=  (-fg*obja[1][0]) * normal_rel_ab[2]

		if obja[1][0]:
			dv[0][0] -= (e0*obja[1][1]/obja[1][0]) * externalEField[0]
			dv[0][1] -= (e0*obja[1][1]/obja[1][0]) * externalEField[1]
			dv[0][2] += (e0*obja[1][1]/obja[1][0]) * externalEField[2]
		if objb[1][0]:
			dv[1][0] -= (e0*objb[1][1]/objb[1][0]) * externalEField[0]
			dv[1][1] += (e0*objb[1][1]/objb[1][0]) * externalEField[1]
			dv[1][2] += (e0*objb[1][1]/objb[1][0]) * externalEField[2]
	return dv

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
						normal_rel_ab = [rel_ab[0]/d_1, rel_ab[1]/d_1, rel_ab[2]/d_1]
						dv_ab = accelleration(obja,objb)
						dv[oia][0] += dv_ab[0][0] * phys_dt
						dv[oia][1] += dv_ab[0][1] * phys_dt
						dv[oia][2] += dv_ab[0][2] * phys_dt
						dv[oib][0] += dv_ab[1][0] * phys_dt
						dv[oib][1] += dv_ab[1][1] * phys_dt
						dv[oib][2] += dv_ab[1][2] * phys_dt
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

		physicalObjects[oi][2] += physicalObjects[oi][5]*phys_dt
		physicalObjects[oi][3] += physicalObjects[oi][6]*phys_dt
		physicalObjects[oi][4] += physicalObjects[oi][7]*phys_dt

		oi += 1

def physics():
	convertPhysicsState()
	for obj in physicalObjects:
		(glObj,x,y,z) = objects[obj[0]]
		objects[obj[0]] = (glObj, obj[2],obj[3],obj[4])


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
		for obji in physicalObjects:
			if obji[1] > 0:
				glPushMatrix()
				glTranslatef(obji[2],obji[3],obji[4])
				objj = physicalObjects[circleObjN]
				arrow.color = [0.0,0.0,1.0,0]
				rel = [objj[2] - obji[2],objj[3] - obji[3],objj[4] - obji[4]]
				urel = sqrt(rel[0]**2+rel[1]**2+rel[2]**2)
				arrow.x = [rel[0]/urel,rel[1]/urel,rel[2]/urel]
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
	global externalEField
	global physicalObjectsOriginal
	global physicalObjectsSaved

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
		physicalObjects[circleObjN+0][1][0] -= 1000
		print "central mass -1000"
	if '0' in kbCntrl.active:
		physicalObjects[circleObjN+0][1][0] += 1000
		print "central mass +1000"
	if 'n' in kbCntrl.active:
		print "reset physics"
		for oi,obj in enumerate(physicalObjectsOriginal):
			physicalObjects[oi] = list(obj)
	if 'p' in kbCntrl.active:
		print "persist physics"
		physicalObjectsSaved = []
		for obj in physicalObjects:
			physicalObjectsSaved.append(list(obj))
	if 'l' in kbCntrl.active:
		print "load physics"
		for oi,obj in enumerate(physicalObjectsSaved):
			physicalObjects[oi] = list(obj)

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
	circleObjN = 60

	externalEField = [0.,0.,0.]
	drawRelativeVectors = False
	drawVelocity = False
	objects = []
	physicalObjects = []
	physicalObjectsOriginal = []
	physicalObjectsSaved= []
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

