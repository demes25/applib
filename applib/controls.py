import pygame as pg 
from typing import Generic, TypeVar, Protocol, runtime_checkable
from abc import ABC, abstractmethod
import time

EventUI = pg.event.Event
fetch = pg.event.get 

T = TypeVar('T')

class Controllable(ABC, Generic[T]):

    def _quit(self, queue : list[T]):
        quit()
    
    def global_handle(self, event : EventUI, queue : list[T]):
        if event.type == pg.QUIT:
            self._quit(queue)
    
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
    def enfocus(self):
        ...

    def defocus(self):
        ...


from .utils import Surface, Coords, Vector, ZERO_VEC
from typing import Iterator, Any
from .objects import View, Array, Object, Structure
    
class Scrollable(View, Controllable[T]):
    def __init__(
        self,
        surface_or_shape : Surface | Coords,
        item : Object,
        margins : Coords = (0, 0),
        velocity : float = 3.0,
        origin : Vector = ZERO_VEC
    ):
        super().__init__(surface_or_shape=surface_or_shape, item=item, margins=margins, origin=origin)

        self.velocity = velocity
        self.frozen = False

    def freeze(self):
        self.frozen = True

    def unfreeze(self):
        self.frozen = False 

    def enfocus(self):
        if isinstance(self.item, Focusable):
            self.item.enfocus()

    def defocus(self):
        if isinstance(self.item, Focusable):
            self.item.defocus()


    def handle(self, event : EventUI, queue : list[T]):
        if event.type == pg.MOUSEWHEEL and not self.frozen:
            displacement = self.velocity * Vector((event.x, event.y))
        else:
            displacement = Vector(0)

        if isinstance(self.item, Controllable):
            self.item.handle(event, queue)

        self.scroll(displacement)


    
class FocusContainer(Array, Controllable[T]):
    def __init__(
            self, 
            surface_or_shape : Surface | Coords,

            respond_to_click : bool = True,
            respond_to_wheel : bool = True,

            origin : Vector = ZERO_VEC
        ):
            super().__init__(surface_or_shape, origin=origin)
            self.focus = None

            self._to_click = respond_to_click
            self._to_wheel = respond_to_wheel

            self.temporary : list[tuple[Object, float, float]] = []

    def __iter__(self):
        yield from super().__iter__()
        self.drain_temps()

    def drain_temps(self):
        active_items = []
        inactive_items = []
        for tup in self.temporary:
            temp, creation_time, lifespan = tup
            if (time.time() - creation_time) >= lifespan:
                inactive_items.append(temp)
            else:
                active_items.append(tup)

        self.temporary = active_items

        for i in inactive_items:
            self.remove(i)
        
    def append_temp(self, obj : Object, lifespan : float):
        self.append(obj)
        #TODO: maybe this should be less roundabout.
        # currently temporary objects are additionally kept inside a separate array along with creation_time/lifespan. maybe incorporate into protocol.
        self.temporary.append((
            obj, time.time(), lifespan
        ))

    def enfocus(self):
        if isinstance(self.focus, Focusable):
            self.focus.enfocus()

    def defocus(self):
        self.mediate_focus(None)
        
    def mediate_focus(self, focus):
        if focus is not self.focus:
            if isinstance(self.focus, Focusable):
                self.focus.defocus()
                
            self.focus = focus
            if focus is not None and len(self.data) > 1:
                self.data.remove(focus)
                self.data.append(focus)
            
        if isinstance(focus, Focusable):
            focus.enfocus()
        

    def adjust_focus(self, coords : Coords, from_global : bool = True):
        focus_key = self.which_hits(coords, from_global=from_global)

        if focus_key < 0:
            self.mediate_focus(None)
            return
        
        self.mediate_focus(self[focus_key])


        

    # handles the event.
    # subhandlers are defined above for text, ingame, game_over, and promotion environments    
    def handle(self, event : EventUI, queue : list[T]):
        if event.type == pg.MOUSEBUTTONDOWN and event.button <= 3 and self._to_click:
            self.adjust_focus(event.pos)

        if event.type == pg.MOUSEWHEEL and self._to_wheel:
            self.adjust_focus(pg.mouse.get_pos()) 
        
        if event.type == pg.MOUSEBUTTONUP and event.button <= 3 and self.focus is not None and not self.focus.hits(event.pos):
            self.mediate_focus(None)
        
        if self.focus is not None and isinstance(self.focus, Controllable):
            self.focus.handle(event, queue)

