from lib.engine.application import application
from lib.engine.keyboard.flyaroundHandler import flyaroundHandler
from lib.simulation_scene import simulation_scene
from lib.particle_gravity import particle_gravity
import numpy
from OpenGLContext.arrays import *

import pyrr
from OpenGL.GL import *
class ShaderProgram(object):
    """ Helper class for using GLSL shader programs
    """
    def __init__(self, vertex, fragment):
        """
        Parameters
        ----------
        vertex : str
            String containing shader source code for the vertex
            shader
        fragment : str
            String containing shader source code for the fragment
            shader

        """
        self.program_id = glCreateProgram()
        vs_id = self.add_shader(vertex, GL_VERTEX_SHADER)
        frag_id = self.add_shader(fragment, GL_FRAGMENT_SHADER)

        glAttachShader(self.program_id, vs_id)
        glAttachShader(self.program_id, frag_id)
        glLinkProgram(self.program_id)

        if glGetProgramiv(self.program_id, GL_LINK_STATUS) != GL_TRUE:
            info = glGetProgramInfoLog(self.program_id)
            glDeleteProgram(self.program_id)
            glDeleteShader(vs_id)
            glDeleteShader(frag_id)
            raise RuntimeError('Error linking program: %s' % (info))
        glDeleteShader(vs_id)
        glDeleteShader(frag_id)

    def add_shader(self, source, shader_type):
        """ Helper function for compiling a GLSL shader

        Parameters
        ----------
        source : str
            String containing shader source code

        shader_type : valid OpenGL shader type
            Type of shader to compile

        Returns
        -------
        value : int
            Identifier for shader if compilation is successful

        """
        try:
            shader_id = glCreateShader(shader_type)
            glShaderSource(shader_id, source)
            glCompileShader(shader_id)
            if glGetShaderiv(shader_id, GL_COMPILE_STATUS) != GL_TRUE:
                info = glGetShaderInfoLog(shader_id)
                raise RuntimeError('Shader compilation failed: %s' % (info))
            return shader_id
        except:
            glDeleteShader(shader_id)
            raise

    def uniform_location(self, name):
        """ Helper function to get location of an OpenGL uniform variable

        Parameters
        ----------
        name : str
            Name of the variable for which location is to be returned

        Returns
        -------
        value : int
            Integer describing location

        """
        return glGetUniformLocation(self.program_id, name)

    def attribute_location(self, name):
        """ Helper function to get location of an OpenGL attribute variable

        Parameters
        ----------
        name : str
            Name of the variable for which location is to be returned

        Returns
        -------
        value : int
            Integer describing location

        """
        return glGetAttribLocation(self.program_id, name)


class sim1():
	def __init__(self,app):
		self.app = app


	def prepare(self):
		app.scene = self.render
		app.keyboard = flyaroundHandler
		vertex = """
		#version 410
		uniform mat4 modelViewMatrix;
		uniform mat4 projectionMatrix;
		in vec3 vin_position;
		in vec3 vin_color;
		out vec3 vout_color;

		void main(void)
		{
		    vout_color = vin_color;
		    gl_Position = projectionMatrix*modelViewMatrix*vec4(vin_position, 1.0);
		}
		"""


		fragment = """
		#version 410
		in vec3 vout_color;
		out vec4 fout_color;

		void main(void)
		{
		    fout_color = vec4(vout_color, 1.0);
		}
		"""
		glClearColor(0.95, 0.0, 0.95, 0)
		self.program = ShaderProgram(fragment=fragment, vertex=vertex)
		vertex_data = numpy.array([
			-0.75, 0.75, 0.0,
			0.75, -0.75, 0.0,
			-0.75, -0.75, 0.0
		], dtype=numpy.float32)

		color_data = numpy.array([
			1, 0, 0,
			0, 1, 0,
			0, 0, 1
		], dtype=numpy.float32)

		self.vao_id = glGenVertexArrays(1)
		glBindVertexArray(self.vao_id)
		self.vbo_id = glGenBuffers(2)
		glBindBuffer(GL_ARRAY_BUFFER, self.vbo_id[0])
		glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(vertex_data), vertex_data, GL_STATIC_DRAW)
		# Now specify how the shader program will be receiving this data
		# In this case the data from this buffer will be available in the shader as the vin_position vertex attribute
		glVertexAttribPointer(self.program.attribute_location('vin_position'), 3, GL_FLOAT, GL_FALSE, 0, None)

		# Turn on this vertex attribute in the shader
		glEnableVertexAttribArray(0)

		# Now do the same for the other vertex buffer
		glBindBuffer(GL_ARRAY_BUFFER, self.vbo_id[1])
		glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(color_data), color_data, GL_STATIC_DRAW)
		glVertexAttribPointer(self.program.attribute_location('vin_color'), 3, GL_FLOAT, GL_FALSE, 0, None)
		glEnableVertexAttribArray(1)

		# Lets unbind our vbo and vao state
		# We will bind these again in the draw loop
		glBindBuffer(GL_ARRAY_BUFFER, 0)
		glBindVertexArray(0)


	def render(self,world):
		glClear(GL_COLOR_BUFFER_BIT)

		# Specify shader to be used
		glUseProgram(self.program.program_id)



		glUniformMatrix4fv(self.program.uniform_location('modelViewMatrix'), 1, GL_FALSE, world.m44_model_view)
		glUniformMatrix4fv(self.program.uniform_location('projectionMatrix'), 1, GL_FALSE, world.m44_projection)

		# Bind VAO - this will automatically
		# bind all the vbo's saving us a bunch
		# of calls
		glBindVertexArray(self.vao_id)

		# Modern GL makes the draw call really simple
		# All the complexity has been pushed elsewhere
		glDrawArrays(GL_TRIANGLES, 0, 3)

		# Lets unbind the shader and vertex array state
		glUseProgram(0)
		glBindVertexArray(0)

	#	glBindBuffer(GL_ARRAY_BUFFER, self.vertexBuffer)
	def destruct(self,world):
		self.scene.destruct()

	def keyboard(self,app):
		"""Keyboard controlling, uses keyboard.flyaroundHandler
		   to provide basic interaction"""
		flyaroundHandler(app)

if __name__ == "__main__":
	app = application()
	sim = sim1(app)
	sim.prepare()
	app.run()
