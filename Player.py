class Player(object):
    # Player class for MayWeekAutoUmpire project written by Danielle Saunders (ds636)
    "Player object"    
    name = "name"
    pseudonym = "pseudonym"
    college = "college"
    address = "address"
    waterStatus = "water status"
    notes = "notes"
    email = "email"
    report = False


    # Mark that new report templates should be created
    def startReporting(self):
        self.report = True


    # Build HTML string for report template
    def __reportString(self, otherPlayer, ID, time):
        nl = "\n"
        event_s = "<div xmlns="" class=\"event\">"
        hr = "<hr/>"
        id_s = "<span id={}>[{}]".format(ID, time)
        head_s = "<span class=\"headline\">"
        report_s = "<div class=\"report\">"
        indent_s = "<div class=\"indent\">"
        p_s = "<p>"
        p_e = "</p>"
        div_e = "</div>"
        span_e = "</span>"

        report = ("{}{}{}{}{}{}".format(nl, nl, event_s, hr, id_s, head_s),
                  " {} ({}) kills {} ({}) ".format(self.pseudonym, self.name, otherPlayer.pseudonym, otherPlayer.name),
                  "{}{}{}{}".format(span_e, span_e, span_e, hr),
                  "{}{}{}{} reports: {}{}{}{}{}".format(report_s, indent_s, p_s, self.pseudonym, nl, p_e, div_e, div_e, div_e),
                  "{}{}{}{} reports: {}{}{}{}{}".format(report_s, indent_s, p_s, otherPlayer.pseudonym, nl, p_e, div_e, div_e, div_e))
        return "".join(report)

        
    # Create a template for a new report.
    def __newReport(self, otherPlayer, time):
        news = "news.txt" # Text file the news will be written to. Change if want.
        lines = open(news, 'r').readlines()

        # ID is formed of one letter, then numbers
        ID = lines[0]
        idnum = int(ID[1:]) + 1
        ID = ID[0] + str(idnum)
        lines[0] = ID+"\n"

        with open(news, 'w') as f:       
            for line in lines:
                f.write(line)
            f.close()
            rep = self.__reportString(otherPlayer, ID, time)

            with open(news, 'a') as f:
                f.write(rep)



    # Notes that another player has killed you.
    def died(self, otherPlayer):
        if otherPlayer in self.killedByList:
            self.killedByList[otherPlayer]+=1
        else:
            self.killedByList[otherPlayer]=1
        self.deaths+=1


    # Add bonus points. Does NOT add a report.
    def bonus(self, bPoints):
        self.bonusPoints += bPoints

        
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
            # Go through each player this player has died to
            for j in range(1,self.killedByList[i]+1):
                # Go through each death and sum scores.
                self.points = self.points - 0.5*j*exp(1-j)

        self.points = 10*self.points # NB points are scaled BEFORE bonus added! 
        self.points += self.bonusPoints


    # Sets that killed another player, sets a report
    def killed(self, otherPlayer, time):
        if (self.report==True):
            self.__newReport(otherPlayer, time)

        if otherPlayer in self.killedList:
            self.killedList[otherPlayer]+=1
        else:
            self.killedList[otherPlayer]=1
        self.kills+=1
        otherPlayer.died(self)

        
    def __init__(self, pName, pPseudonym, pCollege, pAddress, pWaterStatus, pNotes, pEmail):
        self.name = pName
        self.pseudonym = pPseudonym
        self.college = pCollege
        self.address = pAddress
        self.waterStatus = pWaterStatus
        self.notes = pNotes
        self.email = pEmail
        self.kills = 0
        self.deaths = 0
        self.bonusPoints = 0
        self.points = 0
        self.report = False
        self.killedList = {}
        self.killedByList = {}
