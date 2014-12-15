""" OpenGl gravity simulation n2

    context:
    - optimization of force calculation by
      using newtons third law, the force A-B
      is the same as B-A.

    basic euler approximation of newtons gravity.
    approximation:
    - linear steps with length p_dt

    known issues:
    - singulaties when objects are close
    - no collision check
    - very slow due to big amout of python
      high level invocations

    author keksnicoh@googlemail.com
"""

from scene1 import scene1
from OpenGLContext.arrays import *
import numpy

class scene2(scene1):
	def calculateDv(self):
		objN = len(self.physicalObjects)
		dv = numpy.zeros((objN,3))
		d2_calc = 0
		obj_with_mass = len(filter(lambda obj: obj[1], self.physicalObjects));
		exp_d2_calc = obj_with_mass*(obj_with_mass-1.0)/2.0

		oia = 0
		while oia < objN:
			obja = self.physicalObjects[oia]
			if obja[1] > 0:
				oib = oia+1
				while oib < objN:
					objb = self.physicalObjects[oib]
					if objb[1] > 0:
						rel_ab = [objb[2]-obja[2],objb[3]-obja[3],objb[4]-obja[4]]
						d_2 = rel_ab[0]**2 + rel_ab[1]**2 + rel_ab[2]**2
						d_1 = sqrt(d_2)
						d2_calc += 1
						if d_2 != 0:
							f =  1.0/d_2
							normal_rel_ab = [rel_ab[0]/d_1, rel_ab[1]/d_1, rel_ab[2]/d_1]
							dv[oia][0] +=  f * objb[1] * normal_rel_ab[0] * self.phys_dt
							dv[oia][1] +=  f * objb[1] * normal_rel_ab[1] * self.phys_dt
							dv[oia][2] +=  f * objb[1] * normal_rel_ab[2] * self.phys_dt
							dv[oib][0] += -f * obja[1] * normal_rel_ab[0] * self.phys_dt
							dv[oib][1] += -f * obja[1] * normal_rel_ab[1] * self.phys_dt
							dv[oib][2] += -f * obja[1] * normal_rel_ab[2] * self.phys_dt
					oib+=1
			oia += 1

		if(d2_calc != exp_d2_calc):
			print(
				("SIMWARN calculateDv(): d2_calc=%d "
				+ "differ from exp_d2_calc: %d") %
				(d2_calc,exp_d2_calc));
		return dv
	def convertPhysicsState(self):
		dv = self.calculateDv()
		objN = len(self.physicalObjects)
		oi = 0
		while oi < objN:
			self.physicalObjects[oi][5] += dv[oi][0]
			self.physicalObjects[oi][6] += dv[oi][1]
			self.physicalObjects[oi][7] += dv[oi][2]

			self.physicalObjects[oi][2] += self.physicalObjects[oi][5]*self.phys_dt
			self.physicalObjects[oi][3] += self.physicalObjects[oi][6]*self.phys_dt
			self.physicalObjects[oi][4] += self.physicalObjects[oi][7]*self.phys_dt

			oi += 1

