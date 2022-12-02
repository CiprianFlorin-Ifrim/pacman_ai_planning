#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------LICENSE-------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------STUDENT INFO----------------------------------------------------------------------------------------------
# Student Name: Ciprian-Florin Ifrim
# Student Number: 21202592
# Date: 02/12/2022

#-------------------------------------------------------------------------------------REFERENCES & RESEARCH-----------------------------------------------------------------------------------------
# Note: Coursework project code for KCL 6CCS3AIN Module - AI Decision Making and Planning
# References: 
#		Article: https://leyankoh.wordpress.com/2017/12/14/an-mdp-solver-for-pacman-to-navigate-a-nondeterministic-environment/
#		Article: https://prateek-mishra.medium.com/markovian-pac-man-8dd212c5a35c
#		GitHub: https://github.com/leyankoh/pacman-mdp-solver/blob/master/mdpAgents.py (specifically lines: 229-238)
#		GitHub: https://github.com/danilo-archive/pacman-mdp-agent/blob/main/mdpAgents.py (specifically lines: 60-76)

#-----------------------------------------------------------------------------------BERKELEY LICENSE STATEMENT--------------------------------------------------------------------------------------
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).
# The agent here is was written by Simon Parsons, based on the code in pacmanAgents.py

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------LIBRARIES------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
from pacman import Directions
from game import Agent
import api
import random
import game
import util

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------MDP AGENT CLASS---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class MDPAgent(Agent):
	def __init__(self):                                                                           # constructor: this gets run when we first invoke pacman.py
		name = "Pacman"                                                                           # set pacman name

#----------------------------------------------------------------------------------COMPUTE WIDTH AND HEIGHT OF THE MAPO-----------------------------------------------------------------------------
	def getCorners(self, state): 
		corners = api.corners(state)                                                              # get states of corners from the API                                           
 
		width = corners[1][0] + 1                                                                 # compute width
		height = corners[2][1] + 1                                                                # compute height

		return [width, height]                                                                    # return the two values


#----------------------------------------------------------------------------------------CREATE GAME MAP--------------------------------------------------------------------------------------------
	def makeMap(self,state):
		[width, height] = self.getCorners(state)                                                  # get width and height of the game map

		map_array = [[0]*width for i in range(height)]                                            # create 2 dimensional array (list of lists) based on width and height
		return map_array                                                                          # return map

#--------------------------------------------------------------------------------------DEFINE MAP WALL AREA-----------------------------------------------------------------------------------------
	def addWallsToMap(self, state, game_map):
		REWARD_WALL_S = -1                                                                        # reward for wall spaces - heavily optimised for smallGrid layouts
		REWARD_WALL_L = 0                                                                         # reward for wall spaces - heavily optimised for mediumClassic layouts

		walls_state = api.walls(state)                                                            # get state of walls from the API
		walls_count = len(walls_state)                                                            # find how many wall coordiantes sets are available - check if the map is small or large

		for i in range(walls_count):                                                              # iterate through all wall sets of coordinates
			x, y = walls_state[i][1], walls_state[i][0]                                           # get x and y of wall coordinates

			if walls_count < 50: game_map[x][y] = REWARD_WALL_S                                   # if the map has less than 50 wall coordinate sets, then use the small map wall reward
			else: game_map[x][y] = REWARD_WALL_L                                                  # else if the map has more than 50 wall coordinate sets, then use the large map wall reward

		return game_map                                                                           # return the updated game map

#-------------------------------------------------------------------------------------DEFINE FOOD REWARD SPACES-------------------------------------------------------------------------------------
	def updateFoodInMap(self, state, game_map):
		REWARD_FOOD   = 6                                                                         # reward for food spaces - heavily optimised for smallGrid/mediumClassic layouts
		food = api.food(state)                                                                    # get food states from the API

		for i in range(len(food)):                                                                # iterate through all food sets of coordinates available
			x, y = food[i][1], food[i][0]                                                         # get x and y of food coordinates
			game_map[x][y] =  REWARD_FOOD                                                         # set the reward for current x and y

		return game_map                                                                           # return the updated game map

#------------------------------------------------------------------------------------DEFINE CAPSULES REWARD SPACES----------------------------------------------------------------------------------
	def updateCapsulesInMap(self, state, pacman_loc, game_map):
		REWARD_CAPS = 1                                                                           # reward for capsule location
		capsules = api.capsules(state)                                                            # get capsule states

		for i in range(len(capsules)):                                                            # loop through all capsule coordinates available                                   
			dist_to_capsule = int(util.manhattanDistance(pacman_loc,capsules[i]))                 # calculate distance to capsules from pacman

			x, y = capsules[i][1], capsules[i][0]                                                 # get x and y of capsule coordinates
			game_map[x][y] = dist_to_capsule/REWARD_CAPS                                          # set a reward the distance to the capsule - the further away the bigger the reward

		return game_map                                                                           # return the updated game map

#--------------------------------------------------------------------------------------DEFINE GHOST REWARD SPACES-----------------------------------------------------------------------------------
	def updateGhostsInMap(self, state, pacman_loc, game_map):
		REWARD_GHOST = -2                                                                         # reward for ghost location
		ghost_states = api.ghostStates(state)                                                     # get ghost states

		for i in range(len(ghost_states)):                                                        # loop through all ghost coordinates available
			dist_to_ghost = int(util.manhattanDistance(pacman_loc,ghost_states[i][0]))            # calculate distance to ghosts from pacman
			x, y = int(ghost_states[i][0][1]), int(ghost_states[i][0][0])                         # get x and y of ghosts coordinates

			if ghost_states[i][1] == 1:                                                           # if the ghost is edible then:
				game_map[x][y] = dist_to_ghost                                                    # set a reward the distance to the ghost - the further away the bigger the reward
			else:
				game_map[x][y] = REWARD_GHOST/dist_to_ghost                                       # else if the ghost is not edible, add to map the reward divided by the pacman distance to ghost

		return game_map                                                                           # return the updated map

#----------------------------------------------------------------------------------BELLMAN REWARD CONVERGENCE FUNCTION------------------------------------------------------------------------------		   
	def rewardConvergence(self, state, game_map):
		CONV_ITERS = 100                                                                          # set value for the number of loops to compute

		[width, height] = self.getCorners(state)                                                  # get width and height of the game map

		for k in range(0, CONV_ITERS):                                                            # perform value convergence based on the given number of loops
			map_array_last = game_map                                                             # this will store the old values of the map
			food, walls, ghosts = api.food(state), api.walls(state), api.ghosts(state)            # get API states for food, walls and ghosts

			# loop through the width and height set coordinates of the map
			for i in range(width):                                                              
				for j in range(height): 
					if (i,j) not in food and (i,j) not in walls and (i,j) not in ghosts:          # for all (x,y) coordinates from the map not present in food/walls/ghosts, perform utility update
						game_map[j][i] = self.mapUtility(state, j, i, map_array_last)             # update the new map with the computed values

		return game_map                                                                           # return the updated map

#--------------------------------------------------------------------------------------BELLMAN UTILITY PER MAP SPACE--------------------------------------------------------------------------------
	def mapUtility(self, state, x, y, map_used):
		REWARD_EMPTY = -0.004                                                                     # reward for empty spaces - heavily optimised for smallGrid/mediumClassic layouts
		UTILITY_VAL  = 0.65                                                                       # gamma value for the Bellaman equation - heavily optimised for smallGrid/mediumClassic layouts
		FRONT_PROB   = 0.8                                                                        # hardcoded probability for front movement in the Bellman function
		SIDES_PROB   = 0.1                                                                        # hardcoded probability for side movement in the Bellman function

		[width, height] = self.getCorners(state)                                                  # get width and height of the game map

		dirs = [REWARD_EMPTY] * 4                                                                 # empty list for east, west, north, south
		vals = [x, -height + 1, x + 1, y,   x, 0, x-1, y,   
		         y, -width + 1, x, y + 1,   y, 0, x, y-1]                                         # variables needed for the comparison and value acquisition

		for i in range(0, 16, 4):                                                                 # for loop with 4 iterations, range sequence of every 4 values
			if vals[i] > vals[i+1]: dirs[int(i/4)] = map_used[vals[i+2]][vals[i+3]]               # get reward of the speicific x and y and store it in the dirs list

		pi = [0] * 4                                                                              # create empty list to store the utility of all 4 moves (north, east, south, west)
		for i in range(4):
			if i <= 1: pi[i] = dirs[i] * FRONT_PROB + (dirs[2] + dirs[3]) * SIDES_PROB            # east * 0.8 + (north + south) * 0.1 / west * 0.8 + (north + south) * 0.1
			else:      pi[i] = dirs[i] * FRONT_PROB + (dirs[0] + dirs[1]) * SIDES_PROB            # north * 0.8 + (east + west) * 0.1 / south * 0.8 + (east + west) * 0.1

		return REWARD_EMPTY + UTILITY_VAL * max(pi)                                               # return the Bellman equation value for the specific x and y

#-----------------------------------------------------------------------------------------GET LEGAL ACTIONS SCORES----------------------------------------------------------------------------------
	def getActionScores(self, legal, pacman_map, x, y):
		scores, actions = [], []                                                                  # create empty lists for the scores and actions available
		for action in legal:                                                                      # loop through all legal actions
			if action is Directions.NORTH:                                                        # if the direction is north then get that value
				value = pacman_map[y + 1][x]                                                      # add map value to the list for north movement
			elif action is Directions.SOUTH:                                                      # if the direction is south then get that value                   
				value = pacman_map[y - 1][x]                                                      # add map value to the list for south movement
			elif action is Directions.EAST:                                                       # if the direction is east then get that value                     
				value = pacman_map[y][x + 1]                                                      # add map value to the list for east movement
			elif action is Directions.WEST:                                                       # if the direction is west then get that value                        
				value = pacman_map[y][x - 1]                                                      # add map value to the list for west movement
 
			scores.append(value)                                                                  # for every iteration append the value to the list
			actions.append(action)                                                                # for every iteration append the score to the list

		return [scores, actions]                                                                  # return the 2 lists

#------------------------------------------------------------------------------PERFORM ACTION BASED ON MAP UTILITY AND MOVE SCORE-------------------------------------------------------------------
	def getAction(self, state):
		FIRST_FRAME   = 1                                                                         # first game frame constant - needed to only run map creation once
		if FIRST_FRAME > 0:                                                                       # if the first frame has not happened then proceed
			game_map = self.makeMap(state)                                                        # generate game map based on api state
			game_map = self.addWallsToMap(state, game_map)                                        # add walls to map based on api state
			FIRST_FRAME -= 1                                                                      # change the first frame to 0 to stop the event from repeating

		pacman_loc = api.whereAmI(state)                                                          # get pacman location x and y as list from the api
		game_map = self.updateFoodInMap(state, game_map)										  # call function that updates rewards for the food available in the map
		game_map = self.updateCapsulesInMap(state, pacman_loc, game_map)                          # call function that updates rewards for the capsules available based on pacman's distance to them
		game_map = self.updateGhostsInMap(state, pacman_loc, game_map)                            # call function that updates the rewards for ghosts dependant on pacman distance and if/not edible
		game_map = self.rewardConvergence(state, game_map)                                        # call function to update all map spaces available by using value iteration for convergence

		legal = api.legalActions(state)                                                           # get list of all possible moves based on the api state
		if Directions.STOP in legal:legal.remove(Directions.STOP)                                 # remove stop from the moves if it exists
		
		[scores, actions] = self.getActionScores(legal, game_map, pacman_loc[0], pacman_loc[1])   # call function that calculates the score of all the available moves
		return api.makeMove(actions[scores.index(max(scores))], legal)                            # have pacman perform the best legal move based on calculated scores
