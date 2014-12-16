"""base class for rendering scenes with
   opengl, glu, and pyclfw3.
   this class will setup an opengl4 compatible
   environment with shader versions: 410
   @author Nicolas 'keksnicoh' Heimann <nicolas.heimann@gmail.com>
   """

import OpenGL.GLU as GLU
import OpenGL.GL as GL
import cyglfw3 as glfw
import sys
import traceback
from termcolor import colored

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

		self.initGlfw()
		self.initGlCoreProfile()
		self.initGLU()

	def initGlfw(self):
		if not glfw.Init():
			raise RuntimeError('glfw.Init() error')

		self.window = glfw.CreateWindow(self.width,self.height,self.window_title)
		if not self.window:
			raise RuntimeError('glfw.CreateWindow() error')

		glfw.MakeContextCurrent(self.window)
		glfw.SetMouseButtonCallback(self.window, self.onMouse)
		glfw.SetKeyCallback(self.window, self.onKeyboard)

	def initGlCoreProfile(self):
		glfw.WindowHint(glfw.CONTEXT_VERSION_MAJOR, 3)
		glfw.WindowHint(glfw.CONTEXT_VERSION_MINOR, 2)
		glfw.WindowHint(glfw.OPENGL_FORWARD_COMPAT, 1)
		glfw.WindowHint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

	def initGLU(self):
		GLU.gluPerspective(45.0, float(self.width)/float(self.height), 0.1, 100.0)

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
			self.updateCameraRotation(
				 -(cx - self.camera_rotation[2] - self.mouse_btn[0][1]) % 360,
				 -(cy - self.camera_rotation[3] - self.mouse_btn[0][2]) % 360
			)
	def updateCameraRotation(self,rx,ry):
			self.camera_rotation[0] = rx
			self.camera_rotation[1] = ry

	def run(self):
		while not self.exit and not glfw.WindowShouldClose(self.window):
			GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
			GL.glMatrixMode(GL.GL_MODELVIEW)
			GL.glPushMatrix()
			GL.glRotatef(self.camera_rotation[1],1,0,0)
			GL.glRotatef(self.camera_rotation[0],0,1,0)
			GL.glTranslatef(self.camera_position[0],self.camera_position[1],self.camera_position[2])

			try:
				self.scene(self)
				glfw.SwapBuffers(self.window)
			except:
				traceback.print_exc(sys.exc_info()[0])
				print colored("try to shutdown...","yellow")
				self.terminate()
				print colored("program terminated due an unkown error!","red")
				break;
			try:
				self.keyboard(self)
				self.mouseDrag(self)
			except:
				traceback.print_exc(sys.exc_info()[0])
				print colored("IO interrupted...","red", attrs=['reverse', 'blink'])

			glfw.PollEvents()

	def terminate(self):
		self.destruct(self)
		print "shutdown opengl application with following settings"
		print "world.camera_position =", self.camera_position
		print "world.camera_rotation =", self.camera_rotation
		glfw.DestroyWindow(self.window)
		glfw.Terminate()
