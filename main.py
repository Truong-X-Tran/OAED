from AED_Analysis_Python.core.analysis.helper import Helper
from AED_Analysis_Python.core.analysis.AED import AED

lowestScore = 4
highestScore = 9
inputFileName = "input.xlsx"
outputFileName = "output.xlsx"

hp = Helper()

status_code = hp.readExcelFile(inputFileName, lowestScore, highestScore)
if status_code == -1:
    print("Error")
    exit

myAED = AED()
if hp.rangeOfScreensTable is not None and hp.inputScreenFile.shape[0] > 0:

    candidateCocktails = myAED.ApplyAED(hp.rangeOfScreensTable)

# if candidateCocktails.Rows.Count != 0:
#     if hp.WriteExcelFile(candidateCocktails, outputFileName):
#         print("Excel file saved")
#     else:
#         print("Error")



