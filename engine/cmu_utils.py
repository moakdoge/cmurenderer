
import sys
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from engine._game import Game
class CMUtils():
    _game: "Game"
    

    def __init__(self) -> None:
        self._globals: dict = {}
    @staticmethod
    def register_game(obj) -> "Game":
        CMUtils._game: "Game" = obj
        return obj

    def make_global(self, obj, name=None):
        def wrapper(*args, **kwargs):
            return CMUtils._game.__class__.__dict__[obj.__name__](
                CMUtils._game,
                *args,
                **kwargs
            )
        self._globals[name or obj.__name__] = wrapper
        return obj

    @staticmethod
    def is_web():
        return not (sys.implementation.name != "brython")

    def run(self):
        if sys.implementation.name == "cpython":
            main=sys.modules["__main__"]
            for glob, func in self._globals.items():
                setattr(main, glob, func)
            from cmu_graphics import cmu_graphics
            cmu_graphics.run() # type: ignore
        else:
    
            for glob, func in self._globals.items():
                globals()[glob] = func
