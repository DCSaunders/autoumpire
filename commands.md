**List of commands usable in the Autoumpire**

Commands are executed in order from top of file to bottom, one line at a time.  
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

```
"Player4" KILLS "Player2" ALSO "Player2" KILLS "Player4" TIME=15:05
"Player2" KILLS "Player3" "Player1" TIME=11:10
```

**Change player status**
```
REMOVE "Player1"
CASUAL "Player1"
```
**Other*
```
EVENT "Player1" TIME=11:10 
```

**MAIN GAME ONLY**

**Competence**
TODO: adjust inco deadlines (across all players)

**Police Players**
TODO: make player into police player, resurrect a police player optionally with a given rank

**Wantedness**
This can be applied to assassins or police players
```
WANTED "Player1"
```

**Other player activities**
These may add competence, depending on the configuration
```
ATTEMPT "Player1"
ACCOMP "Player1"
```

**MW ONLY**

**Bonus points**
"Player1" BONUS=4