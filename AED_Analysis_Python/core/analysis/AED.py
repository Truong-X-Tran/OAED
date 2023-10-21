import pandas as pd
import numpy as np
import enum as Enum
from AED_Analysis_Python.core.analysis.ReagentType import ReagentType
from AED_Analysis_Python.core.analysis.BadCombination import BadCombination
from AED_Analysis_Python.core.analysis.helper import Helper


class AED:
    numberOfDistinctBuffer = 1
    scoresOfPreps = {}
    scoresOfSalts = {}
    scoresOfPhs = {}
    
    def __init__(self):
        self.scoresOfPhs.clear()
        self.scoresOfPreps.clear()
        self.scoresOfSalts.clear()


    def candidateTriples(self, triple1, triple2, index):
        candidates = [[], []]

        if index == 0:
            candidates[0] = [triple1[0], triple2[1], triple1[2]]
            candidates[1] = [triple1[0], triple1[1], triple2[2]]
        elif index == 1:
            candidates[0] = [triple2[0], triple1[1], triple1[2]]
            candidates[1] = [triple1[0], triple1[1], triple2[2]]
        else:
            candidates[0] = [triple1[0], triple2[1], triple1[2]]
            candidates[1] = [triple2[0], triple1[1], triple1[2]]

        return candidates
    
    
    def get_distinct_salt_con(self, dt, type_of_salt):
        distinct_salt_conc = dt.loc[(dt['C2_Anion'] + " " + dt['C2_Cation']) == type_of_salt, ['C2_Conc','C2_M']].drop_duplicates()
        #salts = [f"{conc}{unit}" for conc, unit in zip(distinct_salt_conc, ['M']*len(distinct_salt_conc))]
        salts = ["{} {}".format(row['C2_Conc'], row['C2_M']) for _, row in distinct_salt_conc.iterrows()]
        return salts
    
    
    def get_distinct_prep_con(self, dt, type_of_prep):
        distinct_prep_conc = dt.loc[(dt['C1_Anion'] + " " + dt['C1_Cation']) == type_of_prep, ['C1_Conc','C1_M']].drop_duplicates()
        #preps = [f"{conc}{unit}" for conc, unit in zip(distinct_prep_conc, ['M']*len(distinct_prep_conc))]
        preps = ["{} {}".format(row['C1_Conc'], row['C1_M']) for _, row in distinct_prep_conc.iterrows()]
        return preps
    
    #tran
    def get_distinct_buffers(self, dt, ph):
        distinct_buffer_types = dt.loc[dt['Ph'] == ph, ['B_Anion', 'B_Cation']].drop_duplicates()
        #distinct_buffer_types = dt.loc[dt['Ph'] == float(ph), ['B_Anion', 'B_Cation']].drop_duplicates()
        buffers = ["{} {}".format(row['B_Anion'], row['B_Cation']) for _, row in distinct_buffer_types.iterrows()]
        return buffers
    
    def generate_concentrations(self, dt_all_cocktails, candidate_triples):
        table = pd.DataFrame(columns=["Ph", "Buffer", "B_Conc", "Precipitant", "P_Conc", "Salt", "S_Conc", "Rank"])
        for i, row in candidate_triples.iterrows():
            buffer_types = self.get_distinct_buffers(dt_all_cocktails, candidate_triples.iloc[i]["Ph"])
            distinct_prep_conc = self.get_distinct_prep_con(dt_all_cocktails, candidate_triples.iloc[i]["Precipitant"])
            distinct_salt_conc = self.get_distinct_salt_con(dt_all_cocktails, candidate_triples.iloc[i]["Salt"])
            
            #print("distinct_prep_conc: \n", distinct_prep_conc)
            #print("distinct_salt_conc: \n", distinct_salt_conc)
            for j in range(len(buffer_types)):
                for m in range(len(distinct_prep_conc)):
                    for n in range(len(distinct_salt_conc)):
                        table = pd.concat([table, pd.DataFrame({"Ph": candidate_triples.iloc[i]["Ph"],
                                            "Buffer": buffer_types[j],
                                            "B_Conc": "0.1",
                                            "Precipitant": candidate_triples.iloc[i]["Precipitant"],
                                            "P_Conc": distinct_prep_conc[m],
                                            "Salt": candidate_triples.iloc[i]["Salt"],
                                            "S_Conc": distinct_salt_conc[n]}, index = [0])],
                                            ignore_index=True)

        return table
    
    #tran
    def apply_ranking(self, dt, ogdt):
        #print("dt: \n", dt)
        #print("dt.iloc[55]: \n", dt.iloc[55])
        #print("len dt: ", len(dt))
        for i in reversed(range(len(dt))):
            #print("index: ", i)
            dr = dt.iloc[i]
            rank_of_ph = self.get_rank_of_reagent(dr["Ph"], ReagentType.PH,ogdt)
            rank_of_precipitant = self.get_rank_of_reagent(dr["Precipitant"], ReagentType.CHEMICAL,ogdt)
            rank_of_salt = self.get_rank_of_reagent(dr["Salt"], ReagentType.CHEMICAL,ogdt)
            self.update_reagent_score_lists(dr["Ph"], rank_of_ph, dr["Precipitant"], rank_of_precipitant, dr["Salt"], rank_of_salt)
            overall_rank = (rank_of_ph + rank_of_precipitant + rank_of_salt) / 3
            #dr["Rank"] = overall_rank
            #dt.iloc[i]["Rank"] = overall_rank
            #dr.set_value('Rank',overall_rank)
            #dt.at(dt.iloc[i].name,'Rank',overall_rank)
            #dt.iloc[i].at["Rank"] = overall_rank
            dt.at[dt.iloc[i].name,'Rank'] = overall_rank
            if overall_rank < 1:
                 dt.drop(dt.iloc[i].name, inplace=True)

    def SortResultsBasedOnRanks(self,dt):
        dt.sort_values(by = ['Rank'])
    
    def update_reagent_score_lists(self, pH, rank_of_pH, prep, rank_of_precipitant, salt, rank_of_salt):
        if pH not in self.scoresOfPhs:
            self.scoresOfPhs[pH] = rank_of_pH
        if prep not in self.scoresOfPreps:
            self.scoresOfPreps[prep] = rank_of_precipitant
        if salt not in self.scoresOfSalts:
            self.scoresOfSalts[salt] = rank_of_salt

    
    def get_avg_score(self,ogdt):
        avg_score = ogdt[['S_a', 'S_b','S_c']].astype(float).mean(axis=1).mean()
        '''
        avg_score = Helper.inputScreenFile.Tables[0].AsEnumerable() \
            .Select(lambda tuple: {'avgScore': (tuple.Field('S_a') + tuple.Field('S_b') + tuple.Field('S_c')) / 3}) \
            .Average(lambda i: i['avgScore'])
        '''
        #print(avg_score)
        return avg_score
    
    #tran
    def get_rank_of_reagent(self, reagent, rt,ogdt):
        if rt == ReagentType.PH:
            # CalculateRankOfPh
            avg_rank_of_ph = ogdt.loc[ogdt['Ph'] == reagent, ['S_a', 'S_b','S_c']].astype(float).mean(axis=1).mean()
            #print("rank_of_ph: \n", ogdt.loc[ogdt['Ph'] == reagent, ['S_a', 'S_b','S_c']])
            #print("avg_rank_of_ph: \n", avg_rank_of_ph)
            
            avg_rank_of_not_ph = ogdt.loc[ogdt['Ph'] != reagent, ['S_a', 'S_b','S_c']].astype(float).mean(axis=1).mean()
            #print("rank_of_not_ph: \n", ogdt.loc[ogdt['Ph'] != reagent, ['S_a', 'S_b','S_c']])
            #print("avg_rank_of_not_ph: \n", avg_rank_of_not_ph)
            
            '''
            avg_rank_of_not_ph = (
                #Helper.inputScreenFile.Tables[0].AsEnumerable()
                ogdt.where(lambda tuple: tuple.Field[str]("Ph") != reagent)
                .select(lambda tuple: (
                    (tuple.Field[float]("S_a") + tuple.Field[float]("S_b") + tuple.Field[float]("S_c")) / 3,
                ))
                .Average(lambda i: i[0])
            )
            '''            
            return float(avg_rank_of_ph) / float(avg_rank_of_not_ph)

        else:
            # CalculateRankOfChemical
            '''
            avg_rank_of_chem = (
                #Helper.inputScreenFile.Tables[0].AsEnumerable()
                ogdt.where(lambda tuple: (
                    (tuple.Field[str]("C1_Anion") + " " + tuple.Field[str]("C1_Cation") == reagent) or
                    (tuple.Field[str]("C2_Anion") + " " + tuple.Field[str]("C2_Cation") == reagent) or
                    (tuple.Field[str]("C3_Anion") + " " + tuple.Field[str]("C3_Cation") == reagent) or
                    (tuple.Field[str]("C4_Anion") + " " + tuple.Field[str]("C4_Cation") == reagent) or
                    (tuple.Field[str]("C5_Anion") + " " + tuple.Field[str]("C5_Cation") == reagent)
                ))
                .select(lambda tuple: (
                    (tuple.Field[float]("S_a") + tuple.Field[float]("S_b") + tuple.Field[float]("S_c")) / 3,
                ))
                .Average(lambda i: i[0])
            )

            if reagent != " ":
                avg_rank_of_not_chem = (
                    #Helper.inputScreenFile.Tables[0].AsEnumerable()
                    ogdt.where(lambda tuple: (
                        (tuple.Field[str]("C1_Anion") + " " + tuple.Field[str]("C1_Cation") != reagent) and
                        (tuple.Field[str]("C2_Anion") + " " + tuple.Field[str]("C2_Cation") != reagent) and
                        (tuple.Field[str]("C3_Anion") + " " + tuple.Field[str]("C3_Cation") != reagent) and
                        (tuple.Field[str]("C4_Anion") + " " + tuple.Field[str]("C4_Cation") != reagent) and
                        (tuple.Field[str]("C5_Anion") + " " + tuple.Field[str]("C5_Cation") != reagent)
                    ))
                    .select(lambda tuple: (
                        (tuple.Field[float]("S_a") + tuple.Field[float]("S_b") + tuple.Field[float]("S_c")) / 3,
                    ))
                    .Average(lambda i: i[0])
                )

                return float(avg_rank_of_chem) / float(avg_rank_of_not_chem)
            '''
            avg_rank_of_chem = ogdt.loc[((ogdt['C1_Anion'] + " " + ogdt['C1_Cation']) == reagent) |
                                        ((ogdt['C2_Anion'] + " " + ogdt['C2_Cation']) == reagent) |
                                        ((ogdt['C3_Anion'] + " " + ogdt['C3_Cation']) == reagent) |
                                        ((ogdt['C4_Anion'] + " " + ogdt['C4_Cation']) == reagent) |
                                        ((ogdt['C5_Anion'] + " " + ogdt['C5_Cation']) == reagent), ['S_a', 'S_b','S_c']].astype(float).mean(axis=1).mean()
            if reagent != " ":
                avg_rank_of_not_chem = ogdt.loc[(ogdt['C1_Anion'] + " " + ogdt['C1_Cation'] != reagent) &
                                        ((ogdt['C2_Anion'] + " " + ogdt['C2_Cation']) != reagent) &
                                        ((ogdt['C3_Anion'] + " " + ogdt['C3_Cation']) != reagent) &
                                        ((ogdt['C4_Anion'] + " " + ogdt['C4_Cation']) != reagent) &
                                        ((ogdt['C5_Anion'] + " " + ogdt['C5_Cation']) != reagent), ['S_a', 'S_b','S_c']].astype(float).mean(axis=1).mean()
                return float(avg_rank_of_chem) / float(avg_rank_of_not_chem)
            else:
                return float(avg_rank_of_chem) / self.get_avg_score(ogdt)
    #tran
    def GenerateCandidateTriples(self, tripleAgents):
        table = pd.DataFrame(columns=["Ph", "Precipitant", "Salt"])

        for i in range(len(tripleAgents[0])):
            for j in range(len(tripleAgents) - 1):
                for k in range(j + 1, len(tripleAgents)):
                    if tripleAgents[j][i] == None and tripleAgents[k][i] == None:
                        tmp = self.candidateTriples(tripleAgents[j], tripleAgents[k], i)
                        table = table.append(pd.DataFrame(tmp, columns=["Ph", "Precipitant", "Salt"]), ignore_index=True)
                    elif tripleAgents[j][i] == None or tripleAgents[k][i] == None:
                        tmp = self.candidateTriples(tripleAgents[j], tripleAgents[k], i)
                        table = table.append(pd.DataFrame(tmp, columns=["Ph", "Precipitant", "Salt"]), ignore_index=True)
                    elif tripleAgents[j][i].strip() == tripleAgents[k][i].strip():
                        tmp = self.candidateTriples(tripleAgents[j], tripleAgents[k], i)
                        table = pd.concat([table,pd.DataFrame(tmp, columns=["Ph", "Precipitant", "Salt"])], ignore_index=True)
                    else:
                        continue
        #print("non-drop: \n", table)
        distinctValues = table.drop_duplicates().reset_index(drop=True)
        distinctValues.columns = ["Ph", "Precipitant", "Salt"]
        #print("out: \n", distinctValues)
        #check nan
        #print(distinctValues["Ph"].isnull())
        #replace nan with empty string
        #distinctValues = distinctValues[['Ph','Precipitant','Salt' ]] = distinctValues[['Ph','Precipitant', 'Salt' ]].fillna('')
        distinctValues2 = distinctValues.fillna("")
        #print("out not NaN: \n", distinctValues2)
        return distinctValues2
        
    def checkUniqeness(self, dt, ogdt):
        currentConditions = [{'pH': row['Ph'], 'precipitant': row['C1_Anion'] + ' ' + row['C1_Cation'], 
                            'prepConc': row['C1_Conc'] + row['C1_M'], 'salt': row['C2_Anion'] + ' ' + row['C2_Cation'], 
                            'saltConc': row['C2_Conc'] + row['C2_M']} 
                            for _, row in ogdt.iterrows()] #tran
        currentConditions = [dict(t) for t in {tuple(d.items()) for d in currentConditions}]
        
        for i in range(len(dt)-1, -1, -1):
            exist = False

            # if precipitant and salt are equal, it's a bad screen, delete it
            if dt.iloc[i, 3] == dt.iloc[i, 5]:
                dt = dt.drop(dt.index[i])
                continue

            for j in range(len(currentConditions)):
                if dt.iloc[i, 0].strip() == "7" and dt.iloc[i, 5].strip() == "LITHIUM SULFATE":
                    x = 1
                if currentConditions[j]['pH'] == dt.iloc[i, 0].strip() and currentConditions[j]['precipitant'] == dt.iloc[i, 3].strip() \
                    and currentConditions[j]['prepConc'] == dt.iloc[i, 4].strip() and currentConditions[j]['salt'] == dt.iloc[i, 5].strip() \
                    and currentConditions[j]['saltConc'] == dt.iloc[i, 6].strip():
                    exist = True
                    break

            if exist:
                dt = dt.drop(dt.index[i])

        return dt

    def get_distinct_triples(self, dt):

        distinct_triples = []
        for index, row in dt.iterrows():
            triple = {
                #"pH": str(row["Ph"]),
                #"precipitant": str(row["C1_Anion"]) + " " + str(row["C1_Cation"]),
                #"salt": str(row["C2_Anion"]) + " " + str(row["C2_Cation"])
                "pH": str(row["Ph"]),
                "precipitant": str(row["C1_Anion"]) + " " + str(row["C1_Cation"]),
                "salt": str(row["C2_Anion"]) + " " + str(row["C2_Cation"])
            }
            if triple not in distinct_triples:
                distinct_triples.append(triple)

        triple_agents = [[t["pH"], t["precipitant"], t["salt"]] for t in distinct_triples]
        return triple_agents
        
    def sort_results_based_on_ranks(self,dt):
        sorted_table = dt.sort_values(by=["Rank"], ascending=False)
        return sorted_table
    
    def check_bad_combinations(self, chemical_list):
        chemical = None
        counter = 0
        badCom1 = False
        badCom2 = False
        #print("Helper.badCom1: \n", Helper.badCom1) #tran
        #print("Helper.badCom2: \n", Helper.badCom2) #tran
        for i in range(len(chemical_list)):
            chemical = str(chemical_list[i])
            while counter < max(len(Helper.badCom1), len(Helper.badCom2)):
                if counter < len(Helper.badCom1):
                    if chemical.find(Helper.badCom1[counter]) != -1:
                        y = chemical.find(Helper.badCom1[counter])
                        badCom1 = True
                if counter < len(Helper.badCom2):
                    if chemical.find(Helper.badCom2[counter]) != -1:
                        badCom2 = True
                counter += 1
            counter = 0
        
        if badCom1 and badCom2:
            return True
        else:
            return False
        
    def EliminateBadCombinations(self, candidateCocktails):
        for i in range(len(candidateCocktails)-1, -1, -1):
            badComb = self.check_bad_combinations(candidateCocktails.iloc[i])
            if badComb:
                candidateCocktails = candidateCocktails.drop(i)
        return candidateCocktails
    
    def ApplyAED(self, dt, originDT):
        #tran
        tripleAgents = self.get_distinct_triples(dt)
        dtTriplets = self.GenerateCandidateTriples(tripleAgents)
        #print("rangeOfScreensTable: \n", dt) #tran
        #print("dtTriplets: \n", dtTriplets)#tran
        rangeOfScreensTable = dt.astype(str) #change all to string. 
        candidateCocktails = self.generate_concentrations(rangeOfScreensTable, dtTriplets)
        originDT = originDT.astype(str) # #change all to string.
        candidateCocktails = self.checkUniqeness(candidateCocktails,originDT)
        self.EliminateBadCombinations(candidateCocktails)
        if candidateCocktails.size != 0:
            self.apply_ranking(candidateCocktails,originDT)
            candidateCocktails = self.sort_results_based_on_ranks(candidateCocktails)
        return candidateCocktails