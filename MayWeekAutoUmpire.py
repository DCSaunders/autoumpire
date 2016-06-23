import csv
import operator
import os.path
from Player import Player

# Enum for columns of playerlist containing relevant info
# If changing playerlist layout, be sure to edit this enum.
class Field(object):
    name = 0
    pseud = 1
    college = 2
    address = 3
    water = 4
    notes = 5
    email = 6
    

# Initialises playerlist and newsfile
# p: player dictionary.
# playerFile: csv file containing playerlist.
# newsFile: text file to output report templates
# startID: anchor ID used for unique HTML links
# index_attr: attribute to index playerlist. Default set to be name
def initialiseGame(p, playerFile, newsFile, startID, index_attr):
    initialiseNews(newsFile, startID)
    with open(playerFile, 'rb') as f:
        reader = csv.reader(f)
        reader.next()
           
        for row in reader:
            player = Player(row[Field.name],row[Field.pseud],row[Field.college], \
                            row[Field.address],row[Field.water],row[Field.notes], \
                            row[Field.email])
            ## If you'd rather index the game by e.g. pseudonym, you can!
            ## Just change the bit in the square brackets on the next line.
            p[getattr(player, index_attr)] = player


# Runs the game start to finish. The only function you should need to update.
# NB Example function indexes using name
# p: player dictionary
# index_attr: attribute to index playerlist. Default set to be name
def runGame(p, index_attr):
    try:
        
        p["Thomas Ruddle"].killed(p["Douglas Hall"], "00:00")
        p["Curtis Reubens"].killed(p["Thomas Ruddle"], "11:00")
        p["Curtis Reubens"].killed(p["Thomas Ruddle"], "15:20")
        p["Curtis Reubens"].killed(p["Thomas Ruddle"], "19:25")
        p["Curtis Reubens"].killed(p["Thomas Ruddle"], "08:20")
        p["Douglas Hall"].bonus(17)
        p["Curtis Reubens"].killed(p["Thomas Ruddle"], "10:00")
        startReporting(p) # !!PLACE THIS LINE WHERE YOU WANT NEW REPORTS TO START!!

    except KeyError, e:
        print "KeyError {} - indexing by {}".format(str(e), index_attr)
    except e:
        print str(e)
        raise
    

# Score the playerlist
# p: player dictionary
def score(p):
    for player in p.itervalues():
        player.calcPoints()

        
# Enable addition of new report templates
# p: player dictionary
def startReporting(p):
    for player in p.itervalues():
        player.startReporting()


# Sets up news file with anchor for unique HTML links
# newsFile: output file.
# startID: ID for unique HTML links
def initialiseNews(newsFile, startID):
    if (os.path.isfile(newsFile) == False):
        with open(newsFile, 'w') as f:
            f.write(startID)
    else:
        print 'News file already initialised'


# Output plaintext scores
# p: sorted player dictionary
# scoreFile: file to output plaintext scores
def plaintextScores(pList, scoreFile):

    with open(scoreFile, 'w') as f:
        for player in pList:
            pointStr = (player.name, str(player.points), "\n")
            pointStr = " ".join(pointStr)
            print pointStr
            f.write(pointStr)


# Output scores in HTML table
# p: sorted player dictionary.
# scoreFile: file for output.
def htmlScores(pList, scoreFile):
    t_s = "<table>"
    t_e = "</table>"
    row_s = "<tr>"
    row_e = "</tr>"
    entry_s = "<td>"
    entry_e = "</td>"
    nl = "\n"

    with open(scoreFile, 'w') as f:
        # Write scores in table
        f.write(t_s)

        for player in pList:
            pointStr = (player.name, player.pseudonym,
                        player.address, player.college,
                        player.waterStatus, player.notes,
                        str(player.kills), str(player.deaths),
                        '%.2f' % player.points)
            pointStr ="{}{}".format(entry_e, entry_s).join(pointStr)
            f.write("{}{}{}{}{}{}".format(row_s, entry_s, pointStr, entry_e, row_e, nl))
        f.write(t_e)


# Output scores in HTML table or plaintext
# p: player dictionary.
# k: key to sort on.
# html: false if plaintext output, true if html table
# desc: false if ascending, true if descending.
def outputScores(p, html, k, desc):
    pList = sorted(p.values(), key=operator.attrgetter(k), reverse = desc)
    oType = "html" if html else "plaintext"
    fileName = "scores-{}-{}.txt".format(k, oType)

    if (html):
        htmlScores(pList, fileName)
    else:
        plaintextScores(pList, fileName)


# Set up filenames, run game
if __name__ == '__main__':
    newsFile = "news.txt" # Text file the news will be written to. 
    startID = "e16000" # Anchor for first entry in news file
    playerFile = "MWAUexampleplayers.csv"
    index_attr = 'name' # Change to e.g. 'email', 'pseudonym' or other unique attr of Player class if want
    p = dict() # Player dictionary

    initialiseGame(p, playerFile, newsFile, startID, index_attr)
    runGame(p, index_attr)
    score(p)
    outputScores(p, False, 'points', True) # simple plaintext scores in point order
    outputScores(p, True, 'points', True) # html scores in point order
    outputScores(p, True, 'college', False) # html scores in college order
    outputScores(p, True, 'name', False) # html scores in name order
    outputScores(p, True, 'kills', True) # simple plaintext scores in point order

