""" OpenGl gravity simulation n7

    context:
    - assume that only massive particles are relevant
      for physical calculation

    basic euler approximation of newtons gravity.
    approximation:
    - linear steps with length p_dt
    - added p_eps to avoid singulaties in numpy
      matricies
    - only heavy particles correlate with
      each particle in the system

    known issues:
    - singulaties when objects are close
    - no collision check
    - the physic state is calculated pretty fast
      now. Problem is the opengl data assignment.
      In case of many particles, there are lots
      of matrices push/pop operations in each frame.

    author keksnicoh@googlemail.com
"""
from OpenGLContext.arrays import *
from OpenGL.GL import *
import numpy

from keyboard.fluent import fluent as kbCntrlFluent
from keyboard.flyaroundHandler import flyaroundHandler
from objects.cube import cube as objCube
from objects.arrow import arrow as objArrow
from world import world as World

#system configuration
global c_obj_n         # number of objects in the circle
global c_e0            # e-field constant
global c_r             # circle radius
#gl vars
global gl_obj          #world object data
#physical vars
global p_obj           #physical objects data
global p_dt            #length of a physics_move evolution
global p_loop_n        #how many physics_move applied each frame
global p_eps           #parameter to avoid singularities
global p_ww
#opengl objects
global gl_o_arrow

c_obj_n  = 3000
p_loop_n = 0
p_dt     = 0.0001
c_r      = 1.5
p_eps    = 0.0000001

def initContext(world):
	global gl_o_arrow
	global p_obj
	global gl_obj
	global c_r
	global p_ww

	main_mass = 8000
	sat_mass  = 1
	physics,objs = [],[]

	"""create stable circle aroung (0,0,0)"""
	sat_v = 1.5*sqrt(main_mass/c_r);
	dphi = 2*pi / c_obj_n
	for obj in range(0,c_obj_n):
		objs.append((objCube(0.05), c_r*cos(dphi*obj), -c_r*sin(dphi*obj), 0))
		physics.append([obj,c_r*cos(dphi*obj), -c_r*sin(dphi*obj),0,sin(dphi*obj)*sat_v, cos(dphi*obj)*sat_v,0,sat_mass,1.])

	"""center mass"""
	objs.append((objCube(0.2), -.5,0,0))
	physics.append([c_obj_n, -.5,0,0,  0,10,-40, main_mass,1.])

	objs.append((objCube(0.2), .5,0,0))
	physics.append([c_obj_n+1, .5,0,0, 0,-10,40, main_mass,1.])

	p_obj = numpy.array(physics)
	gl_obj = objs

	p_ww = numpy.array(p_ww)
	gl_o_arrow = objArrow()

	print "opengl simulation of bla"
	print "main control"
	print " - hold left mouse button to look around"
	print " - use w,a,s,d to fly around"
	print "   [ESC] exit"
	print "   [o]   toggle between shaders"

	print "physics manipulations:"
	print "   [+]   increase p_loop_n by 1"
	print "   [-]   decreate p_loop_n by q"
	print "   [9]   decrease center mass by 1000"
	print "   [0]   increase center mass by 1000"

def physics_move():
	"""calculates the motion of objects"""
	global p_obj, c_e0, p_eps, p_ww
	pos = p_obj[:, [1, 2, 3]]
	ww_i = c_obj_n
	while ww_i < c_obj_n+2:
		d_pos = pos[ww_i]-pos
		gm_by_r3 = p_obj[ww_i][7] / ((d_pos ** 2).sum(axis=1) + p_eps ** 2)**1.5
		accell = (d_pos.T * gm_by_r3)
		p_obj[:, [4,5,6]] += accell.T * p_dt
		ww_i += 1
	p_obj[:, [1,2,3]] += p_obj[:, [4,5,6]] * p_dt
def physics():
	n = 0
	while n < p_loop_n:
		physics_move()
		n+=1

def renderContext():
	"""render objects"""
	global gl_obj
	obj = 1
	while obj < c_obj_n+2:
		glPushMatrix()
		glTranslatef(p_obj[obj][1],p_obj[obj][2],p_obj[obj][3])
		gl_obj[obj][0].render()
		glPopMatrix()
		obj += 1

def handleMovement(world, kbCntrl):
	global p_efield_ext
	global p_loop_n
	"""Keyboard controlling, uses keyboard.flyaroundHandler
	   to provide basic interaction"""
	flyaroundHandler(world, kbCntrl)

	"""central mass controller"""
	if '9' in kbCntrl.active:
		p_obj[c_obj_n+0][7] -= 100
		print "central mass -100"
	if '0' in kbCntrl.active:
		p_obj[c_obj_n+0][7] += 100
		print "central mass +100"

	"""general control"""
	for key in kbCntrl.stack:
		if key == 'o':
			world.useShader = 1 if world.useShader == 0 else 0
			print "switch shader"
		if key == '+':
			p_loop_n += 1
		if key == '-':
			if p_loop_n > 0:
				p_loop_n -= 1

	kbCntrl.stack = []

if __name__ == "__main__":
	gl_obj = numpy.array([], dtype=float)
	p_obj = numpy.array([], dtype=float)
	p_ww = []

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
	#physics()
