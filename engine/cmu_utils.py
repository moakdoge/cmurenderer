
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
    
    
    @property
    def cmu_graphics(self):
        if self.is_desktop():
            import cmu_graphics
            return cmu_graphics
        return None
    
    @property
    def version(self):
        '''Unsupported on CMU; just returns the most recent'''
        if self.is_desktop():
            from cmu_graphics import cmu_graphics
            import os
            current_directory = os.path.dirname(os.path.realpath(cmu_graphics.__file__)) # type: ignore
            with open(os.path.join(current_directory, 'meta', 'version.txt')) as f:
                version = f.read().strip()
                return version
        else:
            with open('https://s3.amazonaws.com/cmu-cs-academy.lib.prod/desktop-cmu-graphics/version.txt', "r") as f:
                return f.read()


        
        

    def make_global(self, obj, name=None, desktop: bool = True, web: bool = True):
        def wrapper(*args, **kwargs):
            return CMUtils._game.__class__.__dict__[obj.__name__](
                CMUtils._game,
                *args,
                **kwargs
            )
        if not desktop and self.is_desktop():
            return obj
        if not web and self.is_web():
            return obj
        self._globals[name or obj.__name__] = wrapper
        return obj

    @staticmethod
    def is_web() -> Literal[False]:
        return (sys.implementation.name == "brython") # type: ignore

    @staticmethod
    def is_desktop() -> Literal[True]:
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
        '''Unsupported on CMU'''
        if self.is_desktop():
            import pygame
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
        self.locked_mouse = True
    def unlock_mouse(self):
        '''Unsupported on CMU'''
        if self.is_desktop():
            import pygame
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
        self.locked_mouse = False
        
