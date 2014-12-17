from engine.scene import scene
from OpenGLContext.arrays import *
from OpenGL.GL import *
from engine.objects.cube import cube as objCube
from engine.objects.arrow import arrow as objArrow
from engine.helpers.shader import compile_shader_from_file, link_program
import os
class simulation_scene(scene):
	def __init__(self):
		self.objects = []
	def prepare(self):
		print "prepare simulation scene..."
		for obj in self.objects:
			print "... object ", obj
			obj.prepare();
		pass

	def render(self,world):
		glEnable(GL_DEPTH_TEST)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		for obj in self.objects:
			obj.render(world);

	def destruct(self):
		self.objects = []
		self.physicalObjects = []
