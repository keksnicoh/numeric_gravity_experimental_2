""" OpenGl gravity simulation n6

    context:
    - reduce heavy data assignment after
      physics calculation by working
      directly on the physics state

    basic euler approximation of newtons gravity.
    approximation:
    - linear steps with length p_dt
    - added p_eps to avoid singulaties in numpy
      matricies

    known issues:
    - singulaties when objects are close
    - no collision check

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
global gl_draw_rel     #parameter: draw relative vectors
global gl_draw_vel     #parameter: draw velocity vectors
global gl_obj          #world object data
#physical vars
global p_obj           #physical objects data
global p_dt            #length of a physics_move evolution
global p_loop_n        #how many physics_move applied each frame
global p_eps           #parameter to avoid singularities
global p_ww
#opengl objects
global gl_o_arrow

c_obj_n  = 2000
p_loop_n = 1
p_dt     = 0.0001
c_e0     = 3000.
c_r      = 2.
p_eps    = 0.0000000001

def initContext(world):
	global gl_o_arrow
	global p_obj
	global gl_obj
	global c_r
	global p_ww

	main_mass = 800000
	sat_mass  = 1
	physics,objs = [],[]

	"""create stable circle aroung (0,0,0)"""
	sat_v = sqrt(main_mass/c_r);
	dphi = 2*pi / c_obj_n
	for obj in range(0,c_obj_n):
		objs.append((objCube(0.1), c_r*cos(dphi*obj), -c_r*sin(dphi*obj), 0))
		physics.append([obj,1+c_r*cos(dphi*obj), -c_r*sin(dphi*obj),.3,sin(dphi*obj)*sat_v, cos(dphi*obj)*sat_v,0,sat_mass,1.])

	"""center mass"""
	objs.append((objCube(0.1), 0,0,0))
	physics.append([c_obj_n, 0,0,0, 0,0,0, main_mass,1.])

	p_obj = numpy.array(physics)
	gl_obj = objs
	p_ww.append(p_obj[c_obj_n:c_obj_n+1])
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
	print "   [v]   draw velocity vectors for physical gl_obj"
	print "   [r]   draw relative vectors for physical gl_obj"

def physics_move():
	"""calculates the motion of objects"""
	global p_obj, c_e0, p_eps, p_ww
	pos = p_obj[:, [1, 2, 3]]
	n = len(pos)-1
	ww_pos,ww_m,ww_q = p_ww[0][:, [1, 2, 3]],p_ww[0][:,7],p_ww[0][:,8]

	o1i = 0
	while o1i < n:
		d_pos = ww_pos - pos[o1i]
		gm_by_r3 = ww_m / ((d_pos ** 2).sum(axis=1) + p_eps ** 2)**1.5
		accell = (d_pos.T * gm_by_r3).sum(axis=1)
		"""reassign data assuming only small changes so
		   it is not neccessary to buffer changes before
		   swapping them into the physical configuration"""
		p_obj[o1i][4] += accell[0] * p_dt
		p_obj[o1i][5] += accell[1] * p_dt
		p_obj[o1i][6] += accell[2] * p_dt

		p_obj[o1i][1] += p_obj[o1i][4] * p_dt
		p_obj[o1i][2] += p_obj[o1i][5] * p_dt
		p_obj[o1i][3] += p_obj[o1i][6] * p_dt
		o1i += 1



def physics():
	n = 0
	while n < p_loop_n:
		physics_move()
		n+=1
	for obj in p_obj:
		(glObj,x,y,z) = gl_obj[int(obj[0])]
		gl_obj[int(obj[0])] = (glObj, obj[1],obj[2],obj[3])

def renderContext():
	"""render objects"""
	obj = 0
	while obj < len(gl_obj):
		(o, x, y, z) = gl_obj[obj]
		glPushMatrix()
		glTranslatef(x,y,z)
		o.render()
		glPopMatrix()
		obj += 1

	"""render relative vectors"""
	if gl_draw_rel:
		for obji in p_obj:
			if obji[7] > 0:
				glPushMatrix()
				glTranslatef(obji[1],obji[2],obji[3])
				objj = p_obj[c_obj_n]
				gl_o_arrow.color = [0.0,0.0,1.0,0]
				rel = [objj[1] - obji[1],objj[2] - obji[2],objj[3] - obji[3]]
				urel = sqrt(rel[0]**2+rel[1]**2+rel[2]**2)
				gl_o_arrow.x = [rel[0]/urel,rel[1]/urel,rel[2]/urel]
				gl_o_arrow.generateVBO()
				gl_o_arrow.render()
				glPopMatrix()

	"""render velocity vectors"""
	if gl_draw_vel:
		for obj in p_obj:
			glPushMatrix()
			glTranslatef(obj[1],obj[2],obj[3])
			gl_o_arrow.color = [1.0,1.0,0.0,0.0]
			gl_o_arrow.x = [.005*obj[4],.005*obj[5],.005*obj[6]]
			gl_o_arrow.generateVBO()
			gl_o_arrow.render()
			glPopMatrix()

def handleMovement(world, kbCntrl):
	global gl_draw_rel
	global gl_draw_vel
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
		if key == 'r':
			gl_draw_rel = False if gl_draw_rel else True
		if key == 'v':
			gl_draw_vel = False if gl_draw_vel else True
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
	gl_draw_rel = False
	gl_draw_vel = False
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
	physics()
