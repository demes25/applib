import pygame as pg 
from typing import Generic, TypeVar, Protocol, runtime_checkable
from abc import ABC, abstractmethod

EventUI = pg.event.Event
fetch = pg.event.get 

T = TypeVar('T')

class Controllable(ABC, Generic[T]):

    def _quit(self):
        quit()
    
    def global_handle(self, event : EventUI, queue : list[T]):
        result = None 
        if event.type == pg.QUIT:
            result = self._quit()
        
        if result is not None:
            queue.append(result)
    
    @abstractmethod
    def handle(self, event : EventUI, queue : list[T]):
        pass

    def process(self, events) -> list[T]:
        results = []

        for event in events:
            self.global_handle(event, results)
            self.handle(event, results)
        
        return results 


@runtime_checkable
class Focusable(Protocol):
    def focus(self):
        ...

    def defocus(self):
        ...


from .utils import Surface, Coords, Vector, ZERO_VEC
from .objects import Array

class Interface(Array, Controllable[T]):
    def __init__(
            self, 
            surface_or_shape : Surface | Coords,
            origin : Vector = ZERO_VEC
        ):
            super().__init__(surface_or_shape, origin=origin)


    def adjust_focus(self, coords : Coords, from_global : bool = True):
        focus_key = self.which_hits(coords, from_global=from_global)

        if focus_key is None:
            self.focus = None 
            return
        
        focus = self[focus_key]

        if not isinstance(focus, Controllable):
            #self.data.remove(focus)
            #self.data.append(focus)
            self.focus = None 
            return 
        
        if focus is not self.focus:
            if isinstance(self.focus, Focusable):
                self.focus.defocus()
                
            self.focus = focus
            # self.data.remove(focus)
            # self.data.append(focus)
            
            if isinstance(focus, Focusable):
                focus.focus()
        

    # handles the event.
    # subhandlers are defined above for text, ingame, game_over, and promotion environments    
    def handle(self, event : EventUI, queue : list[T]):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.adjust_focus(event.pos)
        
        if event.type == pg.MOUSEBUTTONUP and self.focus is not None and not self.focus.hits(event.pos):
            self.focus = None
        
        if self.focus is not None:
            self.focus.handle(event, queue)


