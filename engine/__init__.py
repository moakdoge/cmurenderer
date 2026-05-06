from engine._game import Game
from engine.config import GameConfiguration
game = Game()

if not game.utils.is_web():
    import sys
    for name, mod in sys.modules.items():
        if name == "engine.triangle":
            mod.existing_game = game # type: ignore
            break
else:
    existing_game = game
    
game.configuration = GameConfiguration()