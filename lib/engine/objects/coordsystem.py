from OpenGL.arrays import vbo
from OpenGLContext.arrays import *
from OpenGL.GL import *

class coordsystem():
	def __init__(self, a):
		verticies = [
			0,0,0, 1.0,0,0,
			a,0,0, 1.0,0,0,

			0,0,0, 0,1.0,0,
			0,a,0, 0,1.0,0,

			0,0,0, 0,0,1.0,
			0,0,a, 0,0,1.0,
		]
		self.vbo = vbo.VBO(array(verticies,'f'))


	def render(self):
		self.vbo.bind()
		glEnableClientState(GL_VERTEX_ARRAY);
		glEnableClientState(GL_COLOR_ARRAY);

		glVertexPointer(3, GL_FLOAT, 24, self.vbo)
		glColorPointer(3, GL_FLOAT, 24, self.vbo+12)
		glDrawArrays(GL_LINES, 0, 6)

		glDisableClientState(GL_VERTEX_ARRAY);
		glDisableClientState(GL_COLOR_ARRAY);
