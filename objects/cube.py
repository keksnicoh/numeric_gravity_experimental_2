from OpenGL.arrays import vbo
from OpenGLContext.arrays import *
from OpenGL.GL import *

class cube():
	def __init__(self, a):
		verticies = [
			0,0,0, 0.0,1.0,0.0,
			a,0,0, 0.0,1.0,0.0,
			a,a,0, 0.0,1.0,0.0,
			0,0,0, 0.0,1.0,0.0,
			a,a,0, 0.0,1.0,0.0,
			0,a,0, 0.0,1.0,0.0,

			0,0,a, 1.0,0.0,0.0,
			a,0,a, 1.0,0.0,0.0,
			a,a,a, 1.0,0.0,0.0,
			0,0,a, 1.0,0.0,0.0,
			a,a,a, 1.0,0.0,0.0,
			0,a,a, 1.0,0.0,0.0,

			a,0,0, 0.0,1.0,1.0,
			a,a,0, 0.0,1.0,1.0,
			a,a,a, 0.0,1.0,1.0,
			a,0,0, 0.0,1.0,1.0,
			a,a,a, 0.0,1.0,1.0,
			a,0,a, 0.0,1.0,1.0,

			0,0,0, 1.0,0.0,1.0,
			0,a,0, 1.0,0.0,1.0,
			0,a,a, 1.0,0.0,1.0,
			0,0,0, 1.0,0.0,1.0,
			0,a,a, 1.0,0.0,1.0,
			0,0,a, 1.0,0.0,1.0,

			0,0,0, 0.6,0.5,0.3,
			a,0,0, 0.6,0.5,0.3,
			a,0,a, 0.6,0.5,0.3,
			0,0,0, 0.6,0.5,0.3,
			a,0,a, 0.6,0.5,0.3,
			0,0,a, 0.6,0.5,0.3,

			0,a,0, 0.0,0.0,1.0,
			a,a,0, 0.0,0.0,1.0,
			a,a,a, 0.0,0.0,1.0,
			0,a,0, 0.0,0.0,1.0,
			a,a,a, 0.0,0.0,1.0,
			0,a,a, 0.0,0.0,1.0,
		]
		self.vbo = vbo.VBO(array(verticies,'f'))


	def render(self):
		self.vbo.bind()
		glEnableClientState(GL_VERTEX_ARRAY);
		glEnableClientState(GL_COLOR_ARRAY);

		glVertexPointer(3, GL_FLOAT, 24, self.vbo)
		glColorPointer(3, GL_FLOAT, 24, self.vbo+12)
		glDrawArrays(GL_TRIANGLES, 0, 36)

		glDisableClientState(GL_VERTEX_ARRAY);
		glDisableClientState(GL_COLOR_ARRAY);
