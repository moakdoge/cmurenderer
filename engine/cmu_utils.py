
import random
import sys
from typing import TYPE_CHECKING, Literal

from cmu_graphics import rgb
if TYPE_CHECKING:
    from engine._game import Game
    from cmu_graphics.shape_logic import RGB
    

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


        
        
    def make_global(self, name=None, desktop: bool = True, web: bool = True):
        def decorator(func):
            def wrapper(*args, **kwargs):

                return CMUtils._game.__class__.__dict__[func.__name__](
                    CMUtils._game,
                    *args,
                    **kwargs
                )

            if not desktop and self.is_desktop():
                return func
            if not web and self.is_web():
                return func
            
        
            self._globals[name or func.__name__] = wrapper
            return func

        return decorator
    
    

    @staticmethod
    def is_web() -> Literal[False]:
        return (sys.implementation.name == "brython")  or "__BRYTHON__" in globals() # type: ignore

    @staticmethod
    def is_desktop() -> Literal[True]:
        return (sys.implementation.name == "cpython")# pyright: ignore[reportReturnType]
    
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
        

    def random_color(self) -> "RGB":
        rng1, rng2, rng3 = random.randint(0,255),random.randint(0,255),random.randint(0,255)
        return rgb(rng1, rng2, rng3)
    
    @property
    def backend_url(self):
        if self.is_web():
            return "https://backend.academy.cs.cmu.edu/get-image/?url="
        return ""