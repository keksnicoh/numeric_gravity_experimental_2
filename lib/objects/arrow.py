from OpenGL.arrays import vbo
from OpenGLContext.arrays import *
from OpenGL.GL import *

class arrow():
	def __init__(self):
		self.x = [0,0,0]
		self.color = [1.0,0.0,0.0]
		self.generateVBO()

	def generateVBO(self):
		verticies = [
			0,0,0, 0.0,0,0,
			self.x[0],self.x[1],self.x[2], self.color[0], self.color[1], self.color[2],
		]
		self.vbo = vbo.VBO(array(verticies,'f'))

	def render(self):
		self.vbo.bind()
		glEnableClientState(GL_VERTEX_ARRAY);
		glEnableClientState(GL_COLOR_ARRAY);

		glVertexPointer(3, GL_FLOAT, 24, self.vbo)
		glColorPointer(3, GL_FLOAT, 24, self.vbo+12)
		glDrawArrays(GL_LINES, 0, 2)

		glDisableClientState(GL_VERTEX_ARRAY);
		glDisableClientState(GL_COLOR_ARRAY);
