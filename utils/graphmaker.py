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
from datetime import datetime 
import errno 
import csv
import json

### VARIABLES STORED IN RESULTS ### 
# total = total number of negotiations
# accepted = the number of accepts in all negotiations
# scores = the gains the players got in each negotiations 
# avg_gains = the average gain of the players over time 
# scores_accepted = the score gain when the offer was accepted
# score_diff = score differences betwen players in each negotiation 
# avg_diff = the avg difference between scores over time 
# negotiation_rounds = the number of negotiation rounds in each negotiation 

def main(argument):
    if argument[0] == 'final':
        final()
        return
    
    file = 'outfile-' + argument[0]
    suffix = argument[0]
    
    with open(file, 'rb') as fp:
        results = pickle.load(fp)
    
    print("This test was run", results['total'], "times")
    print("Of which", results['accepted'].count(1), "negotiations were successful, which is", str(int((results['accepted'].count(1)/results['total'])*100))+"%")
    print("On average, the players of the game gained", sum(results['scores'])/results['total'], "points")
    print("On average, the players negotiated for", sum(results['negotiation_rounds'])/results['total'], "rounds")
    
    if int(argument[0][0]) != 0:
        print("Player A ended up with the correct goal", ([1 for x,y in zip(results['goal_b'], results['beliefs_a']) if np.argmax(y[-1]) == x].count(1)/results['total'])*100 , "% of the time")
        
    if int(argument[0][1]) != 0:
        print("Player B ended up with the correct goal", ([1 for x,y in zip(results['goal_a'], results['beliefs_b']) if np.argmax(y[-1]) == x].count(1)/results['total'])*100 , "% of the time")

    # # avg gains
    # plt.plot(results['avg_gains'])
    # plt.savefig('foo1.pdf')
    # plt.clf()
    
    # # gains 
    # plt.plot(results['scores'])
    # plt.savefig('foo2.pdf')
    # plt.clf()
    
    # # avg difference between player socres 
    # plt.plot(results['avg_diff'])
    # plt.savefig('foo4.pdf')
    # plt.clf()
    
    # # neg. rounds 
    # plt.plot(results['negotiation_rounds'])
    # plt.savefig('foo5.pdf')
    # plt.clf()

def final():

    # 4 boards, yesps
    with open('outfile-00-temp', 'rb') as fp:
        results_00_yesps = pickle.load(fp)
    with open('outfile-01-temp', 'rb') as fp:
        results_01_yesps = pickle.load(fp)
    with open('outfile-02-temp', 'rb') as fp:
        results_02_yesps = pickle.load(fp)
    with open('outfile-11-temp', 'rb') as fp:
        results_11_yesps = pickle.load(fp)
    with open('outfile-12-temp', 'rb') as fp:
        results_12_yesps = pickle.load(fp)
    with open('outfile-22-temp', 'rb') as fp:
        results_22_yesps = pickle.load(fp)

    four_yesps = [results_00_yesps, results_01_yesps, results_02_yesps, results_11_yesps, results_12_yesps, results_22_yesps]

    # 4 boards, nops
    with open('outfile-00_nops-temp', 'rb') as fp:
        results_00_nops = pickle.load(fp)
    with open('outfile-01_nops-temp', 'rb') as fp:
        results_01_nops = pickle.load(fp)
    with open('outfile-02_nops-temp', 'rb') as fp:
        results_02_nops = pickle.load(fp)
    with open('outfile-11_nops-temp', 'rb') as fp:
       results_11_nops = pickle.load(fp)
    with open('outfile-12_nops-temp', 'rb') as fp:
        results_12_nops = pickle.load(fp)
    with open('outfile-22_nops-temp', 'rb') as fp:
        results_22_nops = pickle.load(fp)

    four_nops = [results_00_nops, results_01_nops, results_02_nops, results_11_nops, results_12_nops, results_22_nops]


    # 2 boards, yesps
    with open('outfile-00_2_yesps-temp', 'rb') as fp:
        results_00_2_yesps = pickle.load(fp)
    with open('outfile-01_2_yesps-temp', 'rb') as fp:
        results_01_2_yesps = pickle.load(fp)
    with open('outfile-02_2_yesps-temp', 'rb') as fp:
        results_02_2_yesps = pickle.load(fp)
    with open('outfile-11_2_yesps-temp', 'rb') as fp:
        results_11_2_yesps = pickle.load(fp)
    with open('outfile-12_2_yesps-temp', 'rb') as fp:
        results_12_2_yesps = pickle.load(fp)
    with open('outfile-22_2_yesps-temp', 'rb') as fp:
        results_22_2_yesps = pickle.load(fp)
    two_yesps = [results_00_2_yesps, results_01_2_yesps, results_02_2_yesps, results_11_2_yesps, results_12_2_yesps, results_22_2_yesps]

   
    # 2 boards, nops
    with open('outfile-00_2_nops-temp', 'rb') as fp:
        results_00_2_nops = pickle.load(fp)
    with open('outfile-01_2_nops-temp', 'rb') as fp:
        results_01_2_nops = pickle.load(fp)
    with open('outfile-02_2_nops-temp', 'rb') as fp:
        results_02_2_nops = pickle.load(fp)
    with open('outfile-11_2_nops-temp', 'rb') as fp:
        results_11_2_nops = pickle.load(fp)
    with open('outfile-12_2_nops-temp', 'rb') as fp:
        results_12_2_nops = pickle.load(fp)
    with open('outfile-22_2_nops-temp', 'rb') as fp:
        results_22_2_nops = pickle.load(fp)
    two_nops = [results_00_2_nops, results_01_2_nops, results_02_2_nops, results_11_2_nops, results_12_2_nops, results_22_2_nops]


    situations = ['0 vs 0', '0 vs 1', '0 vs 2', '1 vs 1', '1 vs 2', '2 vs 2']
    situations_4_nops = ['0 vs 0', '0 vs 1', '0 vs 2', '1 vs 2', '2 vs 2']

    all_results = [four_yesps, four_nops, two_yesps, two_nops]
    all_situations = ["4_yesps", "4_nops", "2_yesps", "2_nops"]

    for condition, situation in zip(all_results, all_situations):
        for result in condition:
        #enumerated loop, if negotiation_rounds is 25 then accepted is 0
            for i, x in enumerate(result['negotiation_rounds']):
                if x == 25:
                    result['accepted'].insert(i, 0)
                    #result['accepted'][i] = 0 #this should insert rather than just casting it to that index
                    result['scores'].insert(i, 0)

    four_yesps_len = 125
    for data in four_yesps:
        for key, value in data.items():
            if isinstance(value, list):  # Check if the value is a listelements
               data[key] = value[-four_yesps_len:]  # Slice the last 2  for lists
            else:
               data[key] = value  # Keep integers as they are

        if len(data['negotiation_rounds']) == four_yesps_len:
            data['total'] = four_yesps_len

    four_nops_len = 125

    for data in four_nops:
        for key, value in data.items():
            if isinstance(value, list):  # Check if the value is a list
                data[key] = value[-four_nops_len:]  # Slice the last 2 elements for lists
            else:
                data[key] = value  # Keep integers as they are

        if len(data['negotiation_rounds']) == four_nops_len:
            data['total'] = four_nops_len

    two_yesps_len = 600
    for data in two_yesps:
        for key, value in data.items():
            if isinstance(value, list):  # Check if the value is a list
               data[key] = value[-two_yesps_len:]  # Slice the last 2 elements for lists
            else:
               data[key] = value  # Keep integers as they are

        if len(data['negotiation_rounds']) == two_yesps_len:
            data['total'] = two_yesps_len

    two_nops_len = 600
    for data in two_nops:
        for key, value in data.items():
            if isinstance(value, list):  # Check if the value is a list
               data[key] = value[-two_nops_len:]  # Slice the last 2 elements for lists
            else:
               data[key] = value  # Keep integers as they are

        if len(data['negotiation_rounds']) == two_nops_len:
            data['total'] = two_nops_len
    
    
    for results, situation in zip(all_results, all_situations):
        print(situation)
        for result in results:
            print("This test was run", len(result['negotiation_rounds']), result['total'], len(result['accepted']), "times")
        print("")

    # make folders for the graphs 

    today = datetime.now()

    try:
        os.mkdir("graphs/"+today.strftime('%Y%m%d'))
    except OSError as e: 
        if e.errno != errno.EEXIST:
            raise

    try:
        os.mkdir("graphs/"+today.strftime('%Y%m%d')+"/4_yesps")
    except OSError as e: 
        if e.errno != errno.EEXIST:
            raise

    try:
        os.mkdir("graphs/"+today.strftime('%Y%m%d')+"/4_nops")
    except OSError as e: 
        if e.errno != errno.EEXIST:
            raise

    try:
        os.mkdir("graphs/"+today.strftime('%Y%m%d')+"/2_yesps")
    except OSError as e: 
        if e.errno != errno.EEXIST:
            raise

    try:
        os.mkdir("graphs/"+today.strftime('%Y%m%d')+"/2_nops")
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


    colors = ['red', 'blue', 'green', 'purple']

    # acceptance rate 

    acceptance_rate = []

    for results, situation in zip(all_results, all_situations):

        for result in results:
            acceptance_rate.append((result['accepted'].count(1)/result['total'])*100)

        fig, ax = plt.subplots()
        ax.bar(situations, acceptance_rate)
        ax.set_ylabel('Acceptance Rate in %')
        ax.set_title('Acceptance Rate of Negotiations')
        plt.ylim(0,110)
        
        plt.savefig("graphs/"+ today.strftime('%Y%m%d') + '/' + situation +'/acceptance_rate.pdf', dpi=300, transparent=True)
        
        plt.clf()

        acceptance_rate.clear()

    # average gains

    avg_gains = []
    sem = []

    for results, situation in zip(all_results, all_situations):

        for result in results:
            avg_gains.append(np.mean(result['scores']))
            sem.append(np.std(result['scores'], ddof=1) / np.sqrt(len(result['scores'])))
            
        fig, ax = plt.subplots()
        bars = ax.bar(situations, avg_gains, yerr=sem)
        ax.set_ylabel('Number of points gained')
        ax.set_title('Mean score increase after negotiating')
        plt.ylim(0,150)

        # Create the lines at the end of the error bars
        for bar, error in zip(bars, sem):
            x = bar.get_x() + bar.get_width() / 2
            ax.plot([x, x], [bar.get_height() + error, bar.get_height() - error], color='black', linewidth=2, marker='_', markersize=10, label='Error')
        
        plt.savefig("graphs/"+ today.strftime('%Y%m%d') + '/' + situation +'/points_gained.pdf', dpi=300, transparent=True)
        
        plt.clf()
        avg_gains.clear()
        sem.clear()


    # avg gains but only when accepted

    avg_gains_corr = []
    sem = []
    for results, situation in zip(all_results, all_situations):

        for result in results:
            avg_gains_corr.append(np.mean([x for x,y in zip(result['scores'], result['accepted']) if y == 1]))
            sem.append(np.std([x for x,y in zip(result['scores'], result['accepted']) if y == 1], ddof=1) / np.sqrt(len([x for x,y in zip(result['scores'], result['accepted']) if y == 1])))
        
        fig, ax = plt.subplots()
        bars = ax.bar(situations, avg_gains_corr, yerr=sem)
        ax.set_ylabel('Number of points gained')
        ax.set_title('Mean score increase after successful negotiation')
        plt.ylim(0,250)

        for bar, error in zip(bars, sem):
            x = bar.get_x() + bar.get_width() / 2
            ax.plot([x, x], [bar.get_height() + error, bar.get_height() - error], color='black', linewidth=2, marker='_', markersize=10, label='Error')

        plt.savefig("graphs/"+ today.strftime('%Y%m%d') + '/' + situation +'/points_gained_corr.pdf', dpi=300, transparent=True)
        plt.clf()
        avg_gains_corr.clear()
        sem.clear()
    
    plt.clf()

    # negotiation rounds but without timeouts 

    
    neg_rounds = []
    std_neg_rounds = []
    sem = []

    for results, situation in zip(all_results, all_situations):

        for result in results:
            neg_rounds.append(np.mean(list(filter(lambda x: x != 25, result['negotiation_rounds']))))
            sem.append(np.std(list(filter(lambda x: x != 25, result['negotiation_rounds'])), ddof=1) / np.sqrt(len(list(filter(lambda x: x != 25, result['negotiation_rounds'])))))

        fig, ax = plt.subplots()
        bars = ax.bar(situations, neg_rounds, yerr=sem)
        ax.set_ylabel('Number of rounds')
        ax.set_title('Mean number of negotiation rounds')
        plt.ylim(0,15)
            
        for bar, error in zip(bars, sem):
            x = bar.get_x() + bar.get_width() / 2
            ax.plot([x, x], [bar.get_height() + error, bar.get_height() - error], color='black', linewidth=2, marker='_', markersize=10, label='Error')

            
        plt.savefig("graphs/"+ today.strftime('%Y%m%d') + '/' + situation +'/neg_rounds_corr.pdf', dpi=300, transparent=True)
        plt.clf()
        neg_rounds.clear()


    # time-out rate 

    time_outs = []

    for results, situation in zip(all_results, all_situations):

        for result in results:
            time_outs.append((result['negotiation_rounds'].count(25)/result['total'])*100)


        fig, ax = plt.subplots()
        ax.bar(situations, time_outs)
        ax.set_ylabel('Time-out rate in %')
        plt.ylim(0,110)
        ax.set_title('Time-out rate')
            
        plt.savefig("graphs/"+ today.strftime('%Y%m%d') + '/' + situation +'/time_outs.pdf', dpi=300, transparent=True)
        plt.clf()
        time_outs.clear()
    
    # belief corectness 

    goal_start = []
    goal_opp = []
    for results, situation in zip(all_results, all_situations):

        goal_start = [0, 0, 0, ([1 for x,y in zip(results[3]['goal_b'], results[3]['beliefs_a']) if np.argmax(y[-1]) == x].count(1)/results[3]['total'])*100, ([1 for x,y in zip(results[4]['goal_b'], results[4]['beliefs_a']) if np.argmax(y[-1]) == x].count(1)/results[4]['total'])*100, ([1 for x,y in zip(results[5]['goal_b'], results[5]['beliefs_a']) if np.argmax(y[-1]) == x].count(1)/results[5]['total'])*100]
        goal_opp = [0, ([1 for x,y in zip(results[1]['goal_a'], results[1]['beliefs_b']) if np.argmax(y[-1]) == x].count(1)/results[1]['total'])*100, ([1 for x,y in zip(results[2]['goal_a'], results[2]['beliefs_b']) if np.argmax(y[-1]) == x].count(1)/results[2]['total'])*100, ([1 for x,y in zip(results[3]['goal_a'], results[3]['beliefs_b']) if np.argmax(y[-1]) == x].count(1)/results[3]['total'])*100, ([1 for x,y in zip(results[4]['goal_a'], results[4]['beliefs_b']) if np.argmax(y[-1]) == x].count(1)/results[4]['total'])*100,([1 for x,y in zip(results[5]['goal_a'], results[5]['beliefs_b']) if np.argmax(y[-1]) == x].count(1)/results[5]['total'])*100]


        width = 0.4
        x = np.arange(6)
        fig, ax = plt.subplots()
        ax.bar(x-0.2, goal_start, width)
        ax.bar(x+0.2, goal_opp, width)
        plt.xticks(x, situations)
        ax.set_ylabel('% Correct opponent goal belief')
        ax.set_title('Correct belief')
        plt.ylim(0,110)
            
        plt.savefig("graphs/"+ today.strftime('%Y%m%d') + '/' + situation +'/beliefs.pdf', dpi=300, transparent=True)
        plt.clf()

    plt.close("all")
    

    
if __name__ == "__main__":
    
    mpl.rcParams['axes.prop_cycle'] = cycler(color=['#123EB7', '#0A8754', 'b', 'y'])
    mpl.rcParams["figure.facecolor"] = 'white'
    mpl.rcParams["axes.facecolor"] = 'white'
    mpl.rcParams["savefig.facecolor"] = 'white'

    main(sys.argv[1:])