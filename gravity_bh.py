from lib.engine.application import application
from lib.engine.keyboard.flyaroundHandler import flyaroundHandler
from lib.simulation_scene import simulation_scene
from lib.particle_gravity import particle_gravity

from math import pi,sqrt,cos,sin
import numpy
import random

class gravity_bh_controller():
	def __init__(self,app,c_obj_n):
		self.app = app
		self.scene = simulation_scene()

		self.c_obj_n = c_obj_n
		self.gravity = particle_gravity()
		self.scene.objects.append(self.gravity)

	def prepare(self):
		# todo: this look hacky... better integrate
		# camera information into framework ...
		self.app.camera_position = [25.117134754661578, -4.4148233243429074, -20.328067450210863]
		self.app.camera_rotation = [5.428706140512919, 6.169773848846253, 5.428706140512919, 6.169773848846253]
		self.app._initM44()

		self.app.keyboard = self.keyboard
		self.app.destruct = self.destruct
		self.app.scene = self.scene.render
		print "load %d objects into particle_gravity" % self.c_obj_n
		self.configureObjects(self.c_obj_n)
		print "prepare particle_gravity"
		self.scene.prepare()
		print "[OK] simulation ready!"
	def configureObjects(self,c_obj_n):
		self.gravity.pushParticleToInitState([0,0,0],[0,0,0],800000,2,True,[1,1,0])

		main_mass = 800000
		dphi      = 2*pi / c_obj_n
		c_r       = 6
		sat_v     = sqrt(main_mass/(c_r));
		for obj in range(0,c_obj_n):
			# apply some randomnes
			rand = numpy.random.rand(7)*2
			self.gravity.pushParticleToInitState(
				[1-rand[0]+c_r*cos(dphi*obj),1-rand[1]+-c_r*sin(dphi*obj),.5-rand[2]/2.],
				[rand[3]+sin(dphi*obj)*sat_v,rand[4]+cos(dphi*obj)*sat_v,rand[5]+1],
				50+rand[6]*50, 0.1, False,
				[1-rand[6]/4.,0.5+rand[6]/4.,1-rand[6]/4.]
			)
	def keyboard(self,world):
		flyaroundHandler(world)
		if ord('9') in world.keyboardActive:
			self.gravity._p_mass[0] += 10000
		if ord('8') in world.keyboardActive:
			self.gravity._p_mass[0] -= 10000
		if ord('T') in world.keyboardActive:
			self.gravity._p_pos[0][0] += .3
		if ord('G') in world.keyboardActive:
			self.gravity._p_pos[0][0] -= .3
		if ord('F') in world.keyboardActive:
			self.gravity._p_pos[0][2] += .3
		if ord('H') in world.keyboardActive:
			self.gravity._p_pos[0][2] -= .3

	def destruct(self,word):
		self.scene.destruct()

if __name__ == "__main__":
	app = application()
	sim = gravity_bh_controller(app, 500000)
	sim.prepare()
	app.run()
