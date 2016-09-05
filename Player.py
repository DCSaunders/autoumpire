#!/usr/bin/env python

import collections
import time

class Player(object):
    # Player class for MayWeekAutoUmpire project written by Danielle Saunders (ds636)

    # Notes that another player has killed you.
    def died(self, killer, time):
        self.killedByList[killer] += 1
        self.deaths += 1
        self.last_death_time = time

    def invalid_death(self, killer_name, attempt_time):
        new_format = '%d.%m.%y %H:%M'
        attempt_time = time.strftime(new_format, attempt_time)    
        last_death = time.strftime(new_format, self.last_death_time)
        output_tuple = (killer_name, self.name, attempt_time, last_death)
        print '%s cannot kill %s at %s: previous death at %s' % output_tuple
  
    def is_alive(self, death_time):
        alive = True
        if self.last_death_time:
            delta = time.mktime(death_time) - time.mktime(self.last_death_time)
            alive = delta > 3600
        return alive
        
    # Add bonus points
    def bonus(self, points):
        self.bonus_points += points

    # Calculate total points. Equations provided have been used since MW14 game.
    # NB: The main ideas of the scoring system are to:
    # 1) Ensure killing is more profitable than dying is unprofitable
    # - (killing 3 and dying to 3 people should give a net positive score)
    # 2) Reduce the effectiveness of spawncamping
    # - (just killing your neighbour repeatedly shouldn't be a winning tactic.)
    # Current score is an exponentially decaying function of how many times
    # a player has killed each other player.
    # THIS MAY BE CHANGED AT UMPIRE'S DISCRETION.
    def calcPoints(self):
        from math import exp
        for i in self.killedList:
            # Go through each player this player has killed
            for j in range(1, self.killedList[i] + 1):
                # Go through each kill of that player and sum scores.
                self.points = self.points + j * exp(1 - j)
        for i in self.killedByList:
            for j in range(1, self.killedByList[i] + 1):
                # Go through each death and sum scores.
                self.points = self.points - 0.5 * j * exp(1 - j)
        self.points = 10 * self.points # NB points scaled BEFORE bonus added! 
        self.points += self.bonus_points


    # Sets that killed another player, sets a report
    def killed(self, other_players, time):
        for other_player in other_players:
            if other_player.is_alive(time):
                self.killedList[other_player] += 1
                self.kills += 1
                other_player.died(self, time)
            else:
                other_player.invalid_death(self.name, time)
        
    def __init__(self, name, pseud, college, address, water, notes, email):
        self.name = name
        self.pseudonym = pseud
        self.college = college
        self.address = address
        self.water_status = water
        self.notes = notes
        self.email = email
        self.kills = 0
        self.deaths = 0
        self.bonus_points = 0
        self.points = 0
        self.killedList = collections.defaultdict(int)
        self.killedByList = collections.defaultdict(int)
        self.last_death_time = None
      
