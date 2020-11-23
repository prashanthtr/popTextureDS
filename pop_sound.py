
# generate pop texture
import numpy as np
from scipy import signal
import math

'''
Generates a pop with a few random samples followed by a bandpass filter
@ticksamps - number os random samples to use (usually in the range [1,10] - 3 works well)
@len - total number of samples to generate (should be enough to include the ringing of the filter)
@krms - desired rms of the signal after filtering (not used currently)
@f0 - bandpass filter center frequency
@Q - bandpass filter Q value (<1 creates a long ringing tone at f0, >10 is shorter ringining wide-band noise)
fs - sample rate
'''
def soundModel(f0, Q, fs, len=1000) :

	# pop specific parameters
	ticksamps = 3
	krms = 0.6
	tick=2*np.random.rand(ticksamps)-1
	tick = np.pad(tick, (0, len-ticksamps), 'constant')
    
    # Design peak filter
	b, a = signal.iirpeak(f0, Q, fs)
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