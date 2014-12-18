"""experimental gravity implementation based on
   opencl

   @author Nicolas 'keksnicoh' Heimann <keksnicoh@gmail.com>"""

from OpenGL.GL import *
from engine.gl.shader import shader
import pyopencl as cl
import pyopencl
from pyopencl.tools import get_gl_sharing_context_properties
import numpy
mf = cl.mem_flags

class particle_gravity_cl():
	def __init__(self):
		self.particles_init_state = []
		self.particles_init_state_ww = []
		self.particles_init_state_has_ww = []
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
			mass,radius
		])

		self.particles_init_state_has_ww.append(has_force)
		if has_force:
			self.particles_init_state_ww.append(len(self.particles_init_state)-1)

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
		self._p_count  = len(init)
		self._p_pos    = numpy.zeros((self._p_count, 4), dtype=numpy.float32)
		self._p_vel    = numpy.zeros((self._p_count, 4), dtype=numpy.float32)
		self._p_mass   = init[:, 9]

		self._p_pos[:,[0,1,2]] = init[:, [0,1,2]]
		self._p_pos[:,3]       = self._p_mass

		self._p_vel[:,[0,1,2]] = init[:, [3,4,5]]
		self._p_color          = init[:, [6,7,8]]
		self._p_radius         = init[:, 10]
		self._p_ww             = numpy.array(self.particles_init_state_ww, dtype=numpy.int32)
		self._p_ww_len         = len(self._p_ww)
		self._p_has_ww         = numpy.array(self.particles_init_state_has_ww, dtype=numpy.int32)

		print self._p_has_ww
		# prerpare vertex buffer object and vertex
		# array object.

		self.prepareGlBuffer()
		self.prepareClBuffer()

		self.render = self._render
		self.ready = True

	def prepareGlBuffer(self):
		self.vao_id = glGenVertexArrays(1)
		self.vbo_id = glGenBuffers(4)

		glBindVertexArray(self.vao_id)
		glBindBuffer(GL_ARRAY_BUFFER, self.vbo_id[0])
		glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(self._p_pos), self._p_pos, GL_DYNAMIC_DRAW)
		glVertexAttribPointer(self.shader.attributeLocation('buffer_in_position'),4, GL_FLOAT, GL_FALSE, 0, None)
		glEnableVertexAttribArray(0)

		glBindBuffer(GL_ARRAY_BUFFER, self.vbo_id[1])
		glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(self._p_vel), self._p_vel, GL_STATIC_DRAW)
		glVertexAttribPointer(self.shader.attributeLocation('buffer_in_vel'), 3, GL_FLOAT, GL_FALSE, 0, None)
		glEnableVertexAttribArray(1)

		glBindBuffer(GL_ARRAY_BUFFER, self.vbo_id[2])
		glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(self._p_color), self._p_color, GL_STATIC_DRAW)
		glVertexAttribPointer(self.shader.attributeLocation('buffer_in_color'), 3, GL_FLOAT, GL_FALSE, 0, None)
		glEnableVertexAttribArray(2)

		glBindBuffer(GL_ARRAY_BUFFER, self.vbo_id[3])
		glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(self._p_radius), self._p_radius, GL_STATIC_DRAW)
		glVertexAttribPointer(self.shader.attributeLocation('buffer_in_radius'), 1, GL_FLOAT, GL_FALSE, 0, None)
		glEnableVertexAttribArray(3)

		glBindBuffer(GL_ARRAY_BUFFER, 0)
		glBindVertexArray(0)

	def prepareClBuffer(self):
		platform = cl.get_platforms()
		self.ctx = cl.Context(properties=get_gl_sharing_context_properties(),devices=[])
		self.queue = cl.CommandQueue(self.ctx)
		self._cl_buf_pos  = cl.GLBuffer(self.ctx, mf.READ_WRITE, int(self.vbo_id[0]))
		self._cl_buf_vel  = cl.GLBuffer(self.ctx, mf.READ_WRITE, int(self.vbo_id[1]))
		self._cl_p_ww     = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self._p_ww)
		self._cl_p_has_ww = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self._p_ww)
		self._cl_p_ww_len = numpy.int32(len(self._p_ww))
		self.prog = cl.Program(self.ctx, CL_KERNEL).build()

	def physics(self):
		kernelargs = (self._cl_buf_pos,self._cl_buf_vel,self._cl_p_has_ww, self._cl_p_ww,self._cl_p_ww_len)
		self.prog.physics(self.queue, (self._p_count,), None, *kernelargs)
		self.queue.finish()
		cl.enqueue_release_gl_objects(self.queue, [self._cl_buf_pos,self._cl_buf_vel])

	def _renderNotReady(self,world):
		raise RuntimeError('particle_gravity not ready. use particle_gravity.prepare() before rendering')

	def render(self,world):
		"""before init this method is empty. after init this
		   method will be replaced by _renderNotReady to avoid
		   rendering when vbo,vba is not configured."""
		pass

	def _render(self,world):
		self.shader.useProgram()
		self.physics()

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

CL_KERNEL = """
__kernel void physics(__global float4* a, __global float4* v,__global int* has_ww, __global int* ww_ids, const unsigned int ww_length)
{
	unsigned int id = get_global_id(0);
	unsigned int n = get_global_size(0);
	float4 current = a[id];
	float3 rel;
	float dist = 0;
	float p = 5000;
	float p_eps = 0.000001f;
	float force;
	float acc;
	int ww;
	float dt = 0.0001f;

	for(unsigned int i = 0;i < ww_length;i++) {
		ww = ww_ids[i];
		rel.x = a[ww].x-a[id].x;
		rel.y = a[ww].y-a[id].y;
		rel.z = a[ww].z-a[id].z;

		dist = pow(rel.x,2)+pow(rel.y,2)+pow(rel.z,2)+p_eps;
		rel.x /= half_sqrt(dist);
		rel.y /= half_sqrt(dist);
		rel.z /= half_sqrt(dist);

		acc = 1/dist;
		force = rel.x * acc;
		v[id].x += a[ww].w * force*dt;
		force = rel.y * acc;
		v[id].y += a[ww].w * force*dt;
		force = rel.z * acc;
		v[id].z += a[ww].w * force*dt;
	}


	a[id].x += v[id].x*0.0001f;
	a[id].y += v[id].y*0.0001f;
	a[id].z += v[id].z*0.0001f;
}"""
VERTEX_SHADER = """
#version 410
uniform mat4 modelViewMatrix;
uniform mat4 projectionMatrix;
in vec3 buffer_in_position;
in vec3 buffer_in_vel;
in vec3 buffer_in_color;
in float buffer_in_radius;

out vec3 vert_point_color;
out float vert_radius;
out vec3 vert_vel;
void main() {
	vert_point_color = buffer_in_color;
	vert_radius = buffer_in_radius;
	vert_vel = buffer_in_vel;
	gl_Position = projectionMatrix*modelViewMatrix*vec4(buffer_in_position, 1.0);
}
"""
FRAGMENT_SHADER = """
#version 410

in vec3 vert_color;
in vec2 tex_coord;
in vec3 frag_vel;

out vec4 pixel_color;
float fac;
float fac2;
void main() {
    if (1.0-length(tex_coord)<0.0) {
    	discard;
    }
    //frag_vel;
    //
    vert_color;
    fac = 1-pow(2.8,-length(frag_vel)/1500-0.1);
    fac2 = pow(2.8,-length(frag_vel)/1000);
    pixel_color = vec4(fac2,fac,fac, 0.2-(.7*length( tex_coord )*.7*length( tex_coord ))+.3);
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
in vec3 vert_vel[1];

out vec3 vert_color;
out vec2 tex_coord;
out vec3 frag_vel;

void main(void)
{
	tex_coord = vec2(-1,-1);
	vert_color = vert_point_color[0];
	frag_vel = vert_vel[0];
	gl_Position = gl_in[0].gl_Position + modelMatrix*vec4(-vert_radius[0],-vert_radius[0],0,0) ;
	EmitVertex();

	frag_vel = vert_vel[0];
	tex_coord = vec2(-1,1);
	vert_color = vert_point_color[0];
	gl_Position = gl_in[0].gl_Position + modelMatrix*vec4(-vert_radius[0],vert_radius[0], 0,0) ;
	EmitVertex();

	frag_vel = vert_vel[0];
	tex_coord = vec2(1,-1);
	vert_color = vert_point_color[0];
	gl_Position = gl_in[0].gl_Position + modelMatrix*vec4( vert_radius[0],-vert_radius[0], 0,0) ;
	EmitVertex();

	frag_vel = vert_vel[0];
	tex_coord = vec2(1,1);
	vert_color = vert_point_color[0];
	gl_Position = gl_in[0].gl_Position + modelMatrix*vec4( vert_radius[0],vert_radius[0], 0,0) ;
	EmitVertex();
	EndPrimitive();
}
"""
