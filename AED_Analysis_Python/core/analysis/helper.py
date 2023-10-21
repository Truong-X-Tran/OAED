import os
import pandas as pd
import numpy as np


class Helper:
    badCom1 = [] #tran
    badCom2 = [] #tran
    def __init__(self):
        self.conn = None
        self.strFileType = '.xlsx'
        self.inputScreenFile = None
        self.rangeOfScreensTable = None
        self.badCom1 = []
        self.badCom2 = []
        self.readListOfBadCombinations()

    def readListOfBadCombinations(self):
        with open(os.path.join(os.getcwd(),'AED_Analysis_Python', 'core', 'analysis' ,'listOfC1.txt'), 'r') as file:
            for line in file:
                self.badCom1.append(line.upper().strip())

        with open(os.path.join(os.getcwd(),'AED_Analysis_Python', 'core', 'analysis', 'listOfC2.txt'), 'r') as file:
            for line in file:
                self.badCom2.append(line.upper().strip())

    def getRangeOfScreens(self, lowestScore, highestScore):
        if self.inputScreenFile is not None:
            #self.inputScreenFile[["S_a","S_b", "S_c"]] = self.inputScreenFile[["S_a","S_b", "S_c"]].fillna(0)
            rangeOfScreens = self.inputScreenFile[(self.inputScreenFile['S_a'].gt(lowestScore) & self.inputScreenFile['S_a'].lt(highestScore)) |
                                                (self.inputScreenFile['S_b'].gt(lowestScore) & self.inputScreenFile['S_b'].lt(highestScore)) |
                                                (self.inputScreenFile['S_c'].gt(lowestScore) & self.inputScreenFile['S_c'].lt(highestScore)) &
                                                (self.inputScreenFile['C3_Anion'] == '')]
            #print("rangeOfScreens: \n", rangeOfScreens)
            if not rangeOfScreens.empty:
                self.rangeOfScreensTable = rangeOfScreens
    
    #tran remove all NaN
    def readExcelFile(self, filePath, lowestScore, highestScore):
        #print("In the helper: ", filePath) #tran
        if not os.path.isfile(filePath):
            print("not a file!!!!")
            return -1
        tmp = pd.read_excel(filePath) 
        #print("file: \n", tmp)
        tmp[["S_a","S_b", "S_c"]] = tmp[["S_a","S_b", "S_c"]].fillna(0)
        self.inputScreenFile = tmp.fillna("") # remove all NaN 
        #print("try remove nan: \n", self.inputScreenFile) #tran
        #self.inputScreenFile = pd.read_excel(filePath)
        #print("inputScreenFile: \n", self.inputScreenFile)
        self.inputScreenFile = self.inputScreenFile.applymap(lambda x: x.strip().upper() if isinstance(x, str) else x)
        self.getRangeOfScreens(lowestScore, highestScore)
        #print("inputScreenFile processed: \n", self.inputScreenFile)

        return 0
    
    # def writeExcelFile(Tbl: pd.DataFrame, ExcelFilePath: str = None) -> bool:
    #     if os.path.exists(ExcelFilePath):
    #         os.remove(ExcelFilePath)

    #     connection_string = f"Provider=Microsoft.ACE.OLEDB.12.0;Data Source={ExcelFilePath};Extended Properties='Excel 12.0 XML;HDR=Yes;IMEX=0'"
    #     with pyodbc.connect(connection_string) as conn:
    #         cursor = conn.cursor()

    #         # WriteCandidateCocktails
    #         cursor.execute("""CREATE TABLE [LIST_OF_CANDIDATES] (Well_Id VARCHAR,
    #                         B_Anion	VARCHAR,B_Cation	VARCHAR,Ph	VARCHAR,B_Conc	VARCHAR,
    #                         C1_Anion	VARCHAR, C1_Cation	VARCHAR, C1_Conc	VARCHAR, C1_M	VARCHAR, C1_Ph	VARCHAR,
    #                         C2_Anion	VARCHAR, C2_Cation	VARCHAR, C2_Conc	VARCHAR, C2_M	VARCHAR, C2_Ph	VARCHAR,
    #                         C3_Anion	VARCHAR, C3_Cation	VARCHAR, C3_Conc	VARCHAR, C3_M	VARCHAR, C3_Ph	VARCHAR,
    #                         C4_Anion	VARCHAR, C4_Cation	VARCHAR, C4_Conc	VARCHAR, C4_M	VARCHAR, C4_Ph	VARCHAR,
    #                         C5_Anion	VARCHAR, C5_Cation	VARCHAR, C5_Conc	VARCHAR, C5_M	VARCHAR, C5_Ph	VARCHAR,
    #                         S_a	DOUBLE, S_b	DOUBLE, S_c	DOUBLE, Rank	DOUBLE);""")

    #         for i in range(len(Tbl)):
    #             command = "INSERT INTO [LIST_OF_CANDIDATES] (Ph,B_Anion,B_Conc,C1_Anion,C1_Conc,C2_Anion,C2_Conc,Rank) VALUES("
    #             for j in range(len(Tbl.columns)):
    #                 if Tbl.dtypes[j] == 'object':
    #                     command += f"'{Tbl.iloc[i][j]}',"
    #                 else:
    #                     command += f"{Tbl.iloc[i][j]})"
    #             cursor.execute(command)

    #         # WriteListOfScores
    #         cursor.execute("""CREATE TABLE [LIST_OF_SCORES] (Ph VARCHAR,
    #                         Ph_Rank	VARCHAR,Precipitant	VARCHAR,Precipitant_Rank	VARCHAR,Salt	VARCHAR,
    #                         Salt_Rank	VARCHAR);""")

    #         dtScores = GetListOfScores()
    #         for index, row in dtScores.iterrows():
    #             command = f"INSERT INTO [LIST_OF_SCORES] (Ph,Ph_Rank,Precipitant,Precipitant_Rank,Salt,Salt_Rank) VALUES("
    #             for item in row:
    #                 command += f"'{item}',"
    #             command = command[:-1] + ")"
    #             cursor.execute(command)

    #     return True
    
    def get_list_of_scores():
        dtScores = pd.DataFrame(columns=["Ph", "PhRank", "Prep", "PrepRank", "Salt", "SaltRank"])

        scoresOfPhs = sorted(AED.scoresOfPhs.items(), key=lambda x: x[1], reverse=True)
        scoresOfPreps = sorted(AED.scoresOfPreps.items(), key=lambda x: x[1], reverse=True)
        scoresOfSalts = sorted(AED.scoresOfSalts.items(), key=lambda x: x[1], reverse=True)
        max_length = max(len(scoresOfPhs), len(scoresOfPreps), len(scoresOfSalts))

        for index in range(max_length):
            row = {}
            if index < len(scoresOfPhs):
                row["Ph"] = scoresOfPhs[index][0]
                row["PhRank"] = str(scoresOfPhs[index][1])
            else:
                row["Ph"] = ""
                row["PhRank"] = ""

            if index < len(scoresOfPreps):
                row["Prep"] = scoresOfPreps[index][0]
                row["PrepRank"] = str(scoresOfPreps[index][1])
            else:
                row["Prep"] = ""
                row["PrepRank"] = ""

            if index < len(scoresOfSalts):
                row["Salt"] = scoresOfSalts[index][0]
                row["SaltRank"] = str(scoresOfSalts[index][1])
            else:
                row["Salt"] = ""
                row["SaltRank"] = ""

            dtScores = dtScores.append(row, ignore_index=True)

        return dtScores
    

    def writeExcelFile(self, df, excelFilePath):
        print(excelFilePath)
        with pd.ExcelWriter(excelFilePath) as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
    