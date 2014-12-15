from lib.engine.application import application
from sim1 import sim1
from lib.scene2 import scene2

class sim2(sim1):
	def __init__(self,app):
		self.app = app
		self.scene = scene2()
		self.scene.objN = 80

if __name__ == "__main__":
	app = application()
	sim = sim2(app)
	sim.prepare()
	app.run()
