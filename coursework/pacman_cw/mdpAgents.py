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
        # First, make all grid elements that aren't walls blank.
        food = api.food(state)
        for i in range(len(food)):
            x, y = food[i][1], food[i][0]
            map_array[x][y] = 5

    def rewardConvergence(self, state):
        corners = api.corners(state)
        walls = api.walls(state)
        food = api.food(state)
        ghosts = api.ghosts(state)
        capsules = api.capsules(state)

        #Get max width and height
        maxWidth = self.getLayoutWidth(corners) - 1
        maxHeight = self.getLayoutHeight(corners) - 1

        gamma = 0.8                                                                   #common gamma value
        reward = -0.04

        for i in range(200):
            global map_array_upd
            map_array_upd = map_array                                                       # This will store the old values

            for i in range(maxWidth):
                for j in range(maxHeight):
                    if (i, j) not in walls and (i, j) not in ghosts and (i, j) not in capsules:
                        map_array_upd[i][j] = reward + gamma * self.mapUtility(i, j, map_array, 0)

    def mapUtility(self, x, y, map_used, pacman):
        # This function calculates the maximum expected utility of a coordinate on the initiated valueMap

        # initialise a dictionary to store utility values
        self.util_dict = {"n_util": 0.0, "s_util": 0.0, "e_util": 0.0, "w_util": 0.0}

        # valueMap should be a dictionary containing a list of values assigned to every grid
        self.map_used = map_used

        #north -> [x][y + 1]
        #south -> [x][y - 1]
        #east  -> [x+1][y]
        #west  -> [x-1][y]
        #stay  -> [x][y]

        # If North is not a wall, then multiply expected utility;
        # else multiply expected utility of staying in place
        # If the perpendicular directions are not walls, then multiply expected utility of those
        # else multiply expected utility of just staying in place

        #north
        if self.map_used[x][y + 1] != None:
            n_util = (0.8 * self.map_used[x][y + 1])
        else:
            n_util = (0.8 * self.map_used[x][y])

        #east
        if self.map_used[x+1][y] != None:
            n_util += (0.1 * self.map_used[x+1][y])
        else:
            n_util += (0.1 * self.map_used[x][y])

        #west
        if self.map_used[x-1][y] != None:
            n_util += (0.1 * self.map_used[x-1][y])
        else:
            n_util += (0.1 * self.map_used[x][y])

        self.util_dict["n_util"] = n_util



        # Repeat for the rest of the directions
        #south
        if self.map_used[x][y - 1] != None:
            s_util = (0.8 * self.map_used[x][y - 1])
        else:
            s_util = (0.8 * self.map_used[x][y])

        #east
        if self.map_used[x+1][y] != None:
            s_util += (0.1 * self.map_used[x+1][y])
        else:
            s_util += (0.1 * self.map_used[x][y])

        #west
        if self.map_used[x-1][y] != None:
            s_util += (0.1 * self.map_used[x-1][y])
        else:
            s_util += (0.1 * self.map_used[x][y])

        self.util_dict["s_util"] = s_util




        #east
        if self.map_used[x+1][y] != None:
            e_util = (0.8 * self.map_used[x+1][y])
        else:
            e_util = (0.8 * self.map_used[x][y])

        #north
        if self.map_used[x][y + 1] != None:
            e_util += (0.1 * self.map_used[x][y + 1])
        else:
            e_util += (0.1 * self.map_used[x][y])

        #south
        if self.map_used[x][y - 1] != None:
            e_util += (0.1 * self.map_used[x][y - 1])
        else:
            e_util += (0.1 * self.map_used[x][y])

        self.util_dict["e_util"] = e_util



        #west
        if self.map_used[x-1][y] != None:
            w_util = (0.8 * self.map_used[x-1][y])
        else:
            w_util = (0.8 * self.map_used[x][y])

        #north
        if self.map_used[x][y + 1] != None:
            w_util += (0.1 * self.map_used[x][y + 1])
        else:
            w_util += (0.1 * self.map_used[x][y])

        #south
        if self.map_used[x][y - 1] != None:
            w_util += (0.1 * self.map_used[x][y - 1])
        else:
            w_util += (0.1 * self.map_used[x][y])

        self.util_dict["w_util"] = w_util






        # Take the max value in the dictionary of stored utilities
        # Assign current grid MEU
        # Return updated valueMap that has transition values
        if pacman == 0:
            self.map_used[x-1][y] = max(self.util_dict.values())
            return self.map_used[x-1][y]
        else:
            # return the move with the highest MEU
            return self.util_dict.keys()[self.util_dict.values().index(max(self.util_dict.values()))]


    # For now I just move randomly
    def getAction(self, state):
        self.updateFoodInMap(state)
        self.displayMap()
        self.rewardConvergence(state)

        legal_moves = api.legalActions(state)
        pacman_loc = api.whereAmI(state)

        pacman_loc_x = pacman_loc[0]
        pacman_loc_y = pacman_loc[1]

        

        if self.mapUtility(pacman_loc_x, pacman_loc_y, map_array_upd, 1) == "n_util":
            return api.makeMove(Directions.NORTH, legal_moves)

        if self.mapUtility(pacman_loc_x, pacman_loc_y, map_array_upd, 1) == "s_util":
            return api.makeMove(Directions.SOUTH, legal_moves)

        if self.mapUtility(pacman_loc_x, pacman_loc_y, map_array_upd, 1) == "e_util":
            return api.makeMove(Directions.EAST, legal_moves)

        if self.mapUtility(pacman_loc_x, pacman_loc_y, map_array_upd, 1) == "w_util":
            return api.makeMove(Directions.WEST, legal_moves)



