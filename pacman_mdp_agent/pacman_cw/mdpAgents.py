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

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
         print "Running registerInitialState!"
         # Make a map of the right size
         self.makeMap(state)
         self.addWallsToMap(state)
         self.updateFoodInMap(state)

    # This is what gets run when the game ends.
    def final(self, state):
        print "Looks like I just died!"

    # Functions to get the height and the width of the grid.
    def getLayoutHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1

    def getLayoutWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1

    # Make a map by creating a grid of the right size
    def makeMap(self,state):
        global map_array

        corners = api.corners(state)
        height = self.getLayoutHeight(corners)
        width  = self.getLayoutWidth(corners)

        map_array = [[0]*width for i in range(height)]

    def displayMap(self):
        print('\n'.join(' '.join(map(str,sl)) for sl in map_array))
        print('\n')

    # Put every element in the list of wall elements into the map
    def addWallsToMap(self, state):
        walls = api.walls(state)
        for i in range(len(walls)):
            x, y = walls[i][1], walls[i][0]
            map_array[x][y] = None


    # Create a map with a current picture of the food that exists.
    def updateFoodInMap(self, state):
        food = api.food(state)
        for i in range(len(food)):
            x, y = food[i][1], food[i][0]
            map_array[x][y] = 5


    def updateCapsulesInMap(self, state):
        capsules = api.capsules(state)
        for i in range(len(capsules)):
            x, y = capsules[i][1], capsules[i][0]
            map_array[x][y] = 20

    def updateGhostsInMap(self, state):
        # First, make all grid elements that aren't walls blank.
        ghosts = api.ghosts(state)
        for i in range(len(ghosts)):
            x, y = int(ghosts[i][1]), int(ghosts[i][0])
            map_array[x][y] = -1

    def rewardConvergence(self, state):
        #Get max width and height
        corners = api.corners(state)
        maxWidth = self.getLayoutWidth(corners) - 1
        maxHeight = self.getLayoutHeight(corners) - 1


        iterations = 200
        while iterations > 0:
            global map_array_upd
            map_array_upd = map_array                                                       # This will store the old values

            food = api.food(state)
            walls = api.walls(state)
            ghosts = api.ghosts(state)

            for i in range(maxWidth):
                for j in range(maxHeight):
                    if (i,j) not in food and (i,j) not in walls and (i,j) not in ghosts:
                        map_array_upd[j][i] = self.mapUtility(state, j, i, map_array)

            iterations -= 1

    def mapUtility(self, state, x, y, map_used):
        # This function calculates the maximum expected utility of a coordinate on the initiated valueMap

        current = map_used[x][y]
        reward = -0.01
        gamma = 0.98

        corners = api.corners(state)
        h = corners[1][0] + 1
        w = corners[2][1] + 1

        #north -> [x][y + 1]
        #south -> [x][y - 1]
        #east  -> [x+1][y]
        #west  -> [x-1][y]
        #stay  -> [x][y]


        east = west = north = south = None


        if x < w - 1:
            east = map_used[x + 1][y]
        if x > 0:
            west = map_used[x - 1][y]
        if y < h - 1:
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
        self.updateFoodInMap(state)
        self.updateCapsulesInMap(state)
        self.updateGhostsInMap(state)
        self.rewardConvergence(state)
        #self.displayMap()

        pacman_loc = api.whereAmI(state)

        pacman_loc_x = pacman_loc[0]
        pacman_loc_y = pacman_loc[1]

        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        
        [scores, actions] = self.getActionScores(legal, map_array_upd, pacman_loc_x, pacman_loc_y)
        max_score_index = scores.index(max(scores))
        choice = actions[max_score_index]
        return api.makeMove(choice, legal)


