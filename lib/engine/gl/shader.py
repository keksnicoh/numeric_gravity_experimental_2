from OpenGL.GL import (glCompileShader, glShaderSource, glCreateProgram,
	glCreateShader, glAttachShader, glLinkProgram, glGetUniformLocation,
	glGetShaderInfoLog, glGetAttribLocation, glUseProgram, GL_FRAGMENT_SHADER,
	GL_VERTEX_SHADER, GL_GEOMETRY_SHADER)

class shader(object):
	def __init__(self):
		self.program_id = glCreateProgram()

	def attachShader(self,type,source):
		shader = glCreateShader(type)
		glShaderSource(shader,source)
		glCompileShader(shader)
		shader_log = glGetShaderInfoLog(shader)
		if shader_log:
			if type == GL_FRAGMENT_SHADER:
				str_type = "GL_FRAGMENT_SHADER"
			elif type == GL_VERTEX_SHADER:
				str_type = "GL_VERTEX_SHADER"
			elif type == GL_GEOMETRY_SHADER:
				str_type = "GL_GEOMETRY_SHADER"
			else:
				str_type = "unkown shader type %s" % str(type)
			raise RuntimeError("%s\n%s" % (str_type, shader_log))
		glAttachShader(self.program_id, shader)

	def uniformLocation(self, name):
		return glGetUniformLocation(self.program_id, name)

	def attributeLocation(self, name):
		return glGetAttribLocation(self.program_id, name)

	def linkProgram(self):
		glLinkProgram(self.program_id)
	def useProgram(self):
		glUseProgram(self.program_id)
