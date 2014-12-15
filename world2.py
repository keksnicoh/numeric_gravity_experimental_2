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
import cyglfw3 as glfw
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
		self.camera_rotation        = [0,0,0,0]
		self.camera_position = [0,0,0]
		self.destruct = lambda : None
		self.keyboard = lambda : None
		self.renderContext           = lambda : None
		self.sceneContext            = lambda : None
		self.scene            = lambda : None
		self.cursor = (0,0)
		self.mouse_btn = [[False,0,0,0,0],[False,0,0,0,0]]
		#self.leftMouseButtn
		self.keyboardStack = []
		self.keyboardActive = []
		# internal stuffff
		self.exit = False
		if not glfw.Init():
			raise RuntimeError('glfw.Init() error')

		window = glfw.CreateWindow(400,400,"bl")
		if not window:
			raise RuntimeError('glfw.CreateWindow() error')
		self.window = window

		glfw.MakeContextCurrent(window)
		glfw.SetMouseButtonCallback(self.window, self.onMouse)
		glfw.SetKeyCallback(self.window, self.onKeyboard);
		gluPerspective(45.0, float(self.width)/float(self.height), 0.1, 100.0)

		self.objCoordsystem = objCoordsystem(0.1)

	def onKeyboard(self, win, key, scancode, action, mods):
		if action == 0:
			self.keyboardActive.remove(key)
		elif action == 1:
			self.keyboardStack.append(key)
			self.keyboardActive.append(key)
		elif action == 2:
			self.keyboardStack.append(key)
		print key,scancode,action,mods

	def onMouse(self, win, button, action, mod):
		cursor = self.getCursorRelative()
		if button == 0:
			if action == 1:
				self.mouse_btn[0][0] = True
				self.mouse_btn[0][1] = cursor[0]
				self.mouse_btn[0][2] = cursor[1]
			elif action == 0:
				self.mouse_btn[0][0] = False
				self.mouse_btn[0][3] = cursor[0]
				self.mouse_btn[0][4] = cursor[1]
				self.camera_rotation[2] = self.camera_rotation[0]
				self.camera_rotation[3] = self.camera_rotation[1]

	def mouseDrag(self,world):
		if self.mouse_btn[0][0]:
			cx,cy = self.getCursorRelative()
			orx = self.camera_rotation[2]
			ory = self.camera_rotation[3]
			dx = orx + self.mouse_btn[0][1];
			dy = ory + self.mouse_btn[0][2];
			rx = (cx - dx) % 360
			ry = (cy - dy) % 360
			self.camera_rotation[0] = -rx
			self.camera_rotation[1] = -ry

	def run(self):
		while not self.exit:
			if glfw.WindowShouldClose(self.window):
				break

			self.keyboard(self)
			self.mouseDrag(self)
			self.scene(self)

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		self.destruct()
		print "shutdown opengl application with following settings"
		print "world.camera_position =", self.camera_position
		print "world.camera_rotation =", self.camera_rotation
		glfw.DestroyWindow(self.window)
		glfw.Terminate()

	def getCursorRelative(self):
		wx,wy = glfw.GetCursorPos(self.window)
		cx,cy = glfw.GetWindowPos(self.window)
		return cx-wx,cy-wy



	def renderRefsystem(self):
		glPushMatrix()
		glTranslatef(-0.35,-0.35,-1)
		glDisable(GL_DEPTH_TEST)
		glRotatef(self.camera_rotation[1],1,0,0)
		glRotatef(self.camera_rotation[0],0,1,0)
		self.objCoordsystem.render()
		glEnable(GL_DEPTH_TEST)
		glPopMatrix()

if __name__ == "__main__":
	world = world()
	world.run()


