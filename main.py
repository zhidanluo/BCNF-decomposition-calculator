import utils
import os

# change this path to your input folder
# do NOT add txt files that is not a valid input
fileFolder = "./input/"

for file in sorted(os.listdir(fileFolder)):
    if file[-4:] == '.txt':
        fileName = fileFolder + file
        utils.printSol(fileName)
