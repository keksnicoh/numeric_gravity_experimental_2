#!/usr/bin/python
import cyglfw3 as glfw

from OpenGL.GL import *
from OpenGL.raw import GL
from OpenGL.arrays import ArrayDatatype as ADT
if not glfw.Init():
    exit()
version = 3,2
import numpy
glfw.WindowHint(glfw.CONTEXT_VERSION_MAJOR, version[0])
glfw.WindowHint(glfw.CONTEXT_VERSION_MINOR, version[1])
glfw.WindowHint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
glfw.WindowHint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
#GL.glClear(GL.GL_COLOR_BUFFER_BIT);
window = glfw.CreateWindow(640, 480, 'Hello World')
if not window:
    glfw.Terminate()
    print 'Failed to create window'
    exit()

#glfw.MakeContextCurrent(window)
#print GL.glGetString(GL.GL_VERSION)
#print('GLFW3:',glfw.GetVersionString())
#glPushMatrix()
#glMatrixMode(GL.GL_MODELVIEW)
class VertexBuffer(object):

	def __init__(self, data, usage):
		self.buffer = GLuint(0)
		glGenBuffers(1, self.buffer)
		self.buffer = self.buffer.value
		glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
		glBufferData(GL_ARRAY_BUFFER, ADT.arrayByteCount(data),
		ADT.voidDataPointer(data), usage)

vertices = numpy.array([0.5, 0.5, -0.5, 0.5, -0.5, -0.5, 0.5, -0.5], dtype='float32')
v = VertexBuffer(vertices,GL_STATIC_DRAW)
glfw.PollEvents()
glfw.DestroyWindow(window)
glfw.Terminate()
