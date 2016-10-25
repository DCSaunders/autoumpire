#!/usr/bin/env python

class TestPlayer(object):
    def __init__(self, name):
        self.name = name
        self.targets = []
        self.assassins = []

player_list = []
for i in range (0, 20):
    player_list.append(TestPlayer('player{}'.format(i)))


'''
Need to store targets in an adjacency matrix like so:
targets = [v0 v1 v2 v3 v4 v5]
targets[0] = v0 = [1 2 5] - player 0 has targets 1, 2, 5
Need to avoid cycles, multiple edges (could be sets rather than lists), and 3-cycles (target triangles where each vertex is the target of the other two.) 


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
'''
