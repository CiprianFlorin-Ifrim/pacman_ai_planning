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
	def __init__(self):
		name = "Pacman"

	def registerInitialState(self, state):
		 self.makeMap(state)
		 self.addWallsToMap(state)

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

	def makeMap(self,state):
		global map_array

		corners = api.corners(state)
		height = self.getLayoutHeight(corners)
		width  = self.getLayoutWidth(corners)

		map_array = [[0]*width for i in range(height)]

	def addWallsToMap(self, state):
		walls = api.walls(state)
		for i in range(len(walls)):
			x, y = walls[i][1], walls[i][0]
			map_array[x][y] = -1

	def updateFoodInMap(self, state, pacman_loc):
		food = api.food(state)

		for i in range(len(food)):
			dist_to_food = int(util.manhattanDistance(pacman_loc,food[i]))

			x, y = food[i][1], food[i][0]
			map_array[x][y] =  5#1

	def updateCapsulesInMap(self, state, pacman_loc):
		capsules = api.capsules(state)

		for i in range(len(capsules)):
			dist_to_capsule = int(util.manhattanDistance(pacman_loc,capsules[i])) 

			x, y = capsules[i][1], capsules[i][0]
			map_array[x][y] = 1   #dist_to_capsule/12

	def updateGhostsInMap(self, state, pacman_loc):
		ghost_states = api.ghostStates(state)

		for i in range(len(ghost_states)):
			dist_to_ghost = int(util.manhattanDistance(pacman_loc,ghost_states[i][0]))
			x, y = int(ghost_states[i][0][1]), int(ghost_states[i][0][0])

			if ghost_states[i][1] == 1:
				map_array[x][y] = dist_to_ghost
			else:
				map_array[x][y] = -1#-3/dist_to_ghost
		   
	def rewardConvergence(self, state):
		corners = api.corners(state)
		width = self.getLayoutWidth(corners) - 1
		height = self.getLayoutHeight(corners) - 1

		for k in range(0, 100):
			map_array_last = map_array                                                       # This will store the old values

			food = api.food(state)
			walls = api.walls(state)
			ghosts = api.ghosts(state)
			capsules = api.capsules(state)

			for i in range(width):
				for j in range(height):
					if (i,j) not in food and (i,j) not in walls and (i,j) not in ghosts:
						map_array[j][i] = self.mapUtility(state, j, i, map_array_last)



	def mapUtility(self, state, x, y, map_used):
		reward = -0.01
		gamma = 0.65

		corners = api.corners(state)
		h = corners[1][0] + 1
		w = corners[2][1] + 1

		east = west = north = south = reward

		if x < w - 1: east = map_used[x + 1][y]
		if x > 0:     west = map_used[x - 1][y]
		if y < h - 1: north = map_used[x][y + 1]
		if y > 0:     south = map_used[x][y - 1]

		# region probabilities
		north_val = north * 0.8 + (east + west) * 0.1
		south_val = south * 0.8 + (east + west) * 0.1
		east_val = east * 0.8 + (north + south) * 0.1
		west_val = west * 0.8 + (north + south) * 0.1

		# endregion
		return reward + gamma * max([north_val, south_val, east_val, west_val])

	def getActionScores(self, legal, pacman_map, x, y):
		scores, actions = [], []
		for action in legal:
			if action is Directions.NORTH:
				value = pacman_map[y + 1][x]
			elif action is Directions.SOUTH:
				value = pacman_map[y - 1][x]
			elif action is Directions.EAST:
				value = pacman_map[y][x + 1]
			elif action is Directions.WEST:
				value = pacman_map[y][x - 1]

			scores.append(value)
			actions.append(action)

		return [scores, actions]

	def getAction(self, state):
		pacman_loc = api.whereAmI(state)

		self.updateFoodInMap(state, pacman_loc)
		self.updateCapsulesInMap(state, pacman_loc)
		self.updateGhostsInMap(state, pacman_loc)
		self.rewardConvergence(state)

		legal = api.legalActions(state)
		if Directions.STOP in legal:legal.remove(Directions.STOP)
		
		[scores, actions] = self.getActionScores(legal, map_array, pacman_loc[0], pacman_loc[1])
		return api.makeMove(actions[scores.index(max(scores))], legal)
