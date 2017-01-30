**List of commands usable in the Autoumpire**

Commands are executed in order from top of file to bottom, one line at a time.
**An event template will only be created for a line with a `TIME` specified. All events listed on a given line with a `TIME` will appear in the same template.**  
A new line starts after a linebreak, not after line wrapping.  
Multiple commands may be chained on a given line using `ALSO`.  
Any text following a `#` marker is a comment.  
All commands on a given line take place simultaneously (allowing e.g. double kills.)  
In each example, PlayerX indicates the player's full (signup) name.  

**MAIN AND MW GAME**

**Date/time**


```
DATE=10.08.16
TIME=15:05
```

**Kills**
Kills must be associated with a time.  
Double kills may be specified as in the first example below.  
One player may kill multiple players as in the second example below. Multiple players may not kill one player.

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
`EVENT` can be used for a generic event in which no attempt or accomplicing occurs, such as a random player report. It will never add competence.
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
"Player1" BONUS=4

**Mark a player as casual**
```
CASUAL "Player1"
```