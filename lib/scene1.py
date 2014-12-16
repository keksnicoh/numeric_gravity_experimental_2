""" OpenGl gravity simulation n1

    context:
    - simulate basic newton law of gravity with
      correlation on each particle

    basic euler approximation of newtons gravity.
    approximation:
    - linear steps with length p_dt

    known issues:
    - singulaties when objects are close
    - no collision check
    - very slow due to big amout of python
      high level invocations

    author keksnicoh@googlemail.com
"""

from engine.scene import scene
from OpenGLContext.arrays import *
from OpenGL.GL import *
from engine.objects.cube import cube as objCube
from engine.objects.arrow import arrow as objArrow
from engine.helpers.shader import compile_shader_from_file, link_program
import os
class scene1(scene):
	def __init__(self):
		self.drawRelativeVectors = False
		self.drawVelocity = False
		self.objects = []
		self.physicalObjects = []
		self.phys_dt = 0.0001
		self.attachCenter = False
		self.objN = 0
		self.arrow = 0
		self.shader = None
		self.r = 3

	def prepare(self):
		r = self.r
		main_mass = 80000
		sat_mass = 1.0
		sat_v = sqrt(main_mass/r);
		dphi = 2*pi / self.objN
		for obj in range(0,self.objN):
			self.objects.append((objCube(0.1), r*cos(dphi*obj), -r*sin(dphi*obj), 0))
			self.physicalObjects.append([obj,sat_mass,r*cos(dphi*obj),-r*sin(dphi*obj),0,sin(dphi*obj)*sat_v,cos(dphi*obj)*sat_v,0])

		self.objects.append((objCube(0.1), 0,0,0))
		self.physicalObjects.append([self.objN, main_mass, 0,0,0, 0,0,0])

		self.objects.append((objCube(0.1), r,r,r))
		self.physicalObjects.append([self.objN+1, 0, r,r,r, 0,0,0])

		self.objects.append((objCube(0.1), -r,r,r))
		self.physicalObjects.append([self.objN+2, 0, -r,r,r, 0,0,0])

		self.objects.append((objCube(0.1), r,r,-r))
		self.physicalObjects.append([self.objN+3, 0, r,r,-r, 0,0,0])

		self.objects.append((objCube(0.1), -r,r,-r))
		self.physicalObjects.append([self.objN+4, 0, -r,r,-r, 0,0,0])

		self.objects.append((objCube(0.1), 0,0,r))
		self.physicalObjects.append([self.objN+5, 0, 0,0,r, 0,0,0])

		self.objects.append((objCube(0.1), 0,0,-r))
		self.physicalObjects.append([self.objN+6, 0, 0,0,-r, 0,0,0])

		self.arrow = objArrow()
		self.initShader()


	def initShader(self):
		vert_source = '%s/%s' % (os.path.dirname(__file__), 'engine/shaders/id.v.glsl')
		frag_source = '%s/%s' % (os.path.dirname(__file__), 'engine/shaders/id.f.glsl')

		shader_program = glCreateProgram()
		glAttachShader(shader_program, compile_shader_from_file(GL_VERTEX_SHADER, vert_source))
		glAttachShader(shader_program, compile_shader_from_file(GL_FRAGMENT_SHADER, frag_source))
		link_program(shader_program)
		self.shader = shader_program

	def getLengthSquared(self,v):
		return v[0]**2+v[1]**2+v[2]**2

	def getRelativeVector(self,x1,x2):
		return [x2[0]-x1[0],x2[1]-x1[1],x2[2]-x1[2]]

	def normalize(self,x):
		l = sqrt(self.getLengthSquared(x))
		return map(lambda x : x/l, x)

	def calculateDv(self,obji):
		objects = filter(lambda objj: objj[2:5] != obji[2:5], self.physicalObjects)
		dv = [.0,.0,.0]
		for objj in objects:
			dvj = self.caclculateDvj(obji,objj)
			dv[0] += dvj[0]
			dv[1] += dvj[1]
			dv[2] += dvj[2]
		return dv

	def caclculateDvj(self,obj1, obj2):
		if obj1[1]:
			rel = self.getRelativeVector(obj1[2:5],obj2[2:5])
			acc1 = 1*obj2[1] / self.getLengthSquared(rel)*self.phys_dt
			return map(lambda x: acc1*x, self.normalize(rel))
		else:
			return [0,0,0]

	def convertPhysicsState(self):
		objDv = []
		for obj in self.physicalObjects:
			objDv.append(self.calculateDv(obj))

		objCount = len(objDv)
		objIndex = 0
		while objIndex < objCount:
			dv = objDv[objIndex]

			self.physicalObjects[objIndex][5] += dv[0]
			self.physicalObjects[objIndex][6] += dv[1]
			self.physicalObjects[objIndex][7] += dv[2]

			self.physicalObjects[objIndex][2] += 0.5*self.physicalObjects[objIndex][5]*self.phys_dt
			self.physicalObjects[objIndex][3] += 0.5*self.physicalObjects[objIndex][6]*self.phys_dt
			self.physicalObjects[objIndex][4] += 0.5*self.physicalObjects[objIndex][7]*self.phys_dt

			objIndex += 1

	def physics(self):
		self.convertPhysicsState()
		for obj in self.physicalObjects:
			(glObj,x,y,z) = self.objects[obj[0]]
			self.objects[obj[0]] = (glObj, obj[2],obj[3],obj[4])

	def render(self,world):
		if self.attachCenter:
			world.camera_position[0] = -self.physicalObjects[self.objN][2]
			world.camera_position[1] = -self.physicalObjects[self.objN][3]
			world.camera_position[2] = -self.physicalObjects[self.objN][4] #wuuu...
		self.physics()

		glClear(GL_COLOR_BUFFER_BI | GL_DEPTH_BUFFER_BIT)
		glEnable(GL_DEPTH_TEST)
		glUseProgram(self.shader)

		obj = 0
		while obj < len(self.objects):
			if not self.attachCenter or obj != self.objN:
				(o, x, y, z) = self.objects[obj]
				glPushMatrix()
				glTranslatef(x,y,z)
				o.render()
				glPopMatrix()
			obj += 1

		if self.drawRelativeVectors:
			for obji in self.physicalObjects:
				if obji[1] > 0:
					glPushMatrix()
					glTranslatef(obji[2],obji[3],obji[4])
					for objj in self.physicalObjects:
						if objj[1] > 0:
							self.arrow.color = [0.0,0.0,1.0,0]
							self.arrow.x = self.normalize(self.getRelativeVector(obji[2:5],objj[2:5]))
							self.arrow.generateVBO()
							self.arrow.render()
					glPopMatrix()

		if self.drawVelocity:
			for obj in self.physicalObjects:
				glPushMatrix()
				glTranslatef(obj[2],obj[3],obj[4])
				self.arrow.color = [1.0,1.0,0.0,0.0]
				self.arrow.x = [.01*obj[5],.01*obj[6],.01*obj[7]]
				self.arrow.generateVBO()
				self.arrow.render()
				glPopMatrix()

		glPopMatrix() #end cam perspective
		glUseProgram(0)

	def destruct(self):
		self.objects = []
		self.physicalObjects = []
