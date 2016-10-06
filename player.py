#!/usr/bin/env python
# Player class for MayWeekAutoUmpire project written by Danielle Saunders
from __future__ import division

import collections
import time

RESURRECT_TIME = 4 * 3600
DEAD_COLOUR = '<span class="colourdead1">'
END_SPAN = '</span>'
LIVE_COLOUR = '<span class="colourliveplayer6">'


class Player(object):
    # Notes that another player has killed you.
    def died(self, killer, time):
        self.killed_by_list[killer] += 1
        self.deaths += 1
        self.last_death_time = time

    def invalid_death(self, killer_name, attempt_time):
        new_format = '%d.%m.%y %H:%M'
        attempt_time = time.strftime(new_format, attempt_time)    
        if self.in_game:
            last_death = time.strftime(new_format, self.last_death_time)
            output_tuple = (killer_name, self.name, attempt_time, last_death)
            print '%s cannot kill %s at %s: previous death at %s' % output_tuple
        else:
            output_tuple = (self.name, attempt_time, killer_name)
            print '%s is no longer playing at %s - %s cannot kill them' % output_tuple
  
    def is_alive(self, death_time):
        alive = True
        if self.last_death_time:
            alive = self.time_since_death(death_time) >= RESURRECT_TIME
        return alive

    def time_since_death(self, death_time):
        death_time_seconds = time.mktime(death_time)
        last_death_time_seconds = time.mktime(self.last_death_time)
        return death_time_seconds - last_death_time_seconds

    def represent(self, death_time):
        if not self.in_game:
            represent = '%s, who is no longer playing' % self.name
        elif not self.last_death_time or self.is_alive(death_time):
            represent = ''.join((LIVE_COLOUR, self.pseudonym, END_SPAN))
        else:
            represent = '%s (%s)' % (self.pseudonym, self.name)
            represent = ''.join((DEAD_COLOUR, represent, END_SPAN))
            if death_time != self.last_death_time:
                represent = ' '.join(['the corpse of', represent])
        return represent

    # A rough approximation to kill-death-ratio for score ordering
    def kill_death_ratio(self):
        if self.deaths == 0:
            ratio = self.kills
        else:
            ratio = self.kills / self.deaths
        return ratio
    
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
    def calc_points(self):
        from math import exp
        for kill_count in self.killed_list.values():
            # Go through each player this player has killed
            for j in range(1, kill_count + 1):
                # Go through each kill of that player and sum scores.
                self.points = self.points + j * exp(1 - j)
        for death_count in self.killed_by_list.values():
            for j in range(1, death_count + 1):
                # Go through each death and sum scores.
                self.points = self.points - 0.5 * j * exp(1 - j)
        self.points = 10 * self.points # NB points scaled BEFORE bonus added! 
        self.points += self.bonus_points

    # Sets that killed another player, sets a report
    def killed(self, other_players, time):
        for other_player in other_players:
            if other_player.is_alive(time) and other_player.in_game:
                self.killed_list[other_player] += 1
                self.kills += 1
                other_player.died(self, time)
            else:
                other_player.invalid_death(self.name, time)

    def remove_from_game(self):
        self.in_game = False
    
    def make_casual(self):
        self.casual = True
        
    def __init__(self, name, pseud, college, address, water, notes, email):
        self.name = name
        self.pseud_list = [pseud.strip('"').strip() for pseud in pseud.split(' / ')] 
        self.pseudonym = self.pseud_list[0].strip()
        self.college = college
        self.address = address
        self.water_status = water
        self.notes = notes
        self.email = email
        self.kills = 0
        self.deaths = 0
        self.bonus_points = 0
        self.points = 0.0
        self.in_game = True
        self.casual = False
        self.killed_list = collections.defaultdict(int)
        self.killed_by_list = collections.defaultdict(int)
        self.last_death_time = None
      