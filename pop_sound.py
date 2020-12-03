
'''
Generates a pop with a few random samples followed by a bandpass filter
@ticksamps - number os random samples to use (usually in the range [1,10] - 3 works well)
@len - total number of samples to generate (should be enough to include the ringing of the filter)
@krms - desired rms of the signal after filtering (not used currently)
@f0 - bandpass filter center frequency
@Q - bandpass filter Q value (<1 creates a long ringing tone at f0, >10 is shorter ringining wide-band noise)
fs - sample rate
'''

import numpy as np
#import seaborn as sns
from scipy import signal
import math
#import sys

from mySM import MySoundModel

class MyPop(MySoundModel) :

	def __init__(self, f0=440, Q=10) :
		MySoundModel.__init__(self)
		#create a dictionary of the parameters this synth will use
		self.__addParam__("f0", 100, 2000, f0)
		self.__addParam__("Q", .1, 50, Q)

	'''
		Override of base model method
	'''
	def generate(self, sigLenSecs) :

		# notation for this method
		f0=self.getParam("f0")
		Q =self.getParam("Q")


		# pop specific parameters
		length = round(sigLenSecs*self.sr) # in samples
		ticksamps = 3  # number of noise samples to use before filtering
		krms = 0.6
		tick=2*np.random.rand(ticksamps)-1    #noise samples in [-1,1]
		tick = np.pad(tick, (0, length-ticksamps), 'constant')

	    # Design peak filter
		b, a = signal.iirpeak(f0, Q, self.sr)
		#use it
		tick=signal.lfilter(b, a, tick)

		if False :
			#print("original rms={}".format(math.sqrt(sum([x*x/ticksamps for x in tick]))))
			c=math.sqrt(ticksamps*krms*krms/sum([(x*x) for x in tick]))
			tick = [c*x for x in tick]
			#print("new rms={}".format(math.sqrt(sum([x*x/ticksamps for x in tick]))))
		else :
			maxfsignal=max(abs(tick))
			tick = tick*.9/maxfsignal

		return tick
