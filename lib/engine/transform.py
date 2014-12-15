from OpenGL import GL
import cyglfw3 as glfw


shader_vertex_source = """
	#version 410
    in float inValue;
    out float outValue;

    void main() {
        outValue = sqrt(inValue);
    }
"""





def init_gl_core_profile():
	glfw.WindowHint(glfw.CONTEXT_VERSION_MAJOR, 3)
	glfw.WindowHint(glfw.CONTEXT_VERSION_MINOR, 2)
	glfw.WindowHint(glfw.OPENGL_FORWARD_COMPAT, 1)
	glfw.WindowHint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)



def load_shader():
	shader_program = GL.glCreateProgram()
	shader_vertex = GL.glCreateShader(GL.GL_VERTEX_SHADER)
	GL.glShaderSource(shader_vertex, shader_vertex_source)
	GL.glCompileShader(shader_vertex)
	shader_vertex_log = GL.glGetShaderInfoLog(shader_vertex)
	if shader_vertex_log:
		raise RuntimeError("vertex_shader: " + shader_vertex_log)
	GL.glAttachShader(shader_program, shader_vertex)
	program_log = GL.glGetProgramInfoLog(shader_program)
	glLinkProgram(shader_program)
	if program_log:
		raise RuntimeError("shader_program: " + program_log)

	return shader_program

def init_glfw_window(width,height,title):

	window = glfw.CreateWindow(width, height, title)
	if not window:
		raise RuntimeError('glfw.CreateWindow() error')

	return window

def glfw_init():
	if not glfw.Init():
		raise RuntimeError('glfw.Init() error')

glfw_init()
init_gl_core_profile()
glfw_window = init_glfw_window(640,400, "test")

shader_program = load_shader()

print GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION)
glfw.MakeContextCurrent(glfw_window)

print('GL:',GL.glGetString(GL.GL_VERSION))
print('GLFW3:',glfw.GetVersionString())


feedback = ["","","",""]
GL.glTransformFeedbackVaryings(shader_program, 1, feedback , GL_INTERLEAVED_ATTRIBS);


for iteration in range(100):
    if glfw.WindowShouldClose(glfw_window):
        break
    GL.glClearColor(0.2, 0.2, 0.2, 1.0)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    glfw.SwapBuffers(glfw_window)
    glfw.PollEvents()

glfw.DestroyWindow(glfw_window)
glfw.Terminate()
