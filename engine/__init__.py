
from typing import TYPE_CHECKING

from engine.config import GameConfiguration

if TYPE_CHECKING:
    from engine._game import Game
    from engine.config import GameConfiguration


def make_game() -> "Game":
    from engine._game import Game

    game = Game()

    if not game.utils.is_web():
        import sys
        for name, mod in sys.modules.items():
            if name == "engine.triangle":
                mod.existing_game = game  # type: ignore[attr-defined]
                break
    else:
        existing_game = game

    game.configuration = GameConfiguration()
    return game


game = make_game()