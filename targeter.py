#!/usr/bin/env python
import numpy as np

class TestPlayer(object):
    def __init__(self, name):
        self.name = name
        self.targets = []
        self.assassins = []

class Node(object):
    def __init__(self, name=None):
        self.targets = set()
        self.assassins = set()
        self.player = None
        self.name = name

    def check_three_cycle(self, node):
        # return false if adding this node as a target would make
        # a 3-cycle
        for a in self.assassins:
            if node in a.assassins or node in a.targets:
                return False
        for t in self.targets:
            if node in t.assassins or node in t.targets:
                return False
        return True
            

class Graph(object):
    def __init__(self, node_count):
        self.nodes = []
        self.node_count = node_count
        for i in range(0, self.node_count):
            self.nodes.append(Node(i))

    def get_next_prime(self):
        if (self.node_count + 1) % 2 == 0:
            n = self.node_count + 2
        else:
            n = self.node_count + 1
        while(not self.is_prime(n)):
            n += 2
        return n

    def is_prime(self, n):
        test = 3
        while test <= np.sqrt(n):
            if n % test == 0:
                return False
            test += 2
        return True

    def construct(self):
        for i, node in enumerate(self.nodes):
            targets = [j % self.node_count
                       for j in (i + 5, i + 6, i + 8)]
            for t in targets:
                node.targets.add(self.nodes[t])
                self.nodes[t].assassins.add(node)
                             
    def print_graph(self):
        for node in self.nodes:
            print 'Node {}: assassins: {}, targets: {}'.format(
                node.name,
                [n.name for n in node.assassins],
                [n.name for n in node.targets])

    def dotfile_graph(self):
        with open('targets.dot', 'w') as f:
            f.write('digraph targetting {\n')
            for node in self.nodes:
                for t in node.targets:
                    f.write('"{}" -> "{}";\n'.format(node.name, t.name))
            f.write('}\n')
            
np.random.seed(1234)
player_list = []
player_count = 28
for i in range (0, player_count):
    player_list.append(TestPlayer('player{}'.format(i)))
targets = Graph(player_count)
targets.construct()
targets.print_graph()
targets.dotfile_graph()

'''
Need to store targets in an adjacency list like so:
targets = [v0 v1 v2 v3 v4 v5]
targets[0] = v0 = [1 2 5] - player 0 has targets 1, 2, 5
Need to avoid self-cycles, multiple edges (could be sets rather than lists), and 3-cycles (target triangles where each vertex is the target of the other two.) 

- I cannot target myself.
- I cannot target my assassin
- I cannot target my target's target

A player must always have three distinct
targets and three distinct assassins, and a player may not target their own
assassins (or indeed themselves). In graph theoretic terms this is equivalent
to saying that the targetting graph must remain `simple'

For initial targetting, a completely random (simple) targetting graph is 
generated. While this meets the first two goals, it is very badly suited for 
the third, on occasions blocking after fewer than 10 deaths. The reason for 
this is the existence of `3-cycles', groups of 3 players, all of whom are 
legal targets for each other. It is impossible for a blockage to occur without 
passing through a 3-cycle state, so avoiding these is an excellent way of 
cutting down on blockages. To this end, the targetter randomly reassigns links 
which cause 3-cycles to occur until none remain.

At this point, the targetting graph is finished, and all that remains is to 
assign players to nodes on the graph. This is where the seeding mechanism takes
effect. The players are sorted by their umpire-assigned seed values (with random
sorting where these are equal). They are then placed into the targetting graph 
from the highest seed down, in such a way as to maximise the distance between 
the player being added and all previous players. Obviously, this ceases to be 
useful once we reach the point where all empty graph locations are adjacent to 
an existing player. 
Seeds in e.g. nodes 0, 9, 18, 27...
'''
