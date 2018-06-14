# autoumpire
Tool to help with umpiring an Assassins game. The current input involves a CSV file containing relevant player details (should be collected on signup) and writing a game file, which contains a domain-specific-language description of events. Sample inputs are provided in this repo.

Running AutoUmpire.py with the gamefile and the player CSV in the same directory runs every event in the gamefile from start to finish.

To run the autoumpire, first ensure all Python files are in the same directory as a game_config.cfg file. Then:

```
python AutoUmpire.py
```

The config file must contain the following details (defaults shown):
```
[all]
# Name of file to contain output news templates
news_file = news.html
# Name of file to read game events from
game_file = game.txt
# Name of file containing player information
player_file = exampleplayers.csv
# Start of game date. Date format: dd.mm.yy
start_date = 01.06.16
```
The output includes a news text file and score files. The news text file contains individual HTML report templates for every individual event in the game file. An event is everything that happens on a line of the gamefile which includes a time. Example scorefile creation is at the bottom of AutoUmpire.py. Scorefiles can be created to contain plaintext scores or HTML tables, ordered by any player attribute.

Evolving variants of this tool have been used in games MW14, MW15, MW16, MW17, MW18.

There are no assassins in Cambridge.



## Commands usable in the Autoumpire

Commands are executed in order from top of file to bottom, one line at a time.

**An event template will only be created for a line with a `TIME` specified. All events listed on a given line with a `TIME` will appear in the same template.**  

A new line starts after a linebreak.  
Multiple commands may be chained on a given line using `ALSO`.  
Any text following a `#` marker is a comment.  
All commands on a given line take place simultaneously (allowing e.g. double kills.)  
In each example, PlayerX indicates the player's full (signup) name, **not pseudonym**. The quotation marks are necessary. 

**MAIN AND MW GAME**

**Date/time**


```
DATE=10.08.16
TIME=15:05
```

**Kills**

Kills must be associated with a time.  
Double kills may be specified as in the first example.  
One player may kill multiple players as in the second example. 
Multiple separate kills may take place at the same time as in the third example.
Multiple players may not kill one player.

```
"Player4" KILLS "Player2" ALSO "Player2" KILLS "Player4" TIME=15:05
"Player2" KILLS "Player3" "Player1" TIME=11:10
"Player1" KILLS "Player2" ALSO "Player3" KILLS "Player4" TIME=15:05
```

**Remove player**
```
REMOVE "Player1"
```

**Other player activities**  
`ATTEMPT` and `ACCOMP` may add competence in the main game, depending on the configuration. Even if not, they may be used to maintain a clearer record of the game.  
`EVENT` can be used to generate a template for a generic event in which no attempt or accomplicing occurs, such as a random player report. It will never add competence.
```
ATTEMPT "Player1"
ACCOMP "Player1"
EVENT "Player1" TIME=11:10 
```

**MAIN GAME ONLY**  

**Competence**  
TODO: adjust inco deadlines (across all players)

**Police Players**  
TODO: make player into police player, resurrect a police player optionally with a given rank

**Wantedness**  
This can be applied to assassins or police players. In the case of a player killing a non-target, players will not become wanted automatically, but a prompt message will appear if WANTED does not occur in the same event.
```
WANTED "Player1"
REDEEMED "Player1"
```

**MW ONLY**

**Bonus points** 

Give a player an int, float, positive or negative number of bonus points. 
Will not generate a report template unless associated with a time.
```
"Player1" BONUS=4.3
"Player2" BONUS=-1
```
**Mark a player as casual**

A player becomes a casual player for the purposes of listing scores.
Will not generate a report template.
Should be given its own line in the game-file, if only for clarity.
```
CASUAL "Player1"
```
