"""gravity simulation based on singular mass points.
   vertex shader will pass the transformed point position
   to geometry shader. geometry shader will spawn a screen
   parallel quad around the vertex. the fragment shader
   will render it so it looks like a ball.

   this simulation allows to configure which masses should
   carrier force to other particles. if true for each
   particle this will be a normal simulation with n!
   interactions.

   to simulate heavy amout of particles, it is a good
   approximation to set force carriing particles a
   very big mass compared to particles without force.
   its like a perfect-gas or something, where there
   is a cloud of maybe 500k particles around a black
   hole.

   known issues:
   - each frame requires to swap the whole position
     memory to the grafic-card buffer. this should
     be avoided by using transformation feedback.
   - singulatities when objects are very close

   @author Nicolas 'keksnicoh' Heimann <keksnicoh@gmail.com>"""

from OpenGL.GL import *
from engine.gl.shader import shader
import numpy

class particle_gravity():
	def __init__(self):
		self.particles_init_state = []
		self.initPhysics()

	def initShader(self):
		self.shader = shader()
		self.shader.attachShader(GL_VERTEX_SHADER, VERTEX_SHADER)
		self.shader.attachShader(GL_FRAGMENT_SHADER, FRAGMENT_SHADER)
		self.shader.attachShader(GL_GEOMETRY_SHADER, GEOMETRY_SHADER)
		self.shader.linkProgram()

	def pushParticleToInitState(self, pos, vel, mass, radius=0.1, has_force=False, color=[1,1,1]):
		self.particles_init_state.append([
			pos[0],pos[1],pos[2],
			vel[0],vel[1],vel[2],
			color[0],color[1],color[2],
			has_force,mass,radius
		])

	def initPhysics(self):
		self._p_count  = 0          # particle count
		self._p_pos    = None       # paticle positions
		self._p_vel    = None       # particle velocities
		self._p_mass   = None       # particle masses
		self._p_color  = None       # particle colors
		self._p_eps    = 0.00000001 # factor to avoid infinities in physics()
		self._p_dt     = 0.0001     # length of time in physics()

		self.vao_id = None
		self.vbo_id = None
		self.read   = False
		self.render = self._renderNotReady

	def prepare(self):
		self.initShader()

		init = numpy.array(self.particles_init_state, dtype=numpy.float32)
		self._p_pos    = init[:, [0,1,2]]
		self._p_vel    = init[:, [3,4,5]]
		self._p_color  = init[:, [6,7,8]]
		self._p_mass   = init[:, 10]
		self._p_radius = init[:, 11]
		self._p_count  = len(self._p_pos)

		indices = []
		for (index,has_force) in enumerate(init[:,9]):
			if has_force:
				indices.append(index)
		self._p_ww_indicies = numpy.array(indices)

		# prerpare vertex buffer object and vertex
		# array object.
		self.vao_id = glGenVertexArrays(1)
		self.vbo_id = glGenBuffers(3)

		glBindVertexArray(self.vao_id)
		glBindBuffer(GL_ARRAY_BUFFER, self.vbo_id[0])
		glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(self._p_pos), self._p_pos, GL_STATIC_DRAW)
		glVertexAttribPointer(self.shader.attributeLocation('buffer_in_position'), 3, GL_FLOAT, GL_FALSE, 0, None)
		glEnableVertexAttribArray(0)

		glBindBuffer(GL_ARRAY_BUFFER, self.vbo_id[1])
		glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(self._p_color), self._p_color, GL_STATIC_DRAW)
		glVertexAttribPointer(self.shader.attributeLocation('buffer_in_color'), 3, GL_FLOAT, GL_FALSE, 0, None)
		glEnableVertexAttribArray(1)

		glBindBuffer(GL_ARRAY_BUFFER, self.vbo_id[2])
		glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(self._p_radius), self._p_radius, GL_STATIC_DRAW)
		glVertexAttribPointer(self.shader.attributeLocation('buffer_in_radius'), 1, GL_FLOAT, GL_FALSE, 0, None)
		glEnableVertexAttribArray(2)

		glBindBuffer(GL_ARRAY_BUFFER, 0)
		glBindVertexArray(0)

		# activate rendering
		self.render = self._render
		self.ready = True

	def physics(self):
		"""calculates the motion of objects"""
		for ww_i in self._p_ww_indicies:
			d_pos        = self._p_pos[ww_i]-self._p_pos
			gm_by_r3     = self._p_mass[ww_i] / ((d_pos ** 2).sum(axis=1) + self._p_eps ** 2)**1.5
			self._p_vel += (d_pos.T * gm_by_r3).T * self._p_dt
		self._p_pos += self._p_vel * self._p_dt

	def _renderNotReady(self,world):
		raise RuntimeError('particle_gravity not ready. use particle_gravity.prepare() before rendering')

	def render(self,world):
		"""before init this method is empty. after init this
		   method will be replaced by _renderNotReady to avoid
		   rendering when vbo,vba is not configured."""
		pass

	def _render(self,world):
		self.physics()
		glBindBuffer(GL_ARRAY_BUFFER, self.vbo_id[0])
		glBufferSubData(GL_ARRAY_BUFFER, 0, ArrayDatatype.arrayByteCount(self._p_pos), self._p_pos) ;
		glBindBuffer(GL_ARRAY_BUFFER, 0)

		self.shader.useProgram()
		glEnable(GL_BLEND);
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

		glUniformMatrix4fv(self.shader.uniformLocation('modelViewMatrix'), 1, GL_FALSE, world.m44_model_view)
		glUniformMatrix4fv(self.shader.uniformLocation('projectionMatrix'), 1, GL_FALSE, world.m44_projection)
		glUniformMatrix4fv(self.shader.uniformLocation('modelMatrix'), 1, GL_FALSE, world.m44_camera_translation)

		glBindVertexArray(self.vao_id)
		glDrawArrays(0,0,self._p_count)
		glUseProgram(0)
		glBindVertexArray(0)

	def destruct(self):
		if type(self.vbo_id) == 'numpy.ndarray':
			glDeleteBuffers(len(self.vbo_id),self.vbo_id)

		self.initPhysics()
		glDeleteProgram(self.shader.program_id)
		self.shader = None

VERTEX_SHADER = """
#version 410
uniform mat4 modelViewMatrix;
uniform mat4 projectionMatrix;
in vec3 buffer_in_position;
in vec3 buffer_in_color;
in float buffer_in_radius;

out vec3 vert_point_color;
out float vert_radius;

void main() {
	vert_point_color = buffer_in_color;
	vert_radius = buffer_in_radius;
	gl_Position = projectionMatrix*modelViewMatrix*vec4(buffer_in_position, 1.0);
}
"""
FRAGMENT_SHADER = """
#version 410

in vec3 vert_color;
in vec2 tex_coord;

out vec4 pixel_color;
void main() {
    if (1.0-length(tex_coord)<0.0) {
    	discard;
    }
    pixel_color = vec4(vert_color, 0.2-(.7*length( tex_coord )*.7*length( tex_coord ))+.3);
}
"""
GEOMETRY_SHADER = """
#version 410
layout (points) in;
layout (triangle_strip) out;
layout (max_vertices = 4) out;

uniform mat4 modelMatrix;

in float vert_radius[1];
in vec3 vert_point_color[1];

out vec3 vert_color;
out vec2 tex_coord;
void main(void)
{
	tex_coord = vec2(-1,-1);
	vert_color = vert_point_color[0];
	gl_Position = gl_in[0].gl_Position + modelMatrix*vec4(-vert_radius[0],-vert_radius[0],0,0) ;
	EmitVertex();
	tex_coord = vec2(-1,1);
	vert_color = vert_point_color[0];

	gl_Position = gl_in[0].gl_Position + modelMatrix*vec4(-vert_radius[0],vert_radius[0], 0,0) ;
	EmitVertex();
	tex_coord = vec2(1,-1);
	vert_color = vert_point_color[0];

	gl_Position = gl_in[0].gl_Position + modelMatrix*vec4( vert_radius[0],-vert_radius[0], 0,0) ;
	EmitVertex();
	tex_coord = vec2(1,1);
	vert_color = vert_point_color[0];
	gl_Position = gl_in[0].gl_Position + modelMatrix*vec4( vert_radius[0],vert_radius[0], 0,0) ;
	EmitVertex();
	EndPrimitive();
}
"""
