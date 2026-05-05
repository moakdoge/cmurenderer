
import sys
from typing import TYPE_CHECKING, Literal


if TYPE_CHECKING:
    from engine._game import Game
class CMUtils():
    _game: "Game"
    

    def __init__(self) -> None:
        self._globals: dict = {}
        self.locked_mouse = False
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
    def is_web() -> Literal[False]:
        return (sys.implementation.name == "brython") # type: ignore

    @classmethod
    def is_desktop(cls) -> Literal[True]:
        return (sys.implementation.name == "cpython") # pyright: ignore[reportReturnType]
    
    def run(self):
        if self.is_desktop():
            main=sys.modules["__main__"]
            for glob, func in self._globals.items():
                setattr(main, glob, func)
            from cmu_graphics import cmu_graphics
            cmu_graphics.run() # type: ignore
        else:
    
            for glob, func in self._globals.items():
                globals()[glob] = func
                
    def lock_mouse(self):
        if self.is_desktop():
            import pygame
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
        self.locked_mouse = True
    def unlock_mouse(self):
        if self.is_desktop():
            import pygame
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
        self.locked_mouse = False