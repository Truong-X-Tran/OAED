from AED_Analysis_Python.core.analysis.helper import Helper
from AED_Analysis_Python.core.analysis.AED import AED
import os
import random
import string

# printing lowercase


class EntryPoint:

    def __init__(self) -> None:
        self.hp = Helper()
        pass


    def computeAED(self, inputFileName, lowestScore, highestScore):
        inputFilePath = os.path.join(os.getcwd(), "AED_Analysis_Python", "core", "analysis", "media", inputFileName)
        #print("inputFilePath: ", inputFilePath)
        status_code = self.hp.readExcelFile(inputFilePath, lowestScore, highestScore)
        if status_code == -1:
            print("Error! input is not a file!!")
            exit
        myAED = AED()
        if self.hp.rangeOfScreensTable is not None and self.hp.inputScreenFile.shape[0] > 0:
            candidateCocktails = myAED.ApplyAED(self.hp.rangeOfScreensTable,self.hp.inputScreenFile)
        
        letters = string.ascii_lowercase
        random_string = ''.join(random.choice(letters) for i in range(5))

        outputFileName='output_' + random_string + '.xlsx' 
        outputFilePath = os.path.join(os.getcwd(), "AED_Analysis_Python", "core", "analysis", "media", outputFileName)
        #outputFilePath = os.path.join(os.getcwd(), "media", outputFileName)
        
        self.hp.writeExcelFile(candidateCocktails, outputFilePath)
        
        return outputFileName
