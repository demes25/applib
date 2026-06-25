# Demetre Seturidze
# GameLib
# Objects and Structures

from typing import Any, Union, Iterable
from abc import ABC, abstractmethod
from collections import UserList
from gamelib.utils import Surface, Coords, new_surface, add, sub 


RECT_EDGES = ['topleft', 'topright', 'bottomleft', 'bottomright', 'right', 'left', 'top', 'bottom', 'center']

# wraps a surface to be able to blit/move easier.
# also makes registering hits easier.
class Object:
    def __init__(
        self, 
        surface_or_shape : Surface | Coords, 

        origin : Coords = (0, 0) # the origin of the containing environment. by default, (0, 0)
    ):
        if isinstance(surface_or_shape, Surface):
            surface = surface_or_shape
        else:
            surface = new_surface(surface_or_shape)

        self.surface = surface 
        self.rect = surface.get_rect()
        self.origin = origin

        super().__init__()


    # we set the origin.
    # this is called under-the-hood for environments
    def _set_origin(self, origin : Coords = (0, 0)):
        self.origin = origin
    
    def _shift_origin(self, shift : Coords = (0, 0)):
        self.origin = add(self.origin, shift)


    # we make it so that any reference to the edges of the surface points immediately through self.rect
    
    def __getattr__(self, name : str) -> Any:
        if name in RECT_EDGES:
            return getattr(self.rect, name)
        raise AttributeError(name)
    
    def __setattr__(self, name: str, value: Any):
        if name in RECT_EDGES:
            setattr(self.rect, name, value)
        else:
            object.__setattr__(self, name, value)
    

    # convert coordinates

    def _global_to_local(self, coords : Coords) -> Coords:        
        return (
            coords[0] - self.origin[0],
            coords[1] - self.origin[1]
        )

    def _local_to_global(self, coords : Coords) -> Coords:        
        return (
            coords[0] + self.origin[0],
            coords[1] + self.origin[1]
        )

        
    # returns true if both (or the one given) sets of coordinates collide with this object
    
    def hits(self, coords : Coords, prev_coords : Coords | None = None, from_global : bool = True) -> bool:
        # we transmit to local coordinates by default
        if from_global:
            coords = self._global_to_local(coords)
            if prev_coords is not None:
                prev_coords = self._global_to_local(prev_coords)

        if prev_coords is None:
            return self.rect.collidepoint(coords)
        else:
            return self.rect.collidepoint(coords) and self.rect.collidepoint(prev_coords)
    
    def blit_onto(self, dest : Union['Object', Surface]):
        if isinstance(dest, Object):
            dest.surface.blit(self.surface, self.rect)
        else:
            dest.blit(self.surface, self.rect)



'''
# wraps a "view" on an object.
class View(Object):
    def __init__(vw, view_dims : TileCoords, scroll_speed : int = 1, reference : Surface | None = None, reference_topleft = (0, 0), center : Coords | None = None):
        vw.view_dims = view_dims
        vw.view_pixels = self.tiles_to_pixels(view_dims)

        vw.scroll_speed = scroll_speed

        # by default, we start with the view at the top-left of the given surface
        vw.MAX_TOP = 0
        vw.MAX_LEFT = 0
        
        vw.MIN_TOP = 0
        vw.MAX_TOP = 0

        vw._left, vw._top = reference_topleft
        
        view_surface = new_surface(vw.view_pixels)
        super().__init__(view_surface, center=center)

        if reference is None:
            vw.reference = None 
        else:
            vw.set_reference(reference)


    # restricts the view to be within bounds.
    # returns False if all is well and nothing needed to be corrected,
    # True otherwise
    def restrict(vw) -> bool:
        corrected = False 

        if vw._top > 0:
            vw._top = 0
            corrected = True

        if vw._top < vw.MIN_TOP:
            vw._top = vw.MIN_TOP
            corrected = True 

        if vw._left > 0:
            vw._left = 0
            corrected = True 
        
        if vw._left < vw.MIN_LEFT:
            vw._left = vw.MIN_LEFT
            corrected = True 
        
        return corrected

    
    def flip(vw):
        vw.surface = new_surface(vw.view_pixels)
        vw.surface.blit(vw.reference, (vw._left, vw._top))

    def set_reference(vw, reference : Surface):
        vw.reference = reference
        back_rect = reference.get_rect()

        back_width = back_rect.width 
        back_height = back_rect.height 

        vw.MAX_TOP = max(0, vw.rect.height - back_height)
        vw.MAX_LEFT = max(0, vw.rect.width - back_width)
        vw.MIN_TOP = min(-back_height + vw.rect.height, 0)
        vw.MIN_LEFT = min(-back_width + vw.rect.width, 0)

        vw.restrict()
        vw.flip()
    
    # returns True if restrict returns True
    # by defaults restricts the view to be contained within 
    def scroll(vw, dx : int = 0, dy : int = 0, restrict : bool = True) -> bool:
        vw._left -= dx 
        vw._top -= dy 

        corrected = vw.restrict() if restrict else False

        vw.flip()

        return corrected
        
'''


# an object that contains other objects, adjusts origins, etc.
class Structure(Object, ABC):
    def __init__(
        self,
        surface_or_shape : Surface | Coords,
        origin : Coords = (0, 0)
    ):
        super().__init__(surface_or_shape, origin=origin)
    
    @property
    @abstractmethod
    def _internal_iter(self) -> Iterable[Object]:
        pass 


    def _shift_origin(self, shift : Coords = (0, 0)):
        super()._shift_origin(shift)
        for internal in self._internal_iter:
            internal._shift_origin(shift)

    def _set_origin(self, origin : Coords = (0, 0)):   
        shift = sub(origin, self.origin)
        self._shift_origin(shift)
    

    # sets the origin of a newly adding internal object
    def _wrap(self, val : Object):
        new_origin = add(self.origin, self.rect.topleft)
        val._set_origin(new_origin)

    # sets the origin of a list of newly adding internal objects
    def _wrap_arr(self, vals : Iterable[Object]):
        new_origin = add(self.origin, self.rect.topleft)
        for val in vals:
            val._set_origin(new_origin)


    def __setattr__(self, name: str, value: Any):
        # if the value is a RECT_EDGE, we adjust this rect and then adjust origins     
        if name in RECT_EDGES:
            old_origin = self.rect.topleft 
            setattr(self.rect, name, value)
            new_origin = self.rect.topleft 

            shift = sub(new_origin, old_origin)
            for internal in self._internal_iter:
                internal._shift_origin(shift)
        else:
            object.__setattr__(self, name, value)
    

    def blit_onto(self, dest : Union['Object', Surface]):
        surface = self.surface.copy()

        for internal in self._internal_iter:
            internal.blit_onto(surface)
        
        if isinstance(dest, Object):
            dest.surface.blit(surface, self.rect)
        else:
            dest.blit(surface, self.rect)

    

# an array that contains other objects, adjusts origins, etc.
# stores contained objects in a list.
class Array(Structure):
    def __init__(
        self,
        surface_or_shape : Surface | Coords,
        origin : Coords = (0, 0)
    ):
        super().__init__(surface_or_shape, origin=origin)

        self._internals : list[Object] = []

    @property
    def _internal_iter(self) -> Iterable[Object]:
        return self._internals
    

    def __len__(self):
        return len(self._internals)

    def __getitem__(self, key : int):
        return self._internals[key]

    # internal objects are blitted in the order of self._internals
    def __setitem__(self, key : int, val : Object):
        self._wrap(val)
        self._internals[key] = val 

    def append(self, val : Object):
        self._wrap(val)
        self._internals.append(val)
    
    def extend(self, vals : Iterable[Object]):
        self._wrap_arr(vals)
        self._internals.extend(vals)

    def insert(self, key : int, val : Object):
        self._wrap(val)
        self._internals.insert(key, val)
    

    # returns the index of the hit object. -1 if none hits.
    def which_hits(self, coords : Coords, prev_coords : Coords | None, from_global : bool = True) -> int:
        # we transmit to local coordinates by default
        if from_global:
            coords = self._global_to_local(coords)
            if prev_coords is not None:
                prev_coords = self._global_to_local(prev_coords)
        
        # we transmit to internal local coordinates
        coords = sub(coords, self.rect.topleft)
        if prev_coords is not None:
            prev_coords = sub(prev_coords, self.rect.topleft)

        for index, internal in enumerate(self._internals):
            if internal.hits(coords, prev_coords, from_global=False):
                return index 
        
        return -1 



# an environment which contains other objects, adjusts origins, etc
# stores contained objects in a dict (mutable).
class Environment(Structure):
    def __init__(
        self, 
        surface_or_shape : Surface | Coords,
        origin : Coords = (0, 0)
    ):
        super().__init__(surface_or_shape, origin=origin)

        self._internals : dict[str, Object] = {} # the internal objects in this environment


    @property
    def _internal_iter(self) -> Iterable[Object]:
        return self._internals.values()

    # if we look up an internal object, we accommodate   
    def __getattr__(self, name : str):
        try:
            return super().__getattr__(name)
        except AttributeError:
            _internal = self._internals.get(name, None)
            if _internal is None:
                raise
            else:
                return _internal 
    
    # internal objects are blitted in order of definition
    def __setattr__(self, name: str, value: Any):
        # if the value is an Object, we need to add it to the internals and adjust its origin
        if isinstance(value, Object):
            self._wrap(value)
            self._internals[name] = value 
        # if the value is a RECT_EDGE, we adjust this rect and then adjust origins     
        else:
            super().__setattr__(name, value)
    

    # returns the key of the hit object. None if none hits
    def which_hits(self, coords : Coords, prev_coords : Coords | None, from_global : bool = True) -> str | None:
        # we transmit to local coordinates by default
        if from_global:
            coords = self._global_to_local(coords)
            if prev_coords is not None:
                prev_coords = self._global_to_local(prev_coords)
        
        # we transmit to internal local coordinates
        coords = sub(coords, self.rect.topleft)
        if prev_coords is not None:
            prev_coords = sub(prev_coords, self.rect.topleft)

        for key, internal in self._internals.items():
            if internal.hits(coords, prev_coords, from_global=False):
                return key 
        
        return None