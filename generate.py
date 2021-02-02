# dependencies for file reading
import json
import sys
import itertools
import numpy as np
import os
import soundfile as sf

import librosa # conda install -c conda-forge librosa

from parammanager import paramManager
from sonyganformat import sonyGanJson

from genericsynth import synthInterface as SI
from myPopPatternSynth import MyPopPatternSynth
from filewrite import fileHandler

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


with open(sys.argv[1]) as json_file:
	data = json.load(json_file)
	print("Reading parameters for generating ", data['soundname'], " texture.. ")
	for p in data['params']:
                p['formula'] = eval("lambda *args: " + p['formula'])
                paramArr.append(p)

sr = data['samplerate']
soundName = data["soundname"]
outPath = data["outPath"]
recordFormat = data["recordFormat"]
paramRange = data["paramRange"]
soundDuration = data["soundDuration"]
numVariations = data["numVariations"]

'''Initializes file through a filemanager'''
fileHandle = fileHandler()

print("Enumerating parameter combinations..")

'''
	for every combination of cartesian parameter
    for every variation
		Create variation wav files
		Create variation parameter files
'''

'''2 arrays for normalised and naturalised ranges'''
userRange = []
synthRange = []

if paramRange == "Norm":
    for p in paramArr:
        userRange.append(np.linspace(p["minval"], p["maxval"], p["nvals"], endpoint=True))    
    for p in paramArr:
        synthRange.append(np.linspace(p["minval"], p["maxval"], p["nvals"], endpoint=True))
else:
    for p in paramArr:
        userRange.append(np.linspace(p["minval"], p["maxval"], p["nvals"], endpoint=True))    
    for p in paramArr:
        synthRange.append(np.linspace(p["minval"], p["maxval"], p["nvals"], endpoint=True))

userParam = list(itertools.product(*userRange))
synthParam = list(itertools.product(*synthRange))

sg = sonyGanJson.SonyGanJson(data['soundname'],1, 16000, "POPTextureDS")

for index in range(len(userParam)): # caretesian product of lists

        userP = userParam[index]
        synthP = synthParam[index]

        #set parameters
        barsynth=MyPopPatternSynth()

        if paramRange == "Norm":
            barsynth.setParamNorm("rate_exp", synthP[0]) # will make 2^1 events per second
            barsynth.setParamNorm("irreg_exp", synthP[1])
            barsynth.setParamNorm("cf_exp", synthP[2])
        else:
            barsynth.setParam("rate_exp", synthP[0]) # will make 2^1 events per second
            barsynth.setParam("irreg_exp", synthP[1])
            barsynth.setParam("cf_exp", synthP[2])

        barsig=barsynth.generate(soundDuration)
        varDurationSecs=soundDuration/numVariations  #No need to floor this?

        for v in range(numVariations):

                '''Write wav'''
                wavName = fileHandle.makeName(soundName, paramArr, userP, v)
                wavPath = fileHandle.makeFullPath(outPath,wavName,".wav")
                chunkedAudio = SI.selectVariation(barsig, sr, v, varDurationSecs)
                sf.write(wavPath, chunkedAudio, sr)

                '''Write params'''
                paramName = fileHandle.makeName(soundName, paramArr, userP, v)
                pfName = fileHandle.makeFullPath(outPath, paramName,".params")

                if recordFormat == "params" or recordFormat==0:
                    pm=paramManager.paramManager(pfName, fileHandle.getFullPath())
                    pm.initParamFiles(overwrite=True)
                    for pnum in range(len(paramArr)):
                            pm.addParam(pfName, paramArr[pnum]['pname'], [0,soundDuration], [userP[pnum], userP[pnum]], units=paramArr[pnum]['units'], nvals=paramArr[pnum]['nvals'], minval=paramArr[pnum]['minval'], maxval=paramArr[pnum]['maxval'], origUnits=None, origMinval=barsynth.getParam(paramArr[pnum]['pname']+"_exp", "min"), origMaxval=barsynth.getParam(paramArr[pnum]['pname']+"_exp", "max"))

                elif recordFormat == "sonyGan" or outType == 1:

                    sg.storeSingleRecord(wavName)
                    for pnum in range(len(paramArr)):
                        sg.addParams(wavName, paramArr[pnum]['pname'], userP[pnum], barsynth.getParam(paramArr[pnum]['pname']+"_exp"))
                    sg.write2File("sonyGan.json")
                else:
                    print("Tfrecords")
                '''write TF record'''

		#tfm=tfrecordManager.tfrecordManager(vFilesParam[v], outPath)
		#data,sr = librosa.core.load(outPath + fname + '--v-'+'{:03}'.format(v)+'.wav',sr=16000)
		#print(len(data))
		#tfm.addFeature(vFilesParam[v], 'audio', [0,len(data)], data, units='samples', nvals=len(data), minval=0, maxval=0)
		#for pnum in range(len(paramArr)):
		#	print(pnum)
		#	tfm.addFeature(vFilesParam[v], paramArr[pnum]['pname'], [0,data['soundDuration']], [enumP[pnum], enumP[pnum]], units=paramArr[pnum]['units'], nvals=paramArr[pnum]['nvals'], minval=paramArr[pnum]['minval'], maxval=paramArr[pnum]['maxval'])
		#tfm.writeRecordstoFile()
