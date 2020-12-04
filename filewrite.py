

# loosely inspired from the parammanager

import soundfile as sf
import os

class sound2File():

    def __init__(self,outpath, ext=".wav") :

        self.fname=""
        # if directory exists, then ok, or else create relative to main directory
        if os.path.isdir(outpath):
            self.outpath = outpath
        else:
            self.outpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), outpath)
            if not os.path.isdir(self.outpath):
                os.mkdir(self.outpath)
        self.ext=ext

    '''make file name from soundname, paramNames, param values and variation number'''
    def __makeName__(self, soundName, paramArr, enumP, v):
        '''Construct filenames with static parameters'''
        self.fname = soundName
        for paramNum in range(len(paramArr)):
            self.fname = self.fname + '--' + paramArr[paramNum]['pname'] + '-'+'{:05.2f}'.format(enumP[paramNum])
        self.fname = self.fname + '--v-'+'{:03}'.format(v)

    def __getFile__(self):
        return self.fname

    def __getOutpath__(self):
        return self.outpath

    # only store the actual value, not the normed value used for setting
    def __writeFile__(self, signal, sr) :
        fullpath = os.path.join(self.outpath, self.fname + self.ext)
        sf.write(fullpath, signal, sr)
