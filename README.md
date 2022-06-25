# Liar's Dice
A Python implementation of the dice-betting game made popular in *Red Dead Redemption*.

This Python version of *Liar's Dice* is written in an API-style, seperating the code into game logic and state-keeping (API) and display and interaction (interface).

The API is found in [`game.py`.](dice/lib/game.py)

The interface is found in [`gameinterface.py`](dice/lib/gameinterface.py).

## Requirements
* Python 3.10+
* `rich`
* `scipy`
* A terminal that can render colors and emojis (I recommend [*Windows Terminal.*](https://github.com/microsoft/terminal))

## References
* *Liar's Dice* on [Wikipedia.](https://en.wikipedia.org/wiki/Liar%27s_dice)
* *Liar's Dice* on the [Red Dead Redemption Wiki.](https://reddead.fandom.com/wiki/Liar%27s_Dice)
