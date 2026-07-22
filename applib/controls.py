import pygame as pg 
from typing import Generic, TypeVar
from abc import ABC, abstractmethod

EventUI = pg.event.Event
fetch = pg.event.get 

T = TypeVar('T')

class Controllable(ABC, Generic[T]):
    def global_handle(self, event : EventUI, _ : list[T]):
        if event.type == pg.QUIT:
            quit()
    
    @abstractmethod
    def handle(self, event : EventUI, queue : list[T]):
        pass

    def process(self, events) -> list[T]:
        results = []

        for event in events:
            self.global_handle(event, results)
            self.handle(event, results)
        
        return results 


