import re
def convert(inputFile,outputFile=None):
    with open(inputFile,'r') as ff:
        zmkFile = ff.read()

    zmkFile=re.sub(r'architectureName=\"[A-Za-z\s]+\"','architectureName="mobilenet"',zmkFile)
    zmkFile=re.sub(r'max_value=\"[0-9\.]+\"','',zmkFile)
    zmkFile=zmkFile.replace('paddingType','pad')
    zmkFile=re.sub(r'trainable=\"(true|false)\"','',zmkFile)
    zmkFile=re.sub(r'units=\"[0-9]+\"','',zmkFile)

    if not outputFile:
        outputFile=inputFile
    with open(outputFile,'w') as ff:
        ff.write(zmkFile)