

# loosely inspired from the parammanager
import os

class fileHandler():

    def __init__(self) :

        self.fname=""
        self.outpath = ""

    '''make file name from soundname, paramNames, param values and variation number'''
    def makeName(self, soundName, paramArr, enumP, v):
        '''Construct filenames with static parameters'''
        self.fname = soundName
        for paramNum in range(len(paramArr)):
            self.fname = self.fname + '--' + paramArr[paramNum]['pname'] + '-'+'{:05.2f}'.format(enumP[paramNum])
        self.fname = self.fname + '--v-'+'{:03}'.format(v)
        return self.fname

    def getFileName(self):
        return self.fname

    def getFullPath(self):
        return self.outpath

    # only store the actual value, not the normed value used for setting
    def makeFullPath(self, outpath, name, ext) :

        if os.path.isdir(outpath):
            self.outpath = outpath
        else:
            self.outpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), outpath)
            if not os.path.isdir(self.outpath):
                os.mkdir(self.outpath)

        fullpath = os.path.join(outpath, name + ext)
        return fullpath
