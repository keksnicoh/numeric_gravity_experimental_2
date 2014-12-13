varying vec2 coord;
void main(){
    vec4 color = gl_Color;
    color.a = 1.0-length( coord );
    if (color.a<0.0) discard;

    // A VERY FAKE "lighting" model
    float d = dot( normalize(vec3(coord,1.0)), vec3( 0.19, 0.19, 0.96225 ) );
    // end "lighting"
//new color = 0.5*(0,1,0) + (1-0.5)*(1,0.5,0.5); // (the red was already blended with the white background)
//new color = (1, 0.75, 0.25) = the same orange
    gl_FragColor = vec4(1.0, .75, 0.25, -(.7*length( coord )*.7*length( coord ))+.3);
}
