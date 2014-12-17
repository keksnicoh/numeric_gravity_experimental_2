from OpenGL.GL import *
from engine.gl.shader import shader
import numpy

class particle_gravity():
	def __init__(self):
		self.initParticles()

	def pushParticleToInitState(self, pos, vel, mass, radius=0.1, has_force=False, color=[1,1,1]):
		self.particles_init_state.append([
			pos[0],pos[1],pos[2],
			vel[0],vel[1],vel[2],
			color[0],color[1],color[2],
			has_force,mass,radius
		])
	def initParticles(self):
		self.particles_init_state = []
		self.particles = None
		self._p_count  = 0
		self._p_pos    = None
		self._p_vel    = None
		self._p_mass   = None
		self._p_color  = None
		self._p_eps    = 0.00000001
		self._p_dt     = 0.0001

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

		self.vao_id = glGenVertexArrays(1)
		self.vbo_id = glGenBuffers(3)

		glBindVertexArray(self.vao_id)
		glBindBuffer(GL_ARRAY_BUFFER, self.vbo_id[0])
		glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(self._p_pos), self._p_pos, GL_STATIC_DRAW)
		glVertexAttribPointer(self.shader.attributeLocation('vin_position'), 3, GL_FLOAT, GL_FALSE, 0, None)
		glEnableVertexAttribArray(0)

		glBindBuffer(GL_ARRAY_BUFFER, self.vbo_id[1])
		glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(self._p_color), self._p_color, GL_STATIC_DRAW)
		glVertexAttribPointer(self.shader.attributeLocation('vin_color'), 3, GL_FLOAT, GL_FALSE, 0, None)
		glEnableVertexAttribArray(1)

		glBindBuffer(GL_ARRAY_BUFFER, self.vbo_id[2])
		glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(self._p_radius), self._p_radius, GL_STATIC_DRAW)
		glVertexAttribPointer(self.shader.attributeLocation('in_radius'), 1, GL_FLOAT, GL_FALSE, 0, None)
		glEnableVertexAttribArray(2)

		glBindBuffer(GL_ARRAY_BUFFER, 0)
		glBindVertexArray(0)

	def physics_move(self):
		"""calculates the motion of objects"""
		for ww_i in self._p_ww_indicies:
			d_pos        = self._p_pos[ww_i]-self._p_pos
			gm_by_r3     = self._p_mass[ww_i] / ((d_pos ** 2).sum(axis=1) + self._p_eps ** 2)**1.5
			self._p_vel += (d_pos.T * gm_by_r3).T * self._p_dt
		self._p_pos += self._p_vel * self._p_dt

	def initShader(self):
		self.shader = shader()
		self.shader.attachShader(GL_VERTEX_SHADER, VERTEX_SHADER)
		self.shader.attachShader(GL_FRAGMENT_SHADER, FRAGMENT_SHADER)
		self.shader.attachShader(GL_GEOMETRY_SHADER, GEOMETRY_SHADER)
		self.shader.linkProgram()

	def render(self,world):
		self.physics_move()
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
		pass

	def destruct(self):
		pass


VERTEX_SHADER = """
#version 410
uniform mat4 modelViewMatrix;
uniform mat4 projectionMatrix;
in vec3 vin_position;
in vec3 vin_color;
in float in_radius;
out vec3 vout_color;
out vec3 v_color;
out float v_radius;
void main() {
	v_color = vin_color;
	v_radius = in_radius;
	gl_Position = projectionMatrix*modelViewMatrix*vec4(vin_position, 1.0);
}
"""
FRAGMENT_SHADER = """
#version 410
in vec3 vout_color;
out vec4 fout_color;
in vec2 coord;
void main() {
	//fout_color = vec4(1.0,0.0,0.0,0.0);
    if (1.0-length(coord)<0.0) {
    	discard;
    }
    //fout_color = vec4(vout_color, 1.0);
    fout_color = vec4(vout_color, 0.2-(.7*length( coord )*.7*length( coord ))+.3);
}
"""
GEOMETRY_SHADER = """
#version 410
layout (points) in;
layout (triangle_strip) out;
layout (max_vertices = 4) out;
uniform mat4 modelMatrix;
const float radius = .1;
out vec2 coord;
in float v_radius[1];

in vec3 v_color[1];
out vec3 vout_color;
void main(void)
{
  coord = vec2(-1,-1);
  vout_color = v_color[0];
  gl_Position = gl_in[0].gl_Position + modelMatrix*vec4(-v_radius[0],-v_radius[0],0,0) ;
  EmitVertex();
  coord = vec2(-1,1);
    vout_color = v_color[0];

  gl_Position = gl_in[0].gl_Position + modelMatrix*vec4(-v_radius[0],v_radius[0], 0,0) ;
  EmitVertex();
  coord = vec2(1,-1);
    vout_color = v_color[0];

  gl_Position = gl_in[0].gl_Position + modelMatrix*vec4( v_radius[0],-v_radius[0], 0,0) ;
  EmitVertex();
  coord = vec2(1,1);
    vout_color = v_color[0];
  gl_Position = gl_in[0].gl_Position + modelMatrix*vec4( v_radius[0],v_radius[0], 0,0) ;
  EmitVertex();
  EndPrimitive();
}
"""
