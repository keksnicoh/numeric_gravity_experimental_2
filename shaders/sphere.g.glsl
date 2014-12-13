#version 120
#extension GL_EXT_geometry_shader4 : enable
const float radius = .1;
varying out vec2 coord;

void main()
{
  gl_FrontColor = gl_FrontColorIn[0];
  coord = vec2(-1,-1);
  gl_Position = (gl_PositionIn[0] + gl_ProjectionMatrix * vec4(-radius,-radius,0,0) );
  EmitVertex();
  coord = vec2(-1,1);
  gl_Position = (gl_PositionIn[0] + gl_ProjectionMatrix * vec4(-radius,radius, 0,0) );
  EmitVertex();
  coord = vec2(1,-1);
  gl_Position = (gl_PositionIn[0] + gl_ProjectionMatrix * vec4( radius,-radius, 0,0) );
  EmitVertex();
  coord = vec2(1,1);
  gl_Position = (gl_PositionIn[0] + gl_ProjectionMatrix * vec4( radius,radius, 0,0) );
  EmitVertex();
  EndPrimitive();
}
