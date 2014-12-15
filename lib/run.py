import world from world2

if __name__ == "__main__":

	world = World()
	world.camera_position = [3.2216284299338929, -8.0277272964718041, -7.4030994749181191]
	world.camera_rotation = [-319.72265625, -309.3828125, -319.72265625, -309.3828125]


	world.destruct = scene.destruct
	world.keyboard = handleMovement
	world.scene = scene


	world.run()

