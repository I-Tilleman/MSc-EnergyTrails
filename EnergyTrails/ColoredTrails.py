#!/usr/bin/env python3.10

# Main code for the Colored Trails game environment

import random
import logging, sys
import itertools
from tqdm import tqdm
from datetime import datetime 

class Game_ct:
    def print_board(self):
        for line in self.board:
            print(line)
        print(
            "0:",
            self.locations[0],
            self.chip_sets[0],
            "-",
            Game_ct.convert_code(self.chip_sets[0], self.bin_max),
        )
        print(
            "1:",
            self.locations[1],
            self.chip_sets[1],
            "-",
            Game_ct.convert_code(self.chip_sets[1], self.bin_max),
        )
    
    def print_stats(self, offer_count):
        print("the total offer count is", offer_count)
        print("Then for each goal and board you have the following number of options")
        for goal in range(len(self.valid_goals)):
            print("Goal", goal, ":")
            for board in range(self.number_of_boards):
                print("Board", board,":", len(self.board_info[goal][board]['list']))
                

    def print_boards(self):
        for board in self.boards:
            for line in board:
                print(line)
            print("\n")
        
    def get_goals(self, id):
        return self.locations[id]

    def get_chip_sets(self, id):
        return self.chip_sets[id]
    
    def get_bin_max(self):
        return self.bin_max

    def get_chip_difference(offer1, offer2, bin_max):
        bins1 = Game_ct.convert_code(offer1, bin_max)
        bins2 = Game_ct.convert_code(offer2, bin_max)
        for i in range(len(bins1)):
            bins1[i] -= bins2[i]
        return bins1

    def invert_code(offer, bin_max):
        out_array = Game_ct.convert_code(offer, bin_max)
        for i in range(len(bin_max)):
            out_array[i] = bin_max[i] - out_array[i]
        return Game_ct.convert_chips(out_array, bin_max)

    def convert_code(offer, bin_max):
        out_array = []
        for i in range(len(bin_max)):
            out_array.append(offer % (bin_max[i] + 1))
            offer = int(offer / (bin_max[i] + 1))
        return out_array
    
    # this converts a code to the chips YOU get if you place this offer, instead of what you offer to the other player 
    def convert_code_perspective(offer, bin_max):
        offer = Game_ct.invert_code(offer, bin_max)
        
        out_array = []
        for i in range(len(bin_max)):
            out_array.append(offer % (bin_max[i] + 1))
            offer = int(offer / (bin_max[i] + 1))
        return out_array

    def convert_chips(chips_array, bin_max):
        code = chips_array[len(chips_array) - 1]
        for i in range(len(chips_array) - 2, -1, -1):
            code = code * (bin_max[i] + 1) + chips_array[i]
        return code

    # ! figure out when this is used 
    def load_setting(self, board, chips1, chips2, location1, location2):
        self.board = board
        self.chips = [chips1, chips2]
        self.calculate_setting()
        self.locations = [location1, location2]

    def __init__(self, boards = 4, point_sharing = True, priorities = True):
        self.number_of_colors = 4
        self.number_of_chips_per_player = self.number_of_colors * boards # should be 16 in most cases 
        self.number_of_boards = boards # should be 4 in most cases 
        #size of the grid 
        self.m = 5
        self.n = 5
        
        self.point_sharing = point_sharing
        self.priorities = priorities
        
        # goal locations of players
        self.locations = [] 
        # the goal compositions of the trails of the players, goal composition is represented as single number to save space :)
        # a list of lists: [[playerAgoal1, playerAgoal2, playerAgoal3, playerAgoal4], [playerBgoal1, playerBgoal2, playerBgoal3, playerBgoal4]]
        self.goal_compositions = []
        # the number of the goal compositions of the players
        self.goal_composition_code = []
        # Initial sets of chips for both players, represented as arrays
        self.chips = []
        # Initial set of chips for both players, represented as codes
        self.chip_sets = []
        # Flips the offer to the perspective of the other player
        self.flip_array = []
        # Total numbers of chips for each color
        self.bin_max = []
        # The utility function that contains the utility for all possible goals
        self.utility_function = []
        # temporarily holds the trail list
        self.trail_list = []
        # stores the boards in the game 
        self.boards = []
        # stores info related to the boards
        self.board_info = []
        # stores the totals of the chips needed to complete each desire 
        self.chips_for_completion = []
        # stores the optimal trails for each board for completion 
        self.completion_distribution = [] 
        # seed for random things 
        self.seed = datetime.now().timestamp()
        # set random seed 
        random.seed(self.seed)
        # stores the offers placed by agents 
        self.offer_history = [[],[]]
        
        # self.valid_goals = [
        #     [[2, 2, 0, 0], [1, 1, 1, 0], [1, 1, 1, 1], [1, 1, 0, 0]],
        #     [[1, 1, 1, 1], [1, 1, 1, 0], [1, 1, 1, 0], [1, 1, 1, 0]],
        #     [[1, 2, 1, 0], [2, 2, 0, 0], [0, 0, 1, 1], [2, 1, 1, 0]],
        #     [[1, 1, 1, 0], [1, 1, 1, 1], [2, 2, 0, 0], [1, 2, 1, 0]],
        #     [[1, 2, 0, 1], [1, 2, 0, 1], [1, 2, 1, 0], [2, 2, 0, 0]],
        #     [[2, 2, 0, 0], [1, 1, 1, 1], [0, 1, 2, 1], [1, 1, 1, 1]]
        # ]
        
        self.valid_goals = [
            [[[1, 1, 1, 1], [1, 1, 1, 0], [1, 1, 1, 0], [1, 1, 1, 0]], [0]], # biology
            [[[2, 2, 0, 0], [1, 1, 1, 0], [1, 1, 1, 1], [1, 1, 0, 0]], [2]], # computing
            [[[1, 2, 0, 0], [2, 2, 0, 0], [1, 1, 1, 1], [1, 1, 1, 0]], [2]], # cantine 
            [[[1, 1, 1, 0], [1, 1, 1, 0], [1, 1, 1, 0], [1, 1, 1, 0]], [2]], # exam hall
            [[[1, 1, 1, 0], [1, 1, 1, 0], [1, 1, 1, 0], [1, 1, 1, 0]], [1]], # conference hall
            [[[1, 2, 1, 0], [1, 1, 1, 0], [1, 2, 1, 0], [1, 1, 1, 0]], [2]], # study hall
            [[[1, 1, 1, 1], [1, 1, 1, 1], [1, 0, 1, 2], [0, 0, 1, 1]], [2]], # observatory 
        ]
        

    # ensures that the chips of players somewhat relate to the chips on boards/the distribution of chips on boards 
    def get_random_board_color(self):
        i = random.randrange(len(self.unused_board_colors))
        n = int(self.unused_board_colors[i])

        return n

    # Initializes/distributes tiles and chips 
    def init(self, location_goal=False):
        
        self.unused_board_colors = ""
        self.boards = []
        self.location_goal = location_goal
        self.chips = [[0 for i in range(self.number_of_colors)] for j in range(2)]


        # Randomly initialize board(s)
        for _ in range(self.number_of_boards):
            self.board = [[0 for i in range(5)] for j in range(5)]
            for i in range(5):
                for j in range(5):
                    if i == 2 and j == 2:
                        self.board[i][j] = 0
                    else:
                        self.board[i][j] = random.randrange(self.number_of_colors)
                        self.unused_board_colors += str(self.board[i][j])
                
            self.boards.append(self.board)
        
        # Give players random set of chips
        for i in range(self.number_of_chips_per_player):
            self.chips[0][self.get_random_board_color()] += 1
            self.chips[1][self.get_random_board_color()] += 1
        
        self.calculate_setting()

    # Calculate and convert important variables based on tile nd chip distributions:
    # possible_offers, bin_max
    def calculate_setting(self):
        offer_count = 1
        self.bin_max = [0] * self.number_of_colors
        self.goal_compositions = [[0 for i in range(self.number_of_colors)] for j in range(2)]
        self.goal_composition_code = [[0 for i in range(self.number_of_colors)] for j in range(2)]
        self.chips_for_completion = [[0 for i in range(self.number_of_colors)] for j in range(len(self.valid_goals))]
        self.completion_distribution = [[] for k in range(len(self.valid_goals))]
        self.board_info = [[] for i in range(len(self.valid_goals))]
        self.utilities = [[] for i in range(len(self.valid_goals))]
        self.offer_count = 0

        # Calculate number of possible offers and bin_max
        for i in range(self.number_of_colors):
            self.bin_max[i] = self.chips[0][i] + self.chips[1][i]
            offer_count *= self.bin_max[i] + 1
        self.flip_array = [0] * offer_count
        for i in range(offer_count):
            self.flip_array[i] = Game_ct.invert_code(i, self.bin_max)
            
        # Convert the chips to numbers
        self.chip_sets = [
            Game_ct.convert_chips(self.chips[0], self.bin_max),
            Game_ct.convert_chips(self.chips[1], self.bin_max),
        ]
        
        # Set goal compositions of agents 
        if not self.location_goal:
            while self.goal_composition_code[0] == self.goal_composition_code[1]:
                self.goal_composition_code[0] = random.randint(0,len(self.valid_goals)-1)
                self.goal_composition_code[1] = random.randint(0,len(self.valid_goals)-1)
            
            self.goal_compositions[0] = self.valid_goals[self.goal_composition_code[0]]
            self.goal_compositions[1] = self.valid_goals[self.goal_composition_code[1]]
        self.offer_count = offer_count
                            
        # figure out the potential paths on the boards
        for goal in range(len(self.valid_goals)):
            self.path_walker(self.valid_goals[goal].copy(), goal)
                    
        # figure out the utility functions for all goals 
        for goal in range(len(self.valid_goals)):
            self.get_utility_function(offer_count, goal)
    
    # generates empty trail matrix for path_walker 
    def getEmptyTrailMatrix(self, trail):
        for row in range(self.m):
            trail.append([])
            for column in range(self.n):
                trail[row].append(0) 
        return trail
                    
    def path_walker(self, desires, goal):
        sx=2
        sy=2
        step=0
        for i in range(self.number_of_boards):
            trail = []
            grid=[]
            trailnr=0
            result=""
            bin_list=[]
            trail_list_lists=[]
            bonus=0
            all_tiles = [0,0,0,0]
            max_len = 5
            desires = self.valid_goals[goal][0][i] # sets the goal to the goal for the specific board you're considering here 
            debug = 0
            
            trail=self.getEmptyTrailMatrix(trail)
            
            # ensure that resulting path is not empty 
            error = True
            while error:
                error = False
                for row in range(self.n):
                    grid.append([])
                    for column in range(5): 
                        tile = random.randrange(1,5) #
                        grid[row].append(str(tile))
                        all_tiles[tile-1] +=1 
                all_tiles[int(grid[sx][sy])-1] -= 1 # remove the starting tile because it doesn't count for the desires 
                for i in range(4):
                    if desires[i] > all_tiles[i]:
                        error = True
                        grid.clear()
                        all_tiles=[0,0,0,0]
                debug +=1
                if debug > 20:
                    print("it was too hard to find a valid board")
                    break
                        
            # to be able to reference the original desires 
            og_desires = desires.copy()
            # to make sure it always gets past the first one 
            desires[int(grid[sx][sy])-1] += 1
            
            self.walk(sx,sy,grid,trail,step,result,desires, bonus, max_len)
            
            #remove duplicates
            self.trail_list= list(set(self.trail_list))
            
            # convert to list of lists 
            for x in self.trail_list:
                res = [int(b) for a,b in enumerate(str(x))]
                res.pop(0)
                trail_list_lists.append(res)
            
            # sort 
            trail_list_lists.sort(reverse = True, key=len)
            
            # convert to list of bins 
            for trail in trail_list_lists:
                bin_list.append([trail.count(1), trail.count(2), trail.count(3), trail.count(4)])
            
            # sort and remove duplicates 
            bin_list = sorted(bin_list)
            bin_list = [i for i, _ in itertools.groupby(bin_list)]
            
            # add all of these to the final list, because they work with the desires
            final_bins = bin_list.copy() 
            
            # the goal can be reached with an optimal path
            if og_desires in bin_list:
                repeat = False
                
            # an optimal path to the goal couldn't be found 
            else:
                bonus += 1
                max_len +=1 # can't use the bonus if the max length isn't increased # ? is the max length really necessary? Is it not just the desires + bonus? 
                
                trail=[]
                trail=self.getEmptyTrailMatrix(trail)
                self.walk(sx,sy,grid,trail,step,result,desires, bonus, max_len)
                
                # remove duplicates
                self.trail_list= list(set(self.trail_list))
                
                # convert to list 
                for x in self.trail_list:
                    res = [int(b) for a,b in enumerate(str(x))]
                    res.pop(0)
                    trail_list_lists.append(res)

                # sort 
                trail_list_lists.sort(reverse = True, key=len)
                
                for item in trail_list_lists:
                    works = True
                    for i in range(4):
                        if og_desires[i] > item.count(i+1):
                            works = False
                            break
                    
                    if works:
                        for _ in range(len(item)):
                            final_bins.append([item.count(1), item.count(2), item.count(3), item.count(4)])
                            item.pop()
                        repeat = False
            
            # make sure it's possible not to give anything to a trail
            final_bins.append([0,0,0,0])
            # sort
            final_bins = sorted(final_bins)
            # remove duplicates 
            final_bins = [i for i, _ in itertools.groupby(final_bins)]
            
            # calculate the number of chips necessary to fulfill all desires 
            for i in range(self.number_of_colors):
                self.chips_for_completion[goal][i] += final_bins[-1][i]
            
            # store final bins as reference for completion
            self.completion_distribution[goal].append(final_bins[-1])
            
            # store the possible routes that can be taken on this board
            self.board_info[goal].append({'board':i, 'list':final_bins})
            
            trail.clear()
            grid.clear()
            bin_list.clear()
            trail_list_lists.clear()
            self.trail_list.clear() 

    def walk(self,x,y,grid,trail,step,result,desires,bonus,max_len):
        step=step+1
        cont=True
        desire=desires.copy()
        
        #running off the board?
        if x<0 or x>self.n-1:
            cont=False
        if y<0 or y>self.m-1:
            cont=False
        #running in own trail?
        if cont and trail[y][x]>0:
            cont=False 
        #check if there's still a desired chip left in this trail
        if cont and desire[int(grid[y][x])-1] <= 0 and bonus > 1:
            print("were using bonus now")
        
        if cont and self.bin_max[int(grid[y][x])-1] <= 0:
            cont=False 
            
        # why can it be lower than 0
        if cont and desire[int(grid[y][x])-1] <= 0 and bonus == 0:
            cont=False
        
        
            
        if cont:
            #clear trail everything lower than value at (x,y)
            for i in range(0,self.m):
                for j in range(0,self.n):
                    if trail[i][j]>=step:
                        trail[i][j]=0
            
            trail[y][x]=step
            
            if desire[int(grid[y][x])-1] <= 0: 
                bonus = bonus - 1
                
            desire[int(grid[y][x])-1] = desire[int(grid[y][x])-1] -1

            result=result+grid[y][x]
            if step==max_len: 
                cont=False

            if len(result) > 1:
                self.trail_list.append(result)

            if cont:
                self.walk(x-1,y,grid,trail,step,result,desire, bonus, max_len)
                self.walk(x+1,y,grid,trail,step,result,desire, bonus, max_len)
                self.walk(x,y+1,grid,trail,step,result,desire, bonus, max_len)
                self.walk(x,y-1,grid,trail,step,result,desire, bonus, max_len)
    
    def get_utility_function(self, offer_count, goal):
        # create a utility list the length of the list of valid goals that has a dict for every possible offer for every goal 
        for offer in range(offer_count+1): # for every offer that can be made in this game
            self.utilities[goal].append({'offer_code': offer, 'bins': Game_ct.convert_code(offer, self.bin_max), 'bins_self': Game_ct.convert_code_perspective(offer, self.bin_max), 'max_utility':0, 'shared_score':0, 'suboffer':[], 'calculated': False})
        
        # set starting board to 0
        board = 0
        # create list of suboffers 
        suboffers = []
        
        #calculate all possible suboffers that can be made from the optimal distribution, anything not in here will always just be leftover chips 
        self.calculate_suboffers(self.chips_for_completion[goal].copy(), board, suboffers, goal, self.chips_for_completion[goal].copy())        

        self.utilities[goal] = sorted(self.utilities[goal], key=lambda x: x['max_utility'], reverse=True) # sort!
        
        # use the suboffers from the optimal distribution to calculate the scores for the remaining offers 
        for offer in range(offer_count):
            suboffers = []
            # check if the offer already has a utility > 0, if so just use that
            if next(item for item in self.utilities[goal] if item['offer_code'] == offer)['calculated']:
                continue # skip this item because the maximum for this one has already been calculated :)
            else: # if the offer doesn't have a utility > 0, find the highest one that fits inside this one and use the leftovers as leftover chips
                offer_item = next(item for item in self.utilities[goal] if item['offer_code'] == offer)
                
                for item in self.utilities[goal]:
                    
                    if all(x >= y for x,y in zip(offer_item['bins'], item['bins'])): # find the first offer in utilities that can be made with the current offer

                        if item['calculated']:
                            offer_item['suboffer'] = item['suboffer'][:self.number_of_boards] # append the suboffers - leftovers
                            offer_item['suboffer'].append([a - b for (a, b) in zip(offer_item['bins'], item['bins'])]) # append the leftovers you now have
                            offer_item['max_utility'], offer_item['shared_score'] = self.calculate_score(offer_item['suboffer'], goal) # calculate the new score and add it to the dictionary
                            break
        
        # sort utilities, now you have a full list of valid offers with the current board and chips for this goal
        self.utilities[goal] = sorted(self.utilities[goal], key=lambda x: x['offer_code']) # ! the standard is with reverse = True, you can also try it without
        
        
    def calculate_suboffers(self, suboffer_bin_max, board, suboffers, goal, bin_max):
        suboffer_count = 1
        suboffers = suboffers.copy()
        
        #check whether we've gone past all boards 
        if board < self.number_of_boards:
            # calculate the number of possible suboffers that can be made with this offer
            for i in range(self.number_of_colors):
                suboffer_count *= suboffer_bin_max[i] + 1
                        
            for suboffer in range(suboffer_count):
                suboffer = Game_ct.convert_code(suboffer, suboffer_bin_max)
                if board < self.number_of_boards:
                    if suboffer in self.board_info[goal][board]['list']: 
                                                
                        #add to current suboffer
                        suboffers.append(suboffer)
                        
                        #rerun this thing with the new bin_max and for the next board 
                        self.calculate_suboffers([a - b for (a, b) in zip(suboffer_bin_max, suboffer)], board+1, suboffers.copy(), goal, bin_max)
                        suboffers.pop()
        elif board is self.number_of_boards:
            
            suboffers.append([0, 0, 0, 0]) # to make sure the leftovers are at least represented, even if there are none lol
            
            score, shared_score = self.calculate_score(suboffers, goal) # this calculates the score without the leftovers in this offer
            
            # calculate totals in suboffer
            # convert totals to offer code
            
            # add the subtotals together to get the complete offer
            total_offer=[sum(item) for item in zip(*suboffers)]

            # get the offer code 
            offer = Game_ct.convert_chips(total_offer, self.bin_max)
            
            # prevents list index out of range
            if offer > self.offer_count:
                return
            
            if self.utilities[goal][offer]['max_utility'] <= score:
                self.utilities[goal][offer]['max_utility'] = score
                self.utilities[goal][offer]['shared_score'] = shared_score
                self.utilities[goal][offer]['suboffer'] = suboffers
                self.utilities[goal][offer]['calculated'] = True
            else:
                suboffers.pop()
    
    def calculate_score(self, offer, goal):
        score = 0
        shared_score = 0
        
        for i in range(self.number_of_boards+1):
            #leftover chips 
            if i is self.number_of_boards:
                score = score + (sum(offer[i])*50)
            #goals 
            else:
                try:
                    max = sum(sorted(self.board_info[goal][i]['list'], key=sum, reverse=True)[0])
                except IndexError:
                    max = 0
                
                if i is self.valid_goals[goal][1]:
                    if sum(offer[i]) is max:
                        score += 1000 
                        if self.point_sharing:
                            shared_score += 800 
                    elif sum(offer[i]) < max:
                        score = score + (sum(offer[i])*100)
                    continue
                
                if sum(offer[i]) is max: 
                    score += 500 # reaching a goal
                    if self.point_sharing:
                        shared_score += 250
                elif sum(offer[i]) < max:
                    score = score + (sum(offer[i])*100) # taking a step towards a goal 
                    
        return score, shared_score
