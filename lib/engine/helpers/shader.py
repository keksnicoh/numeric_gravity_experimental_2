from OpenGL.GL import *

def compile_shader(type, source):
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
	return shader

def compile_shader_from_file(type,file):
	return compile_shader(type,open(file, 'r').read())

def link_program(program):
	program_log = glGetProgramInfoLog(program)
	glLinkProgram(program)
	if program_log:
		raise RuntimeError("shader_program\n%s" % program_log)
