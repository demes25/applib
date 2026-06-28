# Demetre Seturidze
# GameLib
# Objects and Structures

from typing import Any, Union, Iterable, TYPE_CHECKING, Callable
from abc import ABC, abstractmethod
from gamelib.utils import Surface, Coords, new_surface, add, sub, fill, phase
from gamelib.colors import Color


RECT_EDGES = ['topleft', 'topright', 'bottomleft', 'bottomright', 'right', 'left', 'top', 'bottom', 'center']

# wraps a surface to be able to blit/move easier.
# also makes registering hits easier.
class Object:
    if TYPE_CHECKING:
        topleft : Coords
        topright : Coords 
        bottomleft : Coords
        bottomright : Coords

        center : Coords

        right : int 
        left : int 
        top : int 
        bottom : int 

        shape : Coords
        

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
    

    # we make it so that any reference to the edges of the surface points immediately through self.rect
    def __getattr__(self, name : str) -> Any:
        if name in RECT_EDGES:
            return getattr(self.rect, name)
        elif name == 'shape':
            return self.rect.size
        raise AttributeError(name)
    
    def __setattr__(self, name: str, value: Any):
        if name in RECT_EDGES:
            setattr(self.rect, name, value)
        elif name == 'shape':
            raise PermissionError('Unable to alter object')
        else:
            object.__setattr__(self, name, value)


    def _recurse_color_func(self, _color_func : Callable[['Object', Color], None], color : Color, recursion_depth : int = 0):
        _color_func(self, color)

    # we set the origin.
    # this is called under-the-hood for environments
    def _set_origin(self, origin : Coords = (0, 0)):
        self.origin = origin
    
    def _shift_origin(self, displacement : Coords):
        self.origin = add(self.origin, displacement)


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

    
    def phase(self, color : Color):
        self.surface = phase(self.surface, color)
    
    def tint(self, color : Color):
        _tinter = new_surface(self.rect.size)
        _tinter.fill(color.rgba)
        self.surface.blit(_tinter, (0, 0))

    def fill(self, color : Color):
        self.surface = fill(self.surface, color)

    def shift(self, displacement : Coords):
        self.rect.topleft = add(self.rect.topleft, displacement)


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
        self._global_topleft = add(origin, self.rect.topleft)
    
    @property
    @abstractmethod
    def _internal_iter(self) -> Iterable[Object]:
        pass 

    def _shift_origin(self, displacement : Coords):
        self._global_topleft = add(self._global_topleft, displacement)
        super()._shift_origin(displacement)

        for internal in self._internal_iter:
            internal._shift_origin(displacement)

    def _set_origin(self, origin : Coords = (0, 0)):  
        self._global_topleft = add(origin, self.rect.topleft)

        shift = sub(origin, self.origin)
        self._shift_origin(shift)


    def _recurse_color_func(self, _color_func : Callable[['Object', Color], None], color : Color, recursion_depth : int = 0):
        _color_func(self, color)
        if recursion_depth != 0:
            for internal in self._internal_iter:
                internal._recurse_color_func(_color_func, color, recursion_depth-1)


    # sets the origin of a newly adding internal object
    def _wrap(self, val : Object):
        val._set_origin(self._global_topleft)

    # sets the origin of a list of newly adding internal objects
    def _wrap_arr(self, vals : Iterable[Object]):
        for val in vals:
            val._set_origin(self._global_topleft)


    def __setattr__(self, name: str, value: Any):
        # if the value is a RECT_EDGE, we adjust this rect and then adjust origins     
        if name in RECT_EDGES:
            old_tl = self.rect.topleft 
            setattr(self.rect, name, value)
            new_tl = self.rect.topleft 
    
            displacement = sub(new_tl, old_tl)
            self._global_topleft = add(self._global_topleft, displacement)
            
            for internal in self._internal_iter:
                internal._shift_origin(displacement)
        else:
            object.__setattr__(self, name, value)

    
    def phase(self, color : Color, recursion_depth : int = 0):
        return self._recurse_color_func(Object.phase, color, recursion_depth)
    
    def tint(self, color : Color, recursion_depth : int = 0):
        return self._recurse_color_func(Object.tint, color, recursion_depth)

    def fill(self, color : Color, recursion_depth : int = 0):
        return self._recurse_color_func(Object.fill, color, recursion_depth)

    
    def shift(self, displacement : Coords):
        super().shift(displacement)
        self._global_topleft = add(self._global_topleft, displacement)
        
        for internal in self._internal_iter:
            internal._shift_origin(displacement)

    def blit_onto(self, dest : Union['Object', Surface]):
        surface = self.surface.copy()

        for internal in self._internal_iter:
            internal.blit_onto(surface)
        
        if isinstance(dest, Object):
            dest.surface.blit(surface, self.rect)
        else:
            dest.blit(surface, self.rect)

    
from collections import UserList, UserDict

# an array that contains other objects, adjusts origins, etc.
# stores contained objects in a list.
class Array(Structure, UserList[Object]):
    def __init__(
        self,
        surface_or_shape : Surface | Coords,
        origin : Coords = (0, 0)
    ):
        super().__init__(surface_or_shape, origin=origin)
        UserList.__init__(self)


    @property
    def _internal_iter(self) -> Iterable[Object]:
        return self.data

    # internal objects are blitted in the order of self.data
    def __setitem__(self, key : int, val : Object):
        assert isinstance(key, int)

        self._wrap(val)
        self.data[key] = val 

    def __iadd__(self, vals : Iterable[Object]):
        vals = list(vals)
        self._wrap_arr(vals)
        self.data.extend(vals)
        return self

    def append(self, val : Object):
        self._wrap(val)
        self.data.append(val)
    
    def extend(self, vals : Iterable[Object]):
        vals = list(vals)
        self._wrap_arr(vals)
        self.data.extend(vals)

    def insert(self, key : int, val : Object):
        self._wrap(val)
        self.data.insert(key, val)
    

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

        for index, internal in enumerate(self.data):
            if internal.hits(coords, prev_coords, from_global=False):
                return index 
        
        return -1 



# an environment which contains other objects, adjusts origins, etc
# stores contained objects in a dict (mutable).
class Environment(Structure, UserDict[str, Object]):
    def __init__(
        self, 
        surface_or_shape : Surface | Coords,
        origin : Coords = (0, 0)
    ):
        super().__init__(surface_or_shape, origin=origin)
        UserDict.__init__(self)

    @property
    def _internal_iter(self) -> Iterable[Object]:
        return self.data.values()

    # internal objects are blitted in the order of self._internals
    def __setitem__(self, key : str, val : Object):
        self._wrap(val)
        self.data[key] = val
     
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

        for key, internal in self.data.items():
            if internal.hits(coords, prev_coords, from_global=False):
                return key 
        
        return None