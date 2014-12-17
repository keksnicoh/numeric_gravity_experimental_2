""" another setup of sim8"""


from OpenGLContext.arrays import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL import GL as gl
from OpenGL.GL.ARB.geometry_shader4 import *
from OpenGL.GL.EXT.geometry_shader4 import *

import numpy

from keyboard.fluent import fluent as kbCntrlFluent
from keyboard.flyaroundHandler import flyaroundHandler
from objects.cube import cube as objCube
from objects.arrow import arrow as objArrow
from world import world as World

GL_GEOMETRY_SHADER_EXT       = 0x8DD9
GL_GEOMETRY_INPUT_TYPE_EXT   = 0x8DDB
GL_GEOMETRY_OUTPUT_TYPE_EXT  = 0x8DDC
GL_GEOMETRY_VERTICES_OUT_EXT = 0x8DDA



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
global world
global p_color
global p_pos
global p_vel
global p_mass

c_obj_n  = 200000
p_loop_n = 0
p_dt     = 0.0001
c_r      = 1.0
p_eps    = 0.0000001

def initContext(world):
	global gl_o_arrow
	global p_obj
	global gl_obj
	global c_r
	global p_ww
	global p_color
	global p_pos
	global p_vel
	global p_mass
	shader_program = gl.glCreateProgram()

	shader_vert = glCreateShader(GL_VERTEX_SHADER)
	shader_frag = glCreateShader(GL_FRAGMENT_SHADER)
	shader_geom = glCreateShader(GL_GEOMETRY_SHADER_EXT)

	glShaderSource(shader_vert, open('shaders/sphere.v.glsl', 'r').read())
	glShaderSource(shader_frag, open('shaders/sphere.f.glsl', 'r').read())
	glShaderSource(shader_geom, open('shaders/sphere.g.glsl', 'r').read())

	glProgramParameteriEXT(shader_program, GL_GEOMETRY_INPUT_TYPE_EXT, gl.GL_POINTS)
	glProgramParameteriEXT(shader_program, GL_GEOMETRY_OUTPUT_TYPE_EXT, gl.GL_TRIANGLE_STRIP)
	glProgramParameteriEXT(shader_program, GL_GEOMETRY_VERTICES_OUT_EXT, 4)

	glCompileShader(shader_vert)
	log = glGetShaderInfoLog(shader_vert)
	if log: print 'Vertex Shader: ', log

	glCompileShader(shader_geom)
	log = glGetShaderInfoLog(shader_geom)
	if log: print 'Geometry Shader: ', log

	glCompileShader(shader_frag)
	log = glGetShaderInfoLog(shader_frag)
	if log: print 'Fragment Shader: ', log

	glAttachShader(shader_program, shader_vert)
	glAttachShader(shader_program, shader_frag)
	glAttachShader(shader_program, shader_geom)

	glLinkProgram(shader_program)
	log = glGetProgramInfoLog(shader_program)
	if log: print 'shader: ', log

	world.program.append(shader_program)
	glUseProgram(world.program[2])

	main_mass = 8000
	sat_mass  = 1
	physics,objs = [],[]
	p_color = numpy.random.random( (c_obj_n+1)*3 ).reshape( (-1,3) )
	p_pos = numpy.ones( (c_obj_n+1)*3 ).reshape( (-1,3) )
	p_vel = numpy.zeros( (c_obj_n+1)*3 ).reshape( (-1,3) )
	p_mass = numpy.ones( (c_obj_n+1) )

	"""create stable circle aroung (0,0,0)"""

	dphi = 1.5*pi / c_obj_n * 100
	factor = 3/float(c_obj_n)
	for obj in range(0,c_obj_n):
		sat_v = sqrt(main_mass/(1.2*c_r));
		p_pos[obj][0] = c_r*cos(dphi*obj)
		p_pos[obj][1] = -c_r*sin(dphi*obj)
		p_pos[obj][2] = 0

		p_vel[obj][0] = sin(dphi*obj)*sat_v
		p_vel[obj][1] = cos(dphi*obj)*sat_v
		p_vel[obj][2] = 0
		c_r += factor

	"""center mass"""
	p_pos[c_obj_n][0] = -.5
	p_pos[c_obj_n][1] = 0
	p_pos[c_obj_n][2] = 0

	p_vel[c_obj_n][0] = 0
	p_vel[c_obj_n][1] = 10
	p_vel[c_obj_n][2] = -40
	p_mass[c_obj_n] = main_mass

	physics.append([c_obj_n, -.5,0,0,  0,10,-30, main_mass,1.])

	#p_obj = numpy.array(physics)

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
	global p_pos,p_vel,p_mass
	ww_i = c_obj_n
	while ww_i < c_obj_n+1:
		d_pos    = p_pos[ww_i]-p_pos
		gm_by_r3 = p_mass[ww_i] / ((d_pos ** 2).sum(axis=1) + p_eps ** 2)**1.5
		accell   = (d_pos.T * gm_by_r3)
		p_vel   += accell.T * p_dt
		ww_i    += 1
	p_pos += p_vel * p_dt

def physics():
	n = 0
	while n < p_loop_n:
		physics_move()
		n+=1

def renderContext():
	"""render objects"""
	global gl_obj
	global world
	global p_color
	global p_pos

	glEnable(GL_BLEND);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	glDepthMask(False);
	glEnable(GL_ALPHA_TEST)
	glAlphaFunc(GL_GREATER,.01)

	glUseProgram(world.program[2])
	glEnableClientState( GL_COLOR_ARRAY )
	glEnableClientState( GL_VERTEX_ARRAY )
	glColorPointer( 3,GL_FLOAT,0,p_color )
	glVertexPointer(3,GL_FLOAT,0,p_pos )
	glDrawArrays( 0,0, len( p_pos ) )

def handleMovement(world, kbCntrl):
	global p_efield_ext
	global p_loop_n
	"""Keyboard controlling, uses keyboard.flyaroundHandler
	   to provide basic interaction"""
	flyaroundHandler(world, kbCntrl)

	"""central mass controller"""
	if '9' in kbCntrl.active:
		p_mass[c_obj_n] -= 500
		print "central mass -500"
	if '0' in kbCntrl.active:
		p_mass[c_obj_n] += 500
		print "central mass +500"

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
