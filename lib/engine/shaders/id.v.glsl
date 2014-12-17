#version 410
layout (std140) uniform Matrices {
    mat4 projModelViewMatrix;
};
in vec3 position;
void main() {
	gl_Position = projModelViewMatrix * vec4(position, 1.0);

}
