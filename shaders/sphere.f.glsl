varying vec2 coord;
//thanks to https://sites.google.com/site/dlampetest/python/vectorized-particle-system-and-geometry-shaders
void main() {
    if (1.0-length(coord)<0.0) {
    	discard;
    }
    gl_FragColor = vec4(1.0, .75, 0.25, -(.7*length( coord )*.7*length( coord ))+.3);
}
