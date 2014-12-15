from lib.engine.application import application
from lib.engine.keyboard.flyaroundHandler import flyaroundHandler
from lib.scene1 import scene1

class sim1():
	def __init__(self,app):
		self.app = app
		self.scene = scene1()
		self.scene.objN = 40

	def prepare(self):
		self.app.camera_position = [3.2216284299338929, -8.0277272964718041, -7.4030994749181191]
		self.app.camera_rotation = [-319.72265625, -309.3828125, -319.72265625, -309.3828125]

		self.app.keyboard = self.keyboard
		self.app.destruct = self.scene.destruct
		self.app.scene = self.scene.render
		self.scene.prepare()

	def keyboard(self,app):
		"""Keyboard controlling, uses keyboard.flyaroundHandler
		   to provide basic interaction"""
		flyaroundHandler(app)

		if ord('9') in app.keyboardActive:
			self.scene.physicalObjects[self.scene.objN+0][1] -= 1000
			print "central mass -1000"
		if ord('0') in app.keyboardActive:
			self.scene.physicalObjects[self.scene.objN+0][1] += 1000
			print "central mass +1000"

		self.scene.physicalObjects[self.scene.objN+1][1] = 5000 if ord('1') in app.keyboardActive else 0
		self.scene.physicalObjects[self.scene.objN+2][1] = 5000 if ord('2') in app.keyboardActive else 0
		self.scene.physicalObjects[self.scene.objN+3][1] = 5000 if ord('3') in app.keyboardActive else 0
		self.scene.physicalObjects[self.scene.objN+4][1] = 5000 if ord('4') in app.keyboardActive else 0
		self.scene.physicalObjects[self.scene.objN+5][1] = 5000 if ord('5') in app.keyboardActive else 0
		self.scene.physicalObjects[self.scene.objN+6][1] = 5000 if ord('6') in app.keyboardActive else 0

		for key in app.keyboardStack:
			if key == ord('R'):
				self.scene.drawRelativeVectors = False if self.scene.drawRelativeVectors else True
			if key == ord('V'):
				self.scene.drawVelocity = False if self.scene.drawVelocity else True
			if key == 93:
				self.scene.phys_dt += 0.0001
			if key == 47:
				self.scene.phys_dt -= 0.0001
			if key == ord('C'):
				self.scene.attachCenter = False if self.scene.attachCenter else True

		app.keyboardStack = []

if __name__ == "__main__":
	app = application()
	sim = sim1(app)
	sim.prepare()
	app.run()
