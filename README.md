numeric_gravity_experimental_2
==============================

python based OpenGL 4.1 simulations using PyOpenGL, cyglfw3, numpy, GLSL 410

experimental implementation of some simulations.
this repo is for getting experience with python,
opengl,shaders,numpy and so on..

at current stage only simple euler approximation
is used. 

this library aims to use all the awesome features
of OpenGL4.1 so it currently loads OpenGL4.1 core
profile by using glfw. There is no use of GLU,GLUT 
and all deprecated old-fashion-style opengl function.
Tested on Mac OS X Yosimiti. If somethings wrong
with OpenGL4.1 core profile the application will segfault.

currently, to keep it simple, there is no use of consants or SI-units.
for the future:
- integrate units e.g. SI-units and force characterisation constants
- more advanced shader techniques
- more advanced approximations
- mile stone: implementation of position based algorithms
- physics like springs, flying objects under constant gravitational field, ...

fuck yea gravity...

somerthing similar to saturn (1million particles)

![saturn like](/img/saturn like object.png)

galaxy like 

![galaxy like](/img/galaxy like.png)

maybe something like black holes

![bh2](/img/black hole like2.png)
![bh1](/img/black hole like.png)

random

![random1](/img/random1.png)
![random2](/img/random2.png)

first experiments

![trinity1](/img/first experiments.png)
![trinity2](/img/first experiments2.png)
