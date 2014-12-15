from OpenGL.GLUT import *

class fluent():
	"""
	Simple class to fetch keybord events fluently.
	"""
	def __init__(self):
		""" contains a dictonary of active keys """
		self.active = {}
		self.stack = []

	def activate(self):
		glutKeyboardFunc(self.keyboardFunc)
		glutKeyboardUpFunc(self.keyboardUpFunc)

	def keyboardFunc(self, *args):
		self.active[args[0]] = True
		self.stack.append(args[0])

	def keyboardUpFunc(self, *args):
		del self.active[args[0]]
