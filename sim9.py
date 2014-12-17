from lib.engine.application import application
from lib.engine.keyboard.flyaroundHandler import flyaroundHandler
from lib.simulation_scene import simulation_scene
from lib.particle_gravity import particle_gravity

from math import pi,sqrt,cos,sin
import numpy
import random

class sim9():
	def __init__(self,app):
		self.app = app
		self.scene = simulation_scene()

		self.gravity = particle_gravity()
		self.scene.objects.append(self.gravity)

	def prepare(self):
		self.app.camera_position = [25.117134754661578, -4.4148233243429074, -20.328067450210863]
		self.app.camera_rotation = [5.428706140512919, 6.169773848846253, 5.428706140512919, 6.169773848846253]
		self.app._initM44()
		self.app.keyboard = flyaroundHandler
		self.app.destruct = self.destruct
		self.app.scene = self.scene.render

		main_mass = 800000
		c_obj_n   = 600
		dphi      = 2*pi / c_obj_n
		c_r       = 6
		sat_v     = sqrt(main_mass/(c_r));
		for obj in range(0,c_obj_n):
			rand = [
				round(random.uniform(0.1, 1.0), 10),
				round(random.uniform(0.1, 1.0), 10),
				round(random.uniform(0.1, 1.0), 10),
				round(random.uniform(0.1, 1.0), 10),
				round(random.uniform(0.1, 1.0), 10),
				round(random.uniform(0.1, 1.0), 10),
			]
			self.gravity.pushParticleToInitState(
				[rand[0]+c_r*cos(dphi*obj),rand[1]+-c_r*sin(dphi*obj),rand[2]+1],
				[rand[3]+sin(dphi*obj)*sat_v,rand[4]+cos(dphi*obj)*sat_v,rand[5]+1],50
			)

		self.gravity.pushParticleToInitState([0,0,0],[0,0,0],800000)
		self.scene.prepare()

	def destruct(self,word):
		self.scene.destruct()

if __name__ == "__main__":
	app = application()
	sim = sim9(app)
	sim.prepare()
	app.run()
