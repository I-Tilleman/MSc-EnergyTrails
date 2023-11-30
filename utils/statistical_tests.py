from tqdm import tqdm
import pickle
from matplotlib import pyplot as plt
import matplotlib as mpl
import logging
import sys
import pandas as pd 
import numpy as np 
import os
from matplotlib import font_manager as fm, rcParams
from cycler import cycler 
from scipy.stats import chi2_contingency
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scikit_posthocs import posthoc_dunn
import csv
import json

def main(argument):
    if argument[0] == 'yesps_2':
        reduced_len = 600
        with open('outfile-00_2_yesps-temp', 'rb') as fp:
            results_00 = pickle.load(fp)
        
        with open('outfile-01_2_yesps-temp', 'rb') as fp:
            results_01 = pickle.load(fp)
        
        with open('outfile-11_2_yesps-temp', 'rb') as fp:
            results_11 = pickle.load(fp)

        with open('outfile-02_2_yesps-temp', 'rb') as fp:
            results_02 = pickle.load(fp)
            
        with open('outfile-12_2_yesps-temp', 'rb') as fp:
            results_12 = pickle.load(fp)
            
        with open('outfile-22_2_yesps-temp', 'rb') as fp:
            results_22 = pickle.load(fp)
        
    if argument[0] == 'nops_2':
        reduced_len = 600
        with open('outfile-00_2_nops-temp', 'rb') as fp:
            results_00 = pickle.load(fp)
        
        with open('outfile-01_2_nops-temp', 'rb') as fp:
            results_01 = pickle.load(fp)
            
        with open('outfile-11_2_nops-temp', 'rb') as fp:
            results_11 = pickle.load(fp)

        with open('outfile-02_2_nops-temp', 'rb') as fp:
            results_02 = pickle.load(fp)
            
        with open('outfile-12_2_nops-temp', 'rb') as fp:
            results_12 = pickle.load(fp)
            
        with open('outfile-22_2_nops-temp', 'rb') as fp:
            results_22 = pickle.load(fp)

    
    if argument[0] == 'yesps_4':
        reduced_len = 125
        with open('outfile-00-temp', 'rb') as fp:
            results_00 = pickle.load(fp)
        with open('outfile-01-temp', 'rb') as fp:
            results_01 = pickle.load(fp)
        with open('outfile-02-temp', 'rb') as fp:
            results_02 = pickle.load(fp)
        with open('outfile-11-temp', 'rb') as fp:
            results_11 = pickle.load(fp)
        with open('outfile-12-temp', 'rb') as fp:
            results_12 = pickle.load(fp)
        with open('outfile-22-temp', 'rb') as fp:
            results_22 = pickle.load(fp)


    if argument[0] == 'nops_4':
        reduced_len = 125
        with open('outfile-00_nops-temp', 'rb') as fp:
            results_00 = pickle.load(fp)
        with open('outfile-01_nops-temp', 'rb') as fp:
            results_01 = pickle.load(fp)
        with open('outfile-02_nops-temp', 'rb') as fp:
            results_02 = pickle.load(fp)
        with open('outfile-11_nops-temp', 'rb') as fp:
           results_11 = pickle.load(fp)
        with open('outfile-12_nops-temp', 'rb') as fp:
            results_12 = pickle.load(fp)
        with open('outfile-22_nops-temp', 'rb') as fp:
            results_22 = pickle.load(fp)


    situations_results = [results_00, results_01, results_02, results_11, results_12, results_22]
    situations = ['0 vs 0', '0 vs 1', '0 vs 2', '1 vs 1', '1 vs 2', '2 vs 2']


    for result in situations_results:
        #enumerated loop, if negotiation_rounds is 25 then accepted is 0
            for i, x in enumerate(result['negotiation_rounds']):
                if x == 25:
                    result['accepted'].insert(i, 0)
                    result['scores'].insert(i, 0)

    for data in situations_results:
        for key, value in data.items():
            if isinstance(value, list):  # Check if the value is a list
                data[key] = value[-reduced_len:]  # Slice the last 2 elements for lists
            else:
                data[key] = value  # Keep integers as they are

        if len(data['negotiation_rounds']) == reduced_len:
            data['total'] = reduced_len  
    
    ## Test statistical significance of acceptance rates 
    print("--ACCEPTANCE RATES--")
    
    data = np.array([[results_00['accepted'].count(1), results_00['accepted'].count(0)],
                     [results_01['accepted'].count(1), results_01['accepted'].count(0)],
                     [results_02['accepted'].count(1), results_02['accepted'].count(0)],
                     [results_11['accepted'].count(1), results_11['accepted'].count(0)],
                     [results_12['accepted'].count(1), results_12['accepted'].count(0)],
                     [results_22['accepted'].count(1), results_22['accepted'].count(0)],
                     ])
        
    chi2, p, dof, expected = chi2_contingency(data)
    
    print("The p-value is", p)
    
    if p > 0.05:
        print("This is not satistically significant\n")
    else: 
        print("This is statistically significant\n")
        
    pair1_data = np.array([[results_00['accepted'].count(1), results_00['accepted'].count(0)], [results_01['accepted'].count(1), results_01['accepted'].count(0)]])
    pair2_data = np.array([[results_00['accepted'].count(1), results_00['accepted'].count(0)], [results_02['accepted'].count(1), results_02['accepted'].count(0)]])
    pair3_data = np.array([[results_00['accepted'].count(1), results_00['accepted'].count(0)], [results_11['accepted'].count(1), results_11['accepted'].count(0)]])
    pair4_data = np.array([[results_00['accepted'].count(1), results_00['accepted'].count(0)], [results_12['accepted'].count(1), results_12['accepted'].count(0)]])
    pair5_data = np.array([[results_00['accepted'].count(1), results_00['accepted'].count(0)], [results_22['accepted'].count(1), results_22['accepted'].count(0)]])
    
    pairs = [pair1_data, pair2_data, pair3_data, pair4_data, pair5_data]
    
    for pair in pairs:
        number = 1
        chi2, p, dof, expected = chi2_contingency(pair)
        
        print("For pair", number, "the p value is", p)
        alpha = 0.05
        if p < alpha:
            print("There is a significant difference\n")
        else:
            print("There is not a significant difference\n")
            
    ## Test statistical significance of scores with rejections
    
    normal = True
    
    for result in situations_results:
        stat, p = stats.shapiro(result['scores'])
        if not p > 0.05:
            normal = False
            
    print("\n--POINT INCREASE--")
    
    # Combine data into one list 
    all_points = results_00['scores'] + results_01['scores'] + results_02['scores'] + results_11['scores'] + results_12['scores'] + results_22['scores']
    
    # Create labels
    labels = ["0 vs. 0"] * len(results_00['scores']) + ["0 vs. 1"] * len(results_01['scores']) + ["0 vs. 2"] * len(results_02['scores']) + ["1 vs. 1"] * len(results_11['scores']) + ["1 vs. 2"] * len(results_12['scores']) + ["2 vs. 2"] * len(results_22['scores'])
    
    data = pd.DataFrame({'Points Gained': all_points, 'Strategy': labels})
    
    if normal: 
        # Perform one-way ANOVA
        result = stats.f_oneway(*[data['Points Gained'][data['Strategy'] == s] for s in data['Strategy'].unique()])

        # Display the ANOVA results
        print("One-way ANOVA results:")
        print(result)
        
        # Perform one-way ANOVA (if you haven't already)
        anova = sm.OLS.from_formula('data["Points Gained"] ~ data["Strategy"]', data=data).fit()

        # Perform Tukey-Kramer post-hoc test
        tukey = pairwise_tukeyhsd(data['Points Gained'], data['Strategy'])

        # Print the ANOVA results
        print("\nANOVA results:")
        print(anova.summary())

        # Print the Tukey-Kramer results
        print("\nTukey-Kramer post-hoc test:")
        print(tukey.summary())

    else: 
        result = stats.kruskal(results_00['scores'], results_01['scores'], results_02['scores'], results_11['scores'], results_12['scores'], results_22['scores'])
        # Display the Kruskal-Wallis results
        print("Kruskal-Wallis results:")
        print(result)
        
        # Perform Dunn's test for pairwise comparisons
        dunn_results = posthoc_dunn(data, val_col='Points Gained', group_col='Strategy')

        # Print the results
        print("\nDunn's test results:")
        print(dunn_results)

    print("\n--POINT INCREASE CORRECTED--")
    
    results_00['scores'] = [x for x,y in zip(results_00['scores'], results_00['accepted']) if y == 1]
    results_01['scores'] = [x for x,y in zip(results_01['scores'], results_01['accepted']) if y == 1]
    results_02['scores'] = [x for x,y in zip(results_02['scores'], results_02['accepted']) if y == 1]
    results_11['scores'] = [x for x,y in zip(results_11['scores'], results_11['accepted']) if y == 1]
    results_12['scores'] = [x for x,y in zip(results_12['scores'], results_12['accepted']) if y == 1]
    results_22['scores'] = [x for x,y in zip(results_22['scores'], results_22['accepted']) if y == 1]
    
    # Combine data into one list 
    all_points = results_00['scores'] + results_01['scores'] + results_02['scores'] + results_11['scores'] + results_12['scores'] + results_22['scores']
    
    # Create labels
    labels = ["0 vs. 0"] * len(results_00['scores']) + ["0 vs. 1"] * len(results_01['scores']) + ["0 vs. 2"] * len(results_02['scores']) + ["1 vs. 1"] * len(results_11['scores']) + ["1 vs. 2"] * len(results_12['scores']) + ["2 vs. 2"] * len(results_22['scores'])
    
    data = pd.DataFrame({'Points Gained': all_points, 'Strategy': labels})
    
    if normal: 
        # Perform one-way ANOVA
        result = stats.f_oneway(*[data['Points Gained'][data['Strategy'] == s] for s in data['Strategy'].unique()])

        # Display the ANOVA results
        print("One-way ANOVA results:")
        print(result)
        
        # Perform one-way ANOVA (if you haven't already)
        anova = sm.OLS.from_formula('data["Points Gained"] ~ data["Strategy"]', data=data).fit()

        # Perform Tukey-Kramer post-hoc test
        tukey = pairwise_tukeyhsd(data['Points Gained'], data['Strategy'])

        # Print the ANOVA results
        print("\nANOVA results:")
        print(anova.summary())

        # Print the Tukey-Kramer results
        print("\nTukey-Kramer post-hoc test:")
        print(tukey.summary())

    else: 
        result = stats.kruskal(results_00['scores'], results_01['scores'], results_02['scores'], results_11['scores'], results_12['scores'], results_22['scores'])
        # Display the Kruskal-Wallis results
        print("Kruskal-Wallis results:")
        print(result)
        
        # Perform Dunn's test for pairwise comparisons
        dunn_results = posthoc_dunn(data, val_col='Points Gained', group_col='Strategy')

        # Print the results
        print("\nDunn's test results:")
        print(dunn_results)
        
    print("\n-- NUMBER OF ROUNDS (corrected) --")
    results_00['negotiation_rounds'] = list(filter(lambda x: x != 25, results_00['negotiation_rounds']))
    results_01['negotiation_rounds'] = list(filter(lambda x: x != 25, results_01['negotiation_rounds']))
    results_02['negotiation_rounds'] = list(filter(lambda x: x != 25, results_02['negotiation_rounds']))
    results_11['negotiation_rounds'] = list(filter(lambda x: x != 25, results_11['negotiation_rounds']))
    results_12['negotiation_rounds'] = list(filter(lambda x: x != 25, results_12['negotiation_rounds']))
    results_22['negotiation_rounds'] = list(filter(lambda x: x != 25, results_22['negotiation_rounds']))

    # Combine data into one list 
    all_points = results_00['negotiation_rounds'] + results_01['negotiation_rounds'] + results_02['negotiation_rounds'] + results_11['negotiation_rounds'] + results_12['negotiation_rounds'] + results_22['negotiation_rounds']
    
    # Create labels
    labels = ["0 vs. 0"] * len(results_00['negotiation_rounds']) + ["0 vs. 1"] * len(results_01['negotiation_rounds']) + ["0 vs. 2"] * len(results_02['negotiation_rounds']) + ["1 vs. 1"] * len(results_11['negotiation_rounds']) + ["1 vs. 2"] * len(results_12['negotiation_rounds']) + ["2 vs. 2"] * len(results_22['negotiation_rounds'])
    
    data = pd.DataFrame({'Points Gained': all_points, 'Strategy': labels})
    
    if normal: 
        # Perform one-way ANOVA
        result = stats.f_oneway(*[data['Points Gained'][data['Strategy'] == s] for s in data['Strategy'].unique()])

        # Display the ANOVA results
        print("One-way ANOVA results:")
        print(result)
        
        # Perform one-way ANOVA (if you haven't already)
        anova = sm.OLS.from_formula('data["Points Gained"] ~ data["Strategy"]', data=data).fit()

        # Perform Tukey-Kramer post-hoc test
        tukey = pairwise_tukeyhsd(data['Points Gained'], data['Strategy'])

        # Print the ANOVA results
        print("\nANOVA results:")
        print(anova.summary())

        # Print the Tukey-Kramer results
        print("\nTukey-Kramer post-hoc test:")
        print(tukey.summary())

    else: 
        result = stats.kruskal(results_00['negotiation_rounds'], results_01['negotiation_rounds'], results_02['negotiation_rounds'], results_11['negotiation_rounds'], results_12['negotiation_rounds'], results_22['negotiation_rounds'])
        # Display the Kruskal-Wallis results
        print("Kruskal-Wallis results:")
        print(result)
        
        # Perform Dunn's test for pairwise comparisons
        dunn_results = posthoc_dunn(data, val_col='Points Gained', group_col='Strategy')

        # Print the results
        print("\nDunn's test results:")
        print(dunn_results)


if __name__ == "__main__":
    main(sys.argv[1:])