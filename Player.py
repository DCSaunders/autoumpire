#!/usr/bin/env python
class Player(object):
    # Player class for MayWeekAutoUmpire project written by Danielle Saunders (ds636)

    # Notes that another player has killed you.
    def died(self, otherPlayer):
        if otherPlayer in self.killedByList:
            self.killedByList[otherPlayer]+=1
        else:
            self.killedByList[otherPlayer]=1
        self.deaths+=1

    # Add bonus points
    def bonus(self, points):
        self.bonus_points += points

    # Calculate total points. Equations provided are those used for the MW14 game.
    # NB: The main ideas of the scoring system are to:
    # 1) Ensure killing is more profitable than dying is unprofitable (someone who kills 3 people and dies to 3 people should come out with a net positive)
    # 2) Ensure spawncamping isn't a good tactic (someone who kills their neighbour 8 times and no-one else shouldn't win.)
    # Current approach is an exponentially decaying function of how many times a person has killed each player.
    # THIS MAY BE CHANGED AT UMPIRE'S DISCRETION.
    def calcPoints(self):
        from math import exp
        for i in self.killedList:
            # Go through each player this player has killed
            for j in range(1,self.killedList[i]+1):
                # Go through each kill of that player and sum scores.
                self.points = self.points + j*exp(1-j)
        for i in self.killedByList:
            for j in range(1,self.killedByList[i]+1):
                # Go through each death and sum scores.
                self.points = self.points - 0.5*j*exp(1-j)
        self.points = 10*self.points # NB points are scaled BEFORE bonus added! 
        self.points += self.bonus_points


    # Sets that killed another player, sets a report
    def killed(self, other_players, time):
        for other_player in other_players:
            if other_player in self.killedList:
                self.killedList[other_player]+=1
            else:
                self.killedList[other_player]=1
            self.kills+=1
            other_player.died(self)

        
    def __init__(self, name, pseudonym, college, address, water, notes, email, news):
        self.name = name
        self.pseudonym = pseudonym
        self.college = college
        self.address = address
        self.water_status = water
        self.notes = notes
        self.email = email
        self.news = news
        self.kills = 0
        self.deaths = 0
        self.bonus_points = 0
        self.points = 0
        self.killedList = {}
        self.killedByList = {}
