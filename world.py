from OpenGL.arrays import vbo
from OpenGLContext.arrays import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GL import shaders
from keyboard.fluent import fluent as kbCntrlFluent
from objects.cube import cube as objCube
from objects.coordsystem import coordsystem as objCoordsystem
from objects.arrow import arrow as objArrow
from keyboard.flyaroundHandler import flyaroundHandler
from clock import clock
import time
import math
#from OpenGL.raw.GL import glTranslatef
"""this mock of a world is able to perform
buggy movements and basic rendering cycles
using the same shader tuble for all objects"""
class world():
	def __init__(self):
		# configuration
		self.windowTitle     = ""
		self.width           = 600
		self.height          = 600
		self.rotation        = [0,0,0,0]
		self.camera_position = [0,0,0]

		self.keyboardTriggerCallback = lambda : None
		self.renderContext           = lambda : None
		self.sceneContext            = lambda : None

		# internal stuffff
		self.exit = False
		self.mouseData = [0,0,0,0,self.rotation[0],self.rotation[1]]
		self.clock = clock();

		# // field of view, aspect ratio, near and far
		# This will squash and stretch our objects as the window is resized.
		self.initGLUT()
		self.initGLU()
		self.initGL()
		self.initShaders()

		self.objCoordsystem = objCoordsystem(0.1)

	def initGL(self):
		glClearColor(0.0, 0.0, 0.0, 0.0)
		glViewport(0, 0, self.width, self.height)
		glEnable(GL_DEPTH_TEST)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()

	def initGLU(self):
		gluPerspective(45.0, float(self.width)/float(self.height), 0.1, 100.0)


	def initGLUT(self):
		glutInit(sys.argv)
		glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
		glutInitWindowSize(self.width, self.height)
		glutCreateWindow(self.windowTitle)
		glutDisplayFunc(self.render)
		glutIdleFunc(self.scene)
		glutMotionFunc(self.mouseDrag)
		glutMouseFunc(self.mouse)

	def metaController(self, world):
		if world.exit:
			print "shutdown opengl application with following settings"
			print "world.camery_position =", self.camera_position
			print "world.rotation =", self.rotation
			sys.exit()

	def initShaders(self):
		self.useShader = 1

		VERTEX_SHADER = shaders.compileShader("""#version 120
			uniform float end_fog;
			uniform vec4 fog_color;
			varying vec4 vertex_color;
			void main() {
				float fog;
				float fog_coord;
				gl_Position = ftransform();
				//gl_Position = gl_ProjectionMatrix * gl_ModelViewMatrix * gl_Vertex;
				vertex_color = gl_Color;
				fog_coord = abs(gl_Position.z);
				fog_coord = clamp( fog_coord, 0.0, end_fog);
				fog = (end_fog-fog_coord)/end_fog;
				fog = clamp( fog, 0.0, 3.0);
				gl_FrontColor = mix(fog_color, gl_Color, fog);

			}
		""", GL_VERTEX_SHADER )

		FRAGMENT_SHADER = shaders.compileShader("""
			void main() {
				gl_FragColor = gl_Color;
			}
		""",GL_FRAGMENT_SHADER)

		self.program = []
		self.program.append(shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER))

		VERTEX_SHADER = shaders.compileShader("""#version 120
			varying vec4 vertex_color;
			void main() {
				gl_Position = ftransform();
				gl_FrontColor = gl_Color;

			}
		""", GL_VERTEX_SHADER )

		FRAGMENT_SHADER = shaders.compileShader("""
			void main() {
				gl_FragColor = gl_Color;
			}
		""",GL_FRAGMENT_SHADER)

		self.program.append(shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER))

		self.UNIFORM_LOCATIONS = {
			'end_fog': glGetUniformLocation( self.program[0], 'end_fog' ),
			'fog_color': glGetUniformLocation( self.program[0], 'fog_color' ),
		}

	def mouse(self, button, state, x, y):
		if button == 0 and state == 0:
			self.mouseData[0] = x
			self.mouseData[1] = y
		if button == 0 and state == 1:
			self.mouseData[2] = x
			self.mouseData[3] = y
			self.mouseData[4] = self.rotation[0]
			self.mouseData[5] = self.rotation[1]

		print self.mouseData

	def mouseDrag(self, x, y):
		dx = self.mouseData[4] - self.mouseData[0];
		dy = self.mouseData[5] - self.mouseData[1];
		rx = (x + dx) % 360
		ry = (y + dy) % 360
		self.rotation = [rx,ry]

	def run(self):
		glutMainLoop()

	def scene(self):
		self.metaController(self)
		self.keyboardTriggerCallback()
		self.clock.tick()
		self.sceneContext()
		self.render()

	def render(self):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		# scene context
		glMatrixMode(GL_MODELVIEW) #cam perspective
		glPushMatrix()
		glRotatef(self.rotation[1],1,0,0)
		glRotatef(self.rotation[0],0,1,0)
		glTranslatef(self.camera_position[0],self.camera_position[1],self.camera_position[2])
		self.renderContext()
		glPopMatrix() #end cam perspective

		glutSwapBuffers()
		glUseProgram(0)

	def renderRefsystem(self):
		glPushMatrix()
		glTranslatef(-0.35,-0.35,-1)
		glDisable(GL_DEPTH_TEST)
		glRotatef(self.rotation[1],1,0,0)
		glRotatef(self.rotation[0],0,1,0)
		self.objCoordsystem.render()
		glEnable(GL_DEPTH_TEST)
		glPopMatrix()

if __name__ == "__main__":
	world = world()
	world.run()


