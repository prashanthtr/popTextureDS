x
# dependencies for file reading
import json
import sys
import itertools
import numpy as np
import os
import soundfile as sf

import librosa # conda install -c conda-forge librosa

from pop_sound import MyPop
from parammanager import paramManager
from generic_sound import generic_synth
from myPopPatternSynth import MyPopPatternSynth
from filewrite import sound2File

#from Tf_record import tfrecordManager

'''

This code will generate a dataset of textures consiting of pops. A 'pop' is a burst of noise filtered by a bandpass filter.

The files are generated using 3 different parameters that are sampled over a range of values. The three parameters affect:
    rate (average events per second),
    irregularity in temporal distribution (using a gaussian distribution around each evenly-spaced time value), and
    the center frequency of bp filter

The parameter values are each sampled liniearly on an exponential scale:

rate = 2^r_exp  (so r_exp in [0,4] means the rate ranges from 2 to 16)
irregularity = .04*10^irreg_exp; sd = irregularity/events per second  (so irreg_exp in [0,1] means irregularity ranges from completely regular, to Poisson process)
cf = 440*2^cf_exp  (so cf_exp in [0,1] means cf ranges from 440 to 880, one octave)

For each parameter setting, first a "long" signal (of lentgth longDurationSecs) is generated, and then
it is sliced into segments (called variations) of a length desired for training.

Example: If each parameter is sampled at 5 values, the long signal is 10 seconds and variationLength is 2 seconds,
then The the total amount of audio generated is 5*5*5*10= 1250 seconds of sound (about 25 hours; ~3Gb at 16K sr).
If each variation is 2 seconds, then there will be 10/2=5 variations for each parameter setting, and
5*5*5*5 = 625 files
'''

paramArr = []
data = []

''' Initialize generic synthesizer that uses the sound model '''
gs = generic_synth(soundModel)


barsynth=MyPopPatternSynth()

with open(sys.argv[1]) as json_file:
	data = json.load(json_file)
	print("Reading parameters for generating ", data['soundname'], " texture.. ")
	for p in data['params']:
		#	    print('Name: ' + p['pname'])
		#	    print('Units: ' + p['units'])
		#	    print("Formula: " + p['formula'])
	    p['formula'] = eval("lambda *args: " + p['formula'])
	    paramArr.append(p)
	gs.setParam(data['params'])

getParams = gs.getParam()
print(getParams)

cartParam = []

for p in paramArr:
	cartParam.append(np.linspace(p["minval"], p["maxval"], p["nvals"], endpoint=True))

# read synth file
#popSound = eval(data['soundname'])

sr = data['samplerate']

# if directory exists, then ok, or else create
#filepath = os.path.dirname(os.path.realpath(data['soundname']))
#data['soundname']

wavHandle = sound2File(data["outPath"], ".wav") # initializes out directory
paramHandle = sound2File(data["outPath"], ".params") # initializes out directory

print("Enumerating parameter combinations..")

'''
	for every combination of cartesian parameter
	for every variation
		Create variation wav files
		Create variation parameter files
'''

enumParam = list(itertools.product(*cartParam))

#print("Combination of parameters")

for enumP in enumParam: # caretesian product of lists

        #set parameters

        barsynth.setParam("rate_exp", enumP[0]) # will make 2^1 events per second
        barsynth.setParam("irreg_exp", enumP[1])
        barsynth.setParam("cf", enumP[2])
        barsynth.setParam("Q", 40)

        barsig=barsynth.generate(data["soundDuration"])

	varDurationSecs=data["soundDuration"]/data["numVariations"]  #No need to floor this?
	#sig = gs.synthesize(enumP, sr, data["soundDuration"])

	for v in range(data['numVariations']):

                '''Write wav'''
                wavHandle.__makeName__(data['soundname'], paramArr, enumP, v)
		chunkedAudio = SI.selectVariation(sig, sr, v, varDurationSecs)
                wavHandle.__writeFile__(chunkedAudio, sr)

                '''Write param'''
                paramHandle.__makeName__(data['soundname'], paramArr, enumP, v)

		pm=paramManager.paramManager(paramHandle.__getFile__(), paramHandle.__getOutpath__())
		pm.initParamFiles(overwrite=True)
		for pnum in range(len(paramArr)):
			pm.addParam(vFilesParam[v], paramArr[pnum]['pname'], [0,data['soundDuration']], [enumP[pnum], enumP[pnum]], units=paramArr[pnum]['units'], nvals=paramArr[pnum]['nvals'], minval=paramArr[pnum]['minval'], maxval=paramArr[pnum]['maxval'])

                '''write TF record'''

		#tfm=tfrecordManager.tfrecordManager(vFilesParam[v], outPath)
		#data,sr = librosa.core.load(outPath + fname + '--v-'+'{:03}'.format(v)+'.wav',sr=16000)
		#print(len(data))
		#tfm.addFeature(vFilesParam[v], 'audio', [0,len(data)], data, units='samples', nvals=len(data), minval=0, maxval=0)
		#for pnum in range(len(paramArr)):
		#	print(pnum)
		#	tfm.addFeature(vFilesParam[v], paramArr[pnum]['pname'], [0,data['soundDuration']], [enumP[pnum], enumP[pnum]], units=paramArr[pnum]['units'], nvals=paramArr[pnum]['nvals'], minval=paramArr[pnum]['minval'], maxval=paramArr[pnum]['maxval'])
		#tfm.writeRecordstoFile()
