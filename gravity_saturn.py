from lib.engine.application import application
from lib.engine.keyboard.flyaroundHandler import flyaroundHandler
from lib.simulation_scene import simulation_scene
from lib.particle_gravity import particle_gravity

from math import pi,sqrt,cos,sin
import numpy
import random
from gravity_bh import gravity_bh_controller
class gravity_saturn_controller(gravity_bh_controller):

	def configureObjects(self,c_obj_n):
		self.gravity.pushParticleToInitState([0,0,0],[0,0,0],800000,15,True,[1,1,0])

		main_mass = 800000
		dphi      = 2*pi / c_obj_n
		c_r       = 10
		sat_v     = sqrt(main_mass/(c_r));
		for obj in range(0,c_obj_n):
			# apply some randomnes
			rand = numpy.random.rand(7)*2
			self.gravity.pushParticleToInitState(
				[1-rand[0]+c_r*cos(dphi*obj),.1-rand[2]/20.,1-rand[1]+-c_r*sin(dphi*obj)],
				[rand[3]+sin(dphi*obj)*sat_v,1-rand[2]/20,rand[4]+cos(dphi*obj)*sat_v],
				50+rand[6]*50, 0.05, False,
				[1-rand[6]/4.,0.5+rand[6]/4.,1-rand[6]/4.]
			)

if __name__ == "__main__":
	app = application()
	sim = gravity_saturn_controller(app, 1000000)
	sim.prepare()
	app.run()
