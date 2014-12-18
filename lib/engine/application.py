"""base class for rendering scenes with
   opengl, glu, and pyclfw3.
   this class will setup an opengl4.1 compatible
   environment with shader versions: 410.
   Warning: no openGl2-3 operations supported e.g.
            - glMatrixMode, glBegin, ...

   @author Nicolas 'keksnicoh' Heimann <nicolas.heimann@gmail.com>
   """

from OpenGL.GL import *
import cyglfw3 as glfw
from sys import exc_info
from traceback import print_exc
from termcolor import colored
from math import pi
from pyrr.matrix44 import (multiply as m4dot, create_from_translation,
     create_from_x_rotation, create_from_y_rotation,
     create_perspective_projection_matrix)
import numpy

class application():
	def __init__(self, width=600, height=600, window_title="no title"):
		"""general window configuration"""
		self.window_title = window_title
		self.width        = width
		self.height       = height
		self.exit         = False
		"""camera configuration
		     camera_rotation
		     [R,R,R,R]
		     [R,R,_,_] current rotation angle
		     [_,_,R,R] rotation angle when left mouse btn released
		     camera_position
		     [R,R,R] x,y,z camera coord"""
		self.camera_rotation = [0,0,0,0]
		self.camera_position = [0,0,0]
		"""mouse_btn is a 2x5 matrix where
		   the first row represents the left button
		   and the second row the right button.
		    [B,R,R,R,R]
		    [B,_,_,_,_] button active flag
		    [_,R,R,_,_] position on button down
		    [_,_,_,R,R] position on button up"""
		self.mouse_btn = [[False,0,0,0,0],[False,0,0,0,0]]
		"""keyboard_stack [I,...] stack of pressed keys"""
		self.keyboardStack = []
		"""keyboard_active [I,...] contains all currently active keys"""
		self.keyboardActive = []

		"""events"""
		self.destruct = lambda w : None
		self.keyboard = lambda w : None
		self.scene    = lambda w : None

		print "* initialize application"
		self.initGlfw()
		print "- try to load OpenGL 4.1 core profile"
		self.initGlCoreProfile()
		self.initGlfwWindow()

		print 'Vendor: %s' %         glGetString(GL_VENDOR)
		print 'Opengl version: %s' % glGetString(GL_VERSION)
		print 'GLSL Version: %s' %   glGetString(GL_SHADING_LANGUAGE_VERSION)
		print 'Renderer: %s' %       glGetString(GL_RENDERER)
		print 'GLFW3: %s' %          glfw.GetVersionString()

		print "initialize matrices..."
		self._initM44()
		print "[OK] application is ready."

	def initGlCoreProfile(self):
		"""setup opengl 4.1"""
		glfw.WindowHint(glfw.OPENGL_FORWARD_COMPAT, 1)
		glfw.WindowHint(glfw.CONTEXT_VERSION_MAJOR, 4)
		glfw.WindowHint(glfw.CONTEXT_VERSION_MINOR, 1)
		glfw.WindowHint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

	def initGlfw(self):
		"""initialize glfw"""
		if not glfw.Init():
			raise RuntimeError('glfw.Init() error')

	def initGlfwWindow(self):
		"""initialize glwf window and attach callbacks"""
		self.window = glfw.CreateWindow(self.width,self.height,self.window_title)
		if not self.window:
			raise RuntimeError('glfw.CreateWindow() error')
		glfw.MakeContextCurrent(self.window)
		glfw.SetMouseButtonCallback(self.window, self.onMouse)
		glfw.SetKeyCallback(self.window, self.onKeyboard)

	def _initM44(self):
		"""initialize all provided matrices"""
		self.m44_camera_rotation_x = create_from_x_rotation(self.camera_rotation[1])
		self.m44_camera_rotation_y = create_from_y_rotation(self.camera_rotation[0])
		self.m44_camera_translation = create_from_translation(self.camera_position)

		self.m44_projection = create_perspective_projection_matrix(45.00, 3.0/4.0, 0.1, 1000, dtype=None)
		self._buildM44ModelView()

	def _buildM44ModelView(self):
		"""create a static model-view matrix
		   by using self.camera_position, self.camera_rotation"""
		self.m44_model_view_rotation = m4dot(self.m44_camera_rotation_y,self.m44_camera_rotation_x)
		self.m44_model_view = m4dot(self.m44_camera_translation,self.m44_model_view_rotation)

	def getCursorRelative(self):
		"""returns cursor position relative to window"""
		wx,wy = glfw.GetCursorPos(self.window)
		cx,cy = glfw.GetWindowPos(self.window)
		return cx-wx,cy-wy

	def onKeyboard(self, win, key, scancode, action, mods):
		if action == 0:
			self.keyboardActive.remove(key)
		elif action == 1:
			self.keyboardStack.append(key)
			self.keyboardActive.append(key)
		elif action == 2:
			self.keyboardStack.append(key)

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

	"""todo remove this from here"""
	def mouseDrag(self,world):
		if self.mouse_btn[0][0]:
			cx,cy = self.getCursorRelative()
			cx /= 150
			cy /= 150
			self.cameraRotateTo(
				 (cx + self.camera_rotation[2] - self.mouse_btn[0][1]/150) % (2*pi),
				 (cy + self.camera_rotation[3] - self.mouse_btn[0][2]/150) % (2*pi),
			)
	def cameraRotateTo(self,rx,ry):
		self.camera_rotation[0] = rx
		self.camera_rotation[1] = ry
		self.m44_camera_rotation_x = create_from_x_rotation(self.camera_rotation[1])
		self.m44_camera_rotation_y = create_from_y_rotation(self.camera_rotation[0])
		self._buildM44ModelView()

	def translateCameraRelative(self,position):
		self.camera_position = numpy.add(self.camera_position,position)
		self.m44_camera_translation = create_from_translation(self.camera_position)
		self._buildM44ModelView()

	def translateCamera(self,position):
		self.camera_position = numpy.array(position)
		self.m44_camera_translation = create_from_translation(self.camera_position)
		self._buildM44ModelView()

	def run(self):
		while not self.exit and not glfw.WindowShouldClose(self.window):
			"""todo move to a better place..."""
			try:
				glfw.PollEvents()
				self.scene(self)
				glfw.SwapBuffers(self.window)
			except:
				print_exc(exc_info()[0])
				print colored("try to shutdown...","yellow")
				self.terminate()
				print colored("program terminated due an unkown error!","red")
				break;
			try:
				self.keyboard(self)
				self.mouseDrag(self)
			except:
				print_exc(exc_info()[0])
				print colored("IO interrupted...","red", attrs=['reverse', 'blink'])
		self.terminate()

	def terminate(self):
		self.destruct(self)
		print "shutdown opengl application with following settings"
		print "world.camera_position =", self.camera_position
		print "world.camera_rotation =", self.camera_rotation
		glfw.DestroyWindow(self.window)
		glfw.Terminate()
