# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
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

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

class MDPAgent(Agent):
    def __init__(self):                                                            # Constructor: this gets run when we first invoke pacman.py
        name = "Pacman"

    def registerInitialState(self, state):
         self.makeMap(state)
         self.addWallsToMap(state)
         #self.displayMap()

    def getCorners(self, state):
        corners = api.corners(state)
        width = corners[1][0] + 1
        height = corners[2][1] + 1

        return [height, width]

    def makeMap(self,state):
        height, width = self.getCorners(state)

        global map_array
        map_array = [[0]*width for i in range(height)]

    def displayMap(self):
        print('\n'.join(' '.join(map(str,sl)) for sl in map_array))
        print('\n')

    def addWallsToMap(self, state):
        walls = api.walls(state)

        for i in range(len(walls)):
            x, y = walls[i][1], walls[i][0]
            map_array[x][y] = -1

    def updateFoodInMap(self, state, pacman_loc):
        food = api.food(state)

        for i in range(len(food)):
            #dist_to_food = int(util.manhattanDistance(pacman_loc,food[i]))

            x, y = food[i][1], food[i][0]
            map_array[x][y] = 5  #dist_to_food/2

    def updateCapsulesInMap(self, state, pacman_loc):
        capsules = api.capsules(state)

        for i in range(len(capsules)):
            #dist_to_capsule = int(util.manhattanDistance(pacman_loc,capsules[i])) 

            x, y = capsules[i][1], capsules[i][0]
            map_array[x][y] = 20 #dist_to_capsule/2

    def updateGhostsInMap(self, state, pacman_loc):
        ghosts = api.ghosts(state)

        for i in range(len(ghosts)):
            #dist_to_ghost = int(util.manhattanDistance(pacman_loc,ghosts[i]))

            x, y = int(ghosts[i][1]), int(ghosts[i][0])
            map_array[x][y] = -1#-3/dist_to_ghost

    def rewardConvergence(self, state):
        #Get max width and height
        height, width = self.getCorners(state)


        iterations = 200
        

        while iterations > 0:
            global map_array_last
            map_array_last = map_array

            food = api.food(state)
            walls = api.walls(state)
            ghosts = api.ghosts(state)

            for i in range(width):
                for j in range(height):
                    if (i,j) not in food and (i,j) not in walls and (i,j) not in ghosts:
                        map_array_last[j][i] = self.mapUtility(state, j, i, map_array)

            iterations -= 1

    def mapUtility(self, state, x, y, map_used):
        # This function calculates the maximum expected utility of a coordinate on the initiated valueMap

        current = map_used[x][y]
        reward = -0.01
        gamma = 0.98


        height, width = self.getCorners(state)

        east = west = north = south = None


        if x < width - 1:
            east = map_used[x + 1][y]
        if x > 0:
            west = map_used[x - 1][y]
        if y < height - 1:
            north = map_used[x][y + 1]
        if y > 0:
            south = map_used[x][y - 1]

        if east is None:
            east = -1
        if west is None:
            west = -1
        if north is None:
            north = -1
        if south is None:
            south = -1

        # region probabilities
        if north is not None:
            north_val = north * 0.8 + (east + west) * 0.1
        else:
            north_val = current
        if south is not None:
            south_val = south * 0.8 + (east + west) * 0.1
        else:
            south_val = current
        if east is not None:
            east_val = east * 0.8 + (north + south) * 0.1
        else:
            east_val = current
        if west is not None:
            west_val = west * 0.8 + (north + south) * 0.1
        else:
            west_val = current

        # endregion
        all_values = [north_val, south_val, east_val, west_val]
        max_val = max(all_values)

        return reward + gamma * max_val


    def getActionScores(self, legal, pacman_map, x, y):
        scores = []
        actions = []
        for action in legal:
            value = None
            if action is Directions.NORTH:
                value = pacman_map[y + 1][x]
            elif action is Directions.SOUTH:
                value = pacman_map[y - 1][x]
            elif action is Directions.EAST:
                value = pacman_map[y][x + 1]
            elif action is Directions.WEST:
                value = pacman_map[y][x - 1]
            if value is not None:
                scores.append(value)
                actions.append(action)

        return [scores, actions]

    # For now I just move randomly
    def getAction(self, state):
        pacman_loc = api.whereAmI(state)

        pacman_loc_x = pacman_loc[0]
        pacman_loc_y = pacman_loc[1]

        self.updateFoodInMap(state, pacman_loc)
        self.updateCapsulesInMap(state, pacman_loc)
        self.updateGhostsInMap(state, pacman_loc)
        self.rewardConvergence(state)

        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        
        [scores, actions] = self.getActionScores(legal, map_array_last, pacman_loc_x, pacman_loc_y)
        return api.makeMove(actions[scores.index(max(scores))], legal)