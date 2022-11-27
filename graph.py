import math
import numpy as np

class Graph:
	def __init__(self, vertices):
		# make sure dont have dup edges or nodes
		self.nodes = []
		self.edges = []

		# dictionary:
			# a key = 1 node (a website url)
			# value = list of urls (either outgoing or incoming)

		# know incoming and outgoing links for each node
		self.incomingLinks = {}
		self.outgoingLinks = {}

		numVertices = len(vertices)
		for i in range(0, numVertices):
			self.nodes.append(vertices[i])
			self.incomingLinks[vertices[i]] = []
			self.outgoingLinks[vertices[i]] = []
			

	# nodeA points to nodeB    A --> B
	def addEdge(self, nodeA, nodeB):
		edge = (nodeA, nodeB) # tuple
		# dont add edge if it already exists
		if edge in self.edges:
			print("Edge duplicate found.")
			return

		# both nodes (vertices) should exist, if not, not a valid edge
		if nodeA not in self.edges:
			print(f"{nodeA} is not in a vertice in the graph")
			return

		if nodeB not in self.edges:
			print(f"{nodeB} is not in a vertice in the graph")
			return

		self.edges.append(edge) # is valid edge, add it 

		# A is an incoming link of node B
		# incomingLinks[B] = [A, ...]
		self.incomingLinks[nodeB].append(nodeA)

		# B is an outgoing link of node A
		# outgoingLinks[A] = [B, ...]
		self.outgoingLinks[nodeA].append(nodeB)


	def print(self):
		for node in self.nodes:
			print(f"Node: {node}\n"):
			print(f"Incoming Links: {self.incomingLinks[node]}\n")
			print(f"Outgoing Links: {self.outgoingLinks[node]}\n")


	# hub and authority rankings for each node (site)
	# non-converging HITS alg, stops after i iterations
	def get_HITS(self, iterations):
		# key = node, value = tuple (authScore, hubScore)
		scores = {}

		# each node starts with auth 1 and hub 1
		for node in self.nodes:
			scores[node] = (1, 1) # (a, h)

		for _ in range(iterations):
			# update all authority vals
			for node in self.nodes:
				scores[node][0] = 0 # set this page's auth to 0

				# for each incoming link of node
				for incLink in self.incomingLinks[node]:
					# node's auth += its incLink's hub
					scores[node][0] += scores[incLink][1]


			# update all hub values 
			for node in self.nodes:
				scores[node][1] = 0 # set this page's hub to 0

				# for each outgoing link of node
				for outLink in self.outgoingLinks[node]:
					# node's hub += its outLink's auth
					scores[node][1] += scores[outLink][0]

		return scores




'''
Using class

g = Graph([0, 1, 2, 3]) -- a graph w/ nodes

g.addEdge(0, 1) -- an edge, node 0 points to node 1
<<add more edges>>

pr = g.get_pageRank()
hub, auth = g.get_HITS()
'''











