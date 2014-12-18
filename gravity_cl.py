from lib.engine.application import application
from lib.engine.keyboard.flyaroundHandler import flyaroundHandler
from lib.simulation_scene import simulation_scene
from lib.particle_gravity_cl import particle_gravity_cl
import pyopencl as cl
from math import pi,sqrt,cos,sin
import numpy
import random

assert cl.have_gl()
class gravity_bh_controller():
	def __init__(self,app,c_obj_n):
		self.app = app
		self.scene = simulation_scene()

		self.c_obj_n = c_obj_n
		self.gravity = particle_gravity_cl()
		self.scene.objects.append(self.gravity)

	def prepare(self):
		# todo: this look hacky... better integrate
		# camera information into framework ...
		self.app.camera_position = [25.117134754661578, -4.4148233243429074, -20.328067450210863]
		self.app.camera_rotation = [5.428706140512919, 6.169773848846253, 5.428706140512919, 6.169773848846253]
		self.app._initM44()

		self.app.keyboard = flyaroundHandler
		self.app.destruct = self.destruct
		self.app.scene = self.scene.render

		print "load %d objects into particle_gravity" % self.c_obj_n
		self.configureObjects(self.c_obj_n)
		print "prepare particle_gravity"
		self.scene.prepare()
		print "[OK] simulation ready!"

	def configureObjects(self,c_obj_n):
		mass1 = 8000000
		mass2 = 8000000

		v1 = .5*sqrt(mass2/8.)
		v2 = .5*sqrt(mass1/8.)

		self.gravity.pushParticleToInitState([-4,0,0],[0,0,v1],mass1,2,True,[1,1,0])
		self.gravity.pushParticleToInitState([4,0,0],[0,0,-v2],mass2,2,True,[1,1,0])

		main_mass = mass1
		dphi      = 2*pi / c_obj_n
		c_r       = 20
		sat_v     = sqrt(main_mass/(c_r));
		for obj in range(0,c_obj_n):
			self.gravity.pushParticleToInitState(
				[1-rand[0]+c_r*cos(dphi*obj),1-rand[1],1-rand[2]-c_r*sin(dphi*obj),],
				[rand[3]+sin(dphi*obj)*sat_v,0,rand[4]+cos(dphi*obj)*sat_v],
				20, 0.1, False,
				[1-rand[6]/4.,0.5+rand[6]/4.,1-rand[6]/4.]
			)

	def destruct(self,word):
		self.scene.destruct()

if __name__ == "__main__":
	app = application()
	sim = gravity_bh_controller(app, 1000000)
	sim.prepare()
	app.run()
