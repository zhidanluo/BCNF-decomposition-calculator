from utils import BCNF, checkFile
import os
import _config

inputFileFolder = _config.inputFileFolder
specify = _config.specify

# make input folder
if not os.path.exists(inputFileFolder):
    os.makedirs(inputFileFolder)
    print("No input file found! Please add input file under '%s'!" % inputFileFolder)
    os._exit(0)

# make save folder
outputFileFolder = "./output/"
if not os.path.exists(outputFileFolder):
    os.makedirs(outputFileFolder)

# check input folder
files = sorted(os.listdir(inputFileFolder))
num_txtFiles = len([file for file in files if file[-4:] == ".txt"])
if num_txtFiles == 0:
    print("No input file found! Please add input file under '%s'!" % inputFileFolder)
    os._exit(0)

# begin calculating BCNF
if not specify:
    for file in sorted(os.listdir(inputFileFolder)):
        if file != '.DS_Store':
            checkFile(file)
    for file in sorted(os.listdir(inputFileFolder)):
        BCNF(file)
else:
    file = specify
    if not os.path.exists(inputFileFolder+file):
        print("No input file named '%s'!" % file)
        os._exit(0)
    checkFile(file)
    BCNF(file)
