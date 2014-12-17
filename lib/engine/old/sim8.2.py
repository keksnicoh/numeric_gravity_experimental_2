""" another setup of sim8
"""

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
global attachCenter
c_obj_n  = 200000
p_loop_n = 0
p_dt     = 0.0001
c_r      = 10.0
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
	p_color = numpy.random.random( (c_obj_n+2)*3 ).reshape( (-1,3) )
	p_pos = numpy.ones( (c_obj_n+2)*3 ).reshape( (-1,3) )
	p_vel = numpy.zeros( (c_obj_n+2)*3 ).reshape( (-1,3) )
	p_mass = numpy.ones( (c_obj_n+2) )

	"""create stable circle aroung (0,0,0)"""

	dphi = 1.5*pi / c_obj_n * 100

	for obj in range(0,c_obj_n):
		if not obj % 4000:
			c_r += 0.11
			sat_v = sqrt(main_mass/c_r)

		p_pos[obj][0] = c_r*cos(dphi*obj)
		p_pos[obj][1] = 0
		p_pos[obj][2] = -c_r*sin(dphi*obj)

		p_vel[obj][0] = sin(dphi*obj)*sat_v
		p_vel[obj][1] = 0
		p_vel[obj][2] = cos(dphi*obj)*sat_v

	"""center mass"""
	p_pos[c_obj_n][0] = 0
	p_pos[c_obj_n][1] = 0
	p_pos[c_obj_n][2] = 0

	p_vel[c_obj_n][0] = 0
	p_vel[c_obj_n][1] = 0
	p_vel[c_obj_n][2] = 0
	p_mass[c_obj_n] = main_mass

	c_r -= 1.375
	moon_mass = 5
	moon_v = sqrt(main_mass/c_r)

	p_pos[c_obj_n+1][0] = c_r
	p_pos[c_obj_n+1][1] = .1
	p_pos[c_obj_n+1][2] = 0

	p_vel[c_obj_n+1][0] = 0
	p_vel[c_obj_n+1][1] = 0
	p_vel[c_obj_n+1][2] = -moon_v
	p_mass[c_obj_n+1] = moon_mass

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
	"""calculates objects motion"""
	global p_pos,p_vel,p_mass,p_eps
	ww_i = c_obj_n
	while ww_i < c_obj_n+2:
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
	global attachCenter
	global c_obj_n
	#glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
	if attachCenter:
		world.camera_position[0] = -p_pos[c_obj_n+1][0]
		world.camera_position[1] = -p_pos[c_obj_n+1][1]-1
		world.camera_position[2] = -p_pos[c_obj_n+1][2] #wuuu...

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
	global attachCenter
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
	if '1' in kbCntrl.active:
		p_mass[c_obj_n+1] -= 1
		print "moon mass -100"
	if '2' in kbCntrl.active:
		p_mass[c_obj_n+1] += 2
		print "moon mass +100"
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
		if key == 'c':
			attachCenter = False if attachCenter else True

	kbCntrl.stack = []

if __name__ == "__main__":
	gl_obj = numpy.array([], dtype=float)
	p_obj = numpy.array([], dtype=float)
	p_ww = []
	attachCenter = False
	world = World()
	world.camery_position = [4.1412688087349974, -2.0686565258245126, 2.9122694037475161]
	world.rotation = [124, 17]
	world.mouseData       = [0,0,0,0,world.rotation[0],world.rotation[1]]

	# keyboard control
	kbCntrl = kbCntrlFluent()
	kbCntrl.activate()
	world.keyboardTriggerCallback = lambda : handleMovement(world, kbCntrl)
	world.sceneContext = physics
	world.renderContext = renderContext

	initContext(world)
	world.run()
