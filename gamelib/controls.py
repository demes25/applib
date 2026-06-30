import pygame as pg 
from pygame.locals import *
from typing import Protocol, runtime_checkable, Any, Callable

Event = pg.event.Event
events = pg.event.get 


def standard_global_handler(event : Event, _ : list[Any]):
    if event.type == QUIT:
        quit()
    
@runtime_checkable
class Controllable(Protocol):

    def handle(event : Event, queue : list[Any]):
        ...


def controller(global_handler = standard_global_handler) -> Callable[[Controllable], list[Any]]:
    def process(controllable : Controllable):
        results = []
        for event in events():
            global_handler(event, results)
            controllable.handle(event, results)
        return results
    return process