from scipy.special import binom

from dataclasses import dataclass
from functools import total_ordering
from random import randint

_pid = 0

class GameError(Exception):
    pass


@total_ordering
@dataclass
class Bet:
    amount: int
    face: int

    # A bet is less than another bet by checking the amount first, then the face value.
    def __lt__(self, other: "Bet"):
        if other is None:
            return other
        return (self.amount, self.face) < (other.amount, other.face)

    def __str__(self) -> str:
        return f"{self.amount}x [{self.face}]"


class Player:
    """Represents one individual player."""
    def __init__(self, name: str, dice_count = 5, dice_size = 6):
        global _pid
        self.id = _pid
        _pid += 1
        self.name = name
        self.dice_size = dice_size

        # Dice don't need to be special, a list of numbers is probably fine
        self.dice: list[int] = []
        for i in range(dice_count):
            self.dice.append(randint(1, self.dice_size))

    def roll(self):
        count = len(self.dice)
        self.dice.clear()
        for i in range(count):
            self.dice.append(randint(1, self.dice_size))

    def remove_die(self):
        self.dice.pop()

    # A Player loses when they run out of dice.
    @property
    def lost(self) -> bool:
        return len(self.dice) == 0

    @property
    def dice_string(self) -> str:
        s = ""
        for i in self.dice:
            s += f" [{i}]"
        return s.strip()

    def __str__(self) -> str:
        s = f"{self.name:>10}: "
        for i in self.dice:
            s += f" [{i}]"
        return s


class Game:
    """Represents an entire game's backend logic and state-keeping."""
    def __init__(self, player_names: list[str] = [], dice_count = 5, dice_size = 6):
        self.dice_count = dice_count
        self.dice_size = dice_size

        # Create players from names
        self.players: list[Player] = []
        for name in player_names:
            self.players.append(
                Player(name, self.dice_count, self.dice_size)
            )

        # Game state
        self.current_bet: Bet = None
        self.previous_player: Player = None
        self.current_player: Player = None

    @property
    def dice_in_play(self) -> int:
        """Amount of dice in play."""
        return sum((len(p.dice) for p in self.players))

    @property
    def all_dice(self) -> list[int]:
        """Every individual die in play."""
        d = []
        for p in self.players:
            d += p.dice
        return d

    @property
    def game_over(self) -> bool:
        """Return True if only one player is left."""
        return len(self.players) == 1

    def check_bet(self, bet: Bet) -> bool:
        """Return True if a bet is valid against the current dice in play."""
        return self.all_dice.count(bet.face) >= bet.amount

    def check_spot_on(self, bet: Bet) -> bool:
        """Return True if a bet is spot-on against the current dice in play."""
        return self.all_dice.count(bet.face) == bet.amount

    def spot_on_equation(self, die_face: int, dice_amount: int, dice_in_play: int, known_dice: list[int] = []) -> float:
        """What are the odds of a spot-on bet being true?"""
        dice_amount -= known_dice.count(die_face)
        dice_in_play -= len(known_dice)
        q = dice_amount
        n = dice_in_play
        c = binom(n, q)
        return c * ((1/self.dice_size)**q) * (((self.dice_size - 1)/self.dice_size)**(n - q))

    def bet_equation(self, die_face: int, dice_amount: int, dice_in_play: int, known_dice: list[int] = []) -> float:
        """What are the odds of a bet being true?"""
        dice_amount -= known_dice.count(die_face)
        dice_in_play -= len(known_dice)
        return sum([self.spot_on_equation(die_face, i, dice_in_play) for i in range(dice_amount, dice_in_play + 1)])

    def next_player(self) -> Player:
        """Take a player off the beginning of the list,
           and return it after putting it back on the end."""
        self.previous_player = self.current_player
        p = self.players.pop(0)
        self.players.append(p)
        self.current_player = p
        return p

    def remove_lost_players(self) -> list[Player]:
        """Remove any players with zero dice from the game."""
        lost_players = [p for p in self.players if p.lost]
        for lp in lost_players:
            self.players.remove(lp)
        return lost_players

    def setup(self):
        """Called at the beginning of a new game. Get everything prepared."""
        for player in self.players:
            player.roll()
        self.current_player = None
        self.previous_player = None
        self.current_bet = None
        self.next_player()

    def reset(self):
        """Called at the beginning of a new round. Get everything prepared."""
        for player in self.players:
            player.roll()
        self.current_bet = None

    # First bet works slightly differently to other bets so it's its own thing.
    def first_bet(self, bet: Bet):
        if bet.amount > self.dice_in_play:
            raise GameError(f"Bet is for more dice than are on the table. ({bet.amount}).")
        if bet.face > self.dice_size or 1 > bet.face:
            raise GameError(f"Bet is for an invalid die face ({bet.face}).")
        self.current_bet = bet

    def place_bet(self, bet: Bet):
        if bet.amount > self.dice_in_play:
            raise GameError(f"Bet is for more dice than are on the table. ({bet.amount}).")
        if bet.face > self.dice_size or 1 > bet.face:
            raise GameError(f"Bet is for an invalid die face ({bet.face}).")
        if bet.amount > self.current_bet.amount or (bet.amount == self.current_bet.amount
                                                    and bet.face > self.current_bet.face):
            self.current_bet = bet
        else:
            raise GameError("Bet ({bet}) isn't better than the current bet ({self.current_bet})")

    def call_bluff(self) -> bool:
        """Call the previous player's bluff. Returns True if the current player was right."""
        if self.check_bet(self.current_bet):
            self.current_player.remove_die()
            self.reset()
            return False
        else:
            self.previous_player.remove_die()
            self.reset()
            return True

    def call_spot_on(self) -> bool:
        """Call the previous player's bet spot-on. Returns True if the current player was right."""
        if self.check_spot_on(self.current_bet):
            for p in self.players:
                if p != self.current_player:
                    p.remove_die()
            self.reset()
            return True
        else:
            self.current_player.remove_die()
            self.reset()
            return False

    def __str__(self) -> str:
        players = "\n".join([str(p) for p in self.players])
        s = f"Current Player: {self.current_player.name}\nCurrent Bet: {self.current_bet}\n"
        s += players
        return s
