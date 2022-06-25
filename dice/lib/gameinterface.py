from rich.console import Console
from rich.table import Table

from .game import Bet, Game, Player

ascii_art = R"""
 /$$       /$$                    /$$              /$$$$$$$  /$$                    
| $$      |__/                   | $/             | $$__  $$|__/                    
| $$       /$$  /$$$$$$   /$$$$$$|_//$$$$$$$      | $$  \ $$ /$$  /$$$$$$$  /$$$$$$ 
| $$      | $$ |____  $$ /$$__  $$ /$$_____/      | $$  | $$| $$ /$$_____/ /$$__  $$
| $$      | $$  /$$$$$$$| $$  \__/|  $$$$$$       | $$  | $$| $$| $$      | $$$$$$$$
| $$      | $$ /$$__  $$| $$       \____  $$      | $$  | $$| $$| $$      | $$_____/
| $$$$$$$$| $$|  $$$$$$$| $$       /$$$$$$$/      | $$$$$$$/| $$|  $$$$$$$|  $$$$$$$
|________/|__/ \_______/|__/      |_______/       |_______/ |__/ \_______/ \_______/
                                                                                    
                                                                                    """

def pause():
    """Alias for `input()`, which just waits for a keypress and throws away the result."""
    input()


class GameInterface:
    def __init__(self, debug = False):
        """A GameInterface allows interacting and displaying the Game using
        the terminal and standard I/O."""
        self.debug = debug
        self.game: Game = None
        self.turn_count = 0
        self.console = Console()
        self.game_over = False

    def print(self):
        """Print a debug of the current game state."""
        table = Table()
        table.title = f"Liar's Dice | Turn {self.turn_count}"
        table.show_header = False
        table.show_lines = True
        table.title_justify = "center"
        table.title_style = "italic"
        table.add_row("Current Player", self.game.current_player.name)
        table.add_row("Current Bet", self.game.current_bet)
        for player in self.game.players:
            table.add_row(player.name, self.fd(player.dice_string), style = self.color_from_player(player))
        self.console.print(table)

    def fd(self, s: str) -> str:
        """aka `format_dice`, replace all `'[n]'` strings with Unicode dice, if we're playing with d6s."""
        return s.replace("[1]", "⚀").replace("[2]", "⚁").replace("[3]", "⚂")\
                .replace("[4]", "⚃").replace("[5]", "⚄").replace("[6]", "⚅")\
                    if (self.game.dice_size == 6 and self.unicode_dice) else s

    def print_all_dice(self):
        """Print all players dice, formatted."""
        table = Table()
        table.show_header = False
        table.show_lines = True
        for player in self.game.players:
            table.add_row(player.name, self.fd(player.dice_string), style = self.color_from_player(player))
        self.console.print(table)

    def setup(self, dice_count = 5, dice_size = 6, unicode_dice = False, show_odds = False):
        """Prepare a new game."""
        self.console.clear()
        self.console.print(ascii_art, style="green")
        namestring = input("Enter names seperated by spaces. >")
        names = namestring.split()
        self.game = Game(names, dice_count, dice_size)
        self.game.setup()
        self.unicode_dice = unicode_dice
        self.show_odds = show_odds
        self.turn_count = 0

    def color_from_player(self, p: Player) -> str:
        """Take a Player and return a color based on their ID."""
        colors = ["red", "green", "blue", "yellow", "magenta", "cyan", "orange1", "purple", "brown", "gray"]
        return colors[p.id % len(colors)]

    def formatted_name(self, p: Player) -> str:
        """Return the player's name formatted with their color."""
        color = self.color_from_player(p)
        return f"[{color}]{p.name}[/{color}]"

    @property
    def current_player_name(self) -> str:
        """Convienience property, analogous to `self.formatted_name(self.game.current_player)`"""
        return self.formatted_name(self.game.current_player)

    @property
    def previous_player_name(self) -> str:
        """Convienience property, analogous to `self.formatted_name(self.game.previous_player)`"""
        return self.formatted_name(self.game.previous_player)

    def wait_for_player(self):
        """Show a prompt to switch control to a new player."""
        self.console.clear()
        self.console.print(
            f"Give the laptop to {self.current_player_name}."
        )
        pause()
    
    def next(self):
        """Called in a loop, runs the game."""
        self.turn_count += 1
        self.game.next_player()
        self.wait_for_player()

        if self.game.current_bet is None:
            self.first_bet()
        else:
            self.show_options()

        self.console.clear()
        lost_players = self.game.remove_lost_players()
        if lost_players:
            for p in lost_players:
                self.console.print(f"{self.formatted_name(p)} has lost all their dice and are out.")
            pause()
        
        if self.game.game_over:
            self.console.clear()
            only_player = self.game.players[0]
            self.console.print(f"{self.formatted_name(only_player)} has won the game in {self.turn_count} turns!")
            self.game_over = True

    def get_valid_bet(self) -> Bet:
        """Prompt a user for a bet, preform basic validation. Returns a `Bet`."""
        die_face = None
        die_count = None
        while die_face is None:
            df = input(f"What face will you bet for? (1-{self.game.dice_size}) > ")
            df = int(df) if df.isnumeric() else 0
            if not (1 <= df <= self.game.dice_size):
                self.console.print("[bold red]Invalid die face.[/bold red]")
            else:
                die_face = df
        while die_count is None:
            dc = input(self.fd(f"How many [{die_face}]s will you bet for? (1-{self.game.dice_in_play}) > "))
            dc = int(dc) if dc.isnumeric() else 0
            if not (1 <= dc <= self.game.dice_in_play):
                self.console.print("[bold red]Invalid die amount.[/bold red]")
            else:
                die_count = dc
        return Bet(die_count, die_face)

    def first_bet(self):
        """Interface for a player to call `Game.first_bet()`."""
        self.console.clear()
        self.console.print(f"[{self.current_player_name}'s Turn]")
        if self.debug:
            self.print()
        self.console.print(self.fd(f"Your Dice: {self.game.current_player.dice_string}\n"))
        self.console.print(f"{self.current_player_name}, place the first bet:")
        bet = self.get_valid_bet()
        self.game.first_bet(bet)
    
    def show_options(self):
        """Menu for selecting what to do on a player's turn."""
        self.console.clear()
        self.console.print(f"[{self.current_player_name}'s Turn]")
        if self.debug:
            self.print()
        self.console.print(self.fd(f"Your Dice: {self.game.current_player.dice_string}"))
        self.console.print(self.fd(f"Current Bet: {self.game.current_bet}\n"))
        self.console.print(f"[u]Options:[/u]\n"
                           f"[b](1)[/b] Call a higher bet.\n"
                           f"[b](2)[/b] Call {self.previous_player_name}'s bluff.\n"
                           f"[b](3)[/b] Declare the current bet spot-on.\n")
        option = None
        while option is None:
            opt = input("> ")
            if opt not in ['1', '2', '3']:
                self.console.print("[bold red]Invalid option.[/bold red]")
            else:
                option = opt
        match option:
            case '1':
                self.place_bet()
            case '2':
                self.call_bluff()
            case '3':
                self.call_spot_on()

    def place_bet(self):
        """Interface for a player to call `Game.place_bet()`."""
        self.console.clear()
        self.console.print(f"[{self.current_player_name}'s Turn]")
        self.console.print(self.fd(f"Your Dice: {self.game.current_player.dice_string}"))
        self.console.print(self.fd(f"Current Bet: {self.game.current_bet}\n"))
        self.console.print(f"{self.current_player_name}, place a new bet:")
        new_bet = None
        while new_bet is None:
            bet = self.get_valid_bet()
            if bet > self.game.current_bet:
                new_bet = bet
            else:
                self.console.print("[bold red]Invalid bet (too low!).[/bold red]")

        self.game.place_bet(new_bet)

    def call_bluff(self):
        """Interface for a player to call `Game.call_bluff()`."""
        self.print_all_dice()
        current_bet_face = self.game.current_bet.face
        current_bet_amount = self.game.current_bet.amount
        current_dice_in_play = self.game.dice_in_play
        known_dice = self.game.current_player.dice
        odds = self.game.bet_equation(current_bet_face, current_bet_amount, current_dice_in_play, known_dice)
        player_correct = self.game.call_bluff()
        if player_correct:
            self.console.print(f"✅ You were correct! {self.previous_player_name} loses a die.")
        else:
            self.console.print(f"❎ You were incorrect. You lose a die.")
        if self.show_odds:
            self.console.print(f"The odds of that bet being true were {odds:.2%}.", style = "italic grey50")
        pause()

    def call_spot_on(self):
        """Interface for a player to call `Game.call_spot_on()`."""
        self.print_all_dice()
        current_bet_face = self.game.current_bet.face
        current_bet_amount = self.game.current_bet.amount
        current_dice_in_play = self.game.dice_in_play
        known_dice = self.game.current_player.dice
        odds = self.game.spot_on_equation(current_bet_face, current_bet_amount, current_dice_in_play, known_dice)
        player_correct = self.game.call_spot_on()
        if player_correct:
            self.console.print(f"✅ You were correct! All players other than {self.current_player_name} lose a die.")
        else:
            self.console.print(f"❎ You were incorrect. You lose a die.")
        if self.show_odds:
            self.console.print(f"The odds of that bet being spot-on were {odds:.2%}.", style = "italic grey50")
        pause()
