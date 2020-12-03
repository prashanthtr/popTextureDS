# Generic sound class to store sound synthesizer files
import numpy as np
import seaborn as sns
from scipy import signal
import math
import sys

''' Using a soundmodel and parameters, generic_Synth generates a texture

setParam() list of parameters and their ranges

synthesize() Generate events based on the current parameter values (rate, irregularity)

getParams () To get the list of parameters and their ranges

'''

class generic_synth() :

    def __init__(self, soundModel) :
        self.params = []
        self.makeSingleEvent = soundModel # makes a single event
        self.signal = [] # audio signal with sound events

    def setParam(self, data):
        for p in data:
            print('Name: ' + p['pname'])
            print('Units: ' + p['units'])
            #print("Formula: " + p['formula'])
            self.params.append(p)

    def getParam(self):
        return self.params

    '''
    Generic stochastic event generator with 3 parameters
    Takes 3 parameters and produces sound events as specified by sound model
    p1: rate, p2: irregularity, p3: cf
    '''
    def synthesize(self,parameters, sr, soundDurationSecs=4):
        r_exp = parameters[0]
        irreg_exp = parameters[1]
        cf_exp = parameters[2]

        # mapping to the right ranges
        eps=np.power(2,r_exp)
        irregularity=.1*irreg_exp*np.power(10,irreg_exp)
        sd=irregularity/eps
        cf=440*np.power(2,cf_exp)  #range over one octave from 440 to 880

        linspacesteps=int(eps*soundDurationSecs)
        linspacedur = linspacesteps/eps

        eventtimes=[(x+np.random.normal(scale=sd))%soundDurationSecs for x in np.linspace(0, linspacedur, linspacesteps, endpoint=False)]

        # Central frequency controls the Central frequency of bandpass filter
        return self.elist2signal(eventtimes, soundDurationSecs, sr, cf,  50)

    '''adds one (shorter) array in to another starting at startsamp in the second'''
    def addin(self,a,b,startsamp) :
        b[startsamp:startsamp+len(a)]=[sum(x) for x in zip(b[startsamp:startsamp+len(a)], a)]
        return b

    ''' Returns the signal starting sample number of the generated events. Visualization purposes'''
    def generateEvents(self,myevents, soundDurSecs, numSamples, sr=16000):
        sig=np.zeros(soundDurSecs*sr)
        for nf in myevents :

            #print("nf = {} and index is {}".format(nf, int(round(nf*sr))))
            sig[int(round(nf*sr))%numSamples]=1
        return sig

    ''' Take a list of event times, and return our signal of filtered pops at those times'''
    def elist2signal(self, elist, sigLenSecs, sr, cf, Q) :
        numSamples=sr*sigLenSecs
        sig=np.zeros(sigLenSecs*sr)
        for nf in elist :
            startsamp=int(round(nf*sr))%numSamples
            # create some deviation in center frequency
            cfsd = 1
            perturbedCf = cf*np.power(2,np.random.normal(scale=cfsd)/12)
            #print("perturbed CF is {}".format(perturbedCf))
            #   pop(ticksamps, len, krms, f0, Q, fs)
            sig=self.addin(self.makeSingleEvent(perturbedCf,Q, sr, 1000), sig,startsamp)
        self.sig = sig
        return sig

    ''' Returns a chunked wav files from generated signal '''
    def selectVariation(self, sig, fname, outDir, sr, varNum, varDurationSecs):

        variationSamples=math.floor(sr*varDurationSecs)
        print(len(self.sig[varNum*variationSamples:(varNum+1)*variationSamples]))
        return self.sig[varNum*variationSamples:(varNum+1)*variationSamples]

    def generateRandom(eventsPerSecond, sd, soundDurSecs, numSamples, sr=16000):
        return [(x+np.random.normal(scale=sd))%soundDurSecs for x in np.linspace(0, soundDurSecs, eventsPerSecond*soundDurSecs, endpoint=False)]
