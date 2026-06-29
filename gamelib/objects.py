# Demetre Seturidze
# GameLib
# Objects and Structures

from typing import Any, Union, Iterable, TYPE_CHECKING, Callable
from abc import ABC, abstractmethod
from gamelib.utils import Surface, Coords, new_surface, add, sub, mins, maxs, fill, phase
from gamelib.colors import Color


RECT_ATTRS = ('topleft', 'topright', 'bottomleft', 'bottomright', 'right', 'left', 'top', 'bottom', 'center', 'width', 'height')

# wraps a surface to be able to blit/move easier.
# also makes registering hits easier.
class Object:
    '''A wrapper for PyGame surfaces. Essentially couples a surface with a position. Allows direct access to rect attributes and defines
    some auxiliary functions such to manipulate the surface.
    
    This also allows the definition of group Objects (Objects that hold other Objects) that may be used to simultanenously manipulate child Objects.
    In this paradigm, each Object's position is measured from the topleft point of the group Object (called "Structure") that contains it (referred to internally as "origin").
    The screen is the global Object, and its topleft point is (0, 0).

    Therefore, each Object is equipped with two functions to convert between global coordinates (relative to the topleft of the screen) and local coordinates (relative to the topleft of the immediately encompassing Structure).
    The position of any Object is stored relative to the topleft of its immediately encompassing Structure.
    '''
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
        height : int 
        width : int
        midpoint : Coords
        

    def __init__(
        self, 
        surface_or_shape : Surface | Coords, 

        origin : Coords = (0, 0) # the origin of the containing environment. by default, (0, 0)
    ):
        '''Parameters
        ----------
            surface_or_shape : Surface | Coords
                The Surface to wrap, or a set of coordinates denoting the size of the desired surface. If passed coordinates,
                creates a transparent Surface of the given width and height.
            origin : Coords
                The global coordinate of the topleft point of the Structure that stores this Object. By default set to (0, 0) (the topleft of the screen window).
        '''
        if isinstance(surface_or_shape, Surface):
            surface = surface_or_shape
        else:
            surface = new_surface(surface_or_shape)

        self.surface = surface 
        self.rect = surface.get_rect()
        self.origin = origin

        self.midpoint = (self.rect.width // 2, self.rect.height // 2)

        self.__container__ = None

        super().__init__()
    

    # we make it so that any reference to the edges of the surface points immediately through self.rect
    def __getattr__(self, name : str) -> Any:
        if name in RECT_ATTRS:
            return getattr(self.rect, name)
        elif name == 'shape':
            return self.rect.size
        raise AttributeError(name)
    
    def __setattr__(self, name: str, value: Any):
        if name in ('shape', 'width', 'height'):
            raise PermissionError(f'Attribute {name} is immutable.')
        elif name in RECT_ATTRS:
            setattr(self.rect, name, value)
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


    def global_to_local(self, coords : Coords) -> Coords:
        '''Takes the given global coordinates (relative to the topleft of the screen) to a set of local coordinates (relative to the topleft of the immediately encompassing Structure).
        
        Parameters
        ----------
            coords : Coords
                The set of global coordinates.
        
        Returns
        -------
            >>> sub(coords, self.origin)
        '''        
        return sub(coords, self.origin)

    def local_to_global(self, coords : Coords) -> Coords:   
        '''Takes the given local coordinates (relative to the topleft of the immediately encompassing Structure) to a set of global coordinates (relative to the topleft of the screen).
        
        Parameters
        ----------
            coords : Coords
                The set of local coordinates.
            
        Returns
        -------
            >>> add(coords, self.origin)
        '''     
        return add(coords, self.origin)

    
    def phase(self, color : Color):
        '''Multiplies the RGBA values of the this Object by those of the given Color.

        Parameters
        ----------
            color : Color
                The color to phase with.
        '''
        self.surface = phase(self.surface, color)
    
    def tint(self, color : Color):
        '''Tints this Object with the given Color. 

        Essentially, blits a surface filled with the given color onto this Object.

        Parameters
        ----------
            color : Color
                The color to tint with.
        '''
        _tinter = new_surface(self.rect.size)
        _tinter.fill(color.rgba)
        self.surface.blit(_tinter, (0, 0))

    def fill(self, color : Color):
        '''Fills this Object with the given color.
        
        Parameters
        ----------
            color : Color 
                The color to fill with.
        '''
        self.surface = fill(self.surface, color)

    def shift(self, displacement : Coords):
        '''Moves the topleft of this Object by the given displacement.
        
        Parameters
        ----------
            displacement : Coords
                The difference between the desired position and the current position.
        '''
        self.rect.topleft = add(self.rect.topleft, displacement)


    # returns true if both (or the one given) sets of coordinates collide with this object
    
    def hits(self, coords : Coords, prev_coords : Coords | None = None, from_global : bool = True) -> bool:
        '''Whether or not the given set of coordinates collide with this Object. If prev_coords is given, checks if both
        sets of coordinates collide with this Object. If the immediate encompassing Structure is a View, ensures that the given coordinates also hit the View.
        
        Parameters
        ----------
            coords : Coords 
                The set of coordinates to check.
            
            prev_coords : Coords | None 
                If not None, essentially returns 

                >>> hits(coords) and hits(prev_coords)
            
            from_global : bool
                Whether the given coordinates are global (relative to the topleft of the screen).
        
        Returns
        -------
            True if the given coordinates collide with this Object, False otherwise.
        '''

        if prev_coords is None:
            if from_global:
                coords = self.global_to_local(coords)

            if isinstance(self.__container__, View):
                coords_in_bound = (
                    0 <= coords[0] <= self.__container__.rect.width
                    and 
                    0 <= coords[1] <= self.__container__.rect.height
                )
                if not coords_in_bound:
                    return False        
            
            return self.rect.collidepoint(coords)
       
        else:
            # we transmit to local coordinates by default
            if from_global:
                coords = self.global_to_local(coords)
                prev_coords = self.global_to_local(prev_coords)

            if isinstance(self.__container__, View):
                coords_in_bound = (
                    0 <= coords[0] <= self.__container__.rect.width
                    and 
                    0 <= coords[1] <= self.__container__.rect.height
                )

                prev_in_bound = (
                    0 <= prev_coords[0] <= self.__container__.rect.width
                    and 
                    0 <= prev_coords[1] <= self.__container__.rect.height
                )

                if not (coords_in_bound and prev_in_bound):
                    return False

            return self.rect.collidepoint(coords) and self.rect.collidepoint(prev_coords)
    

    def blit_onto(self, dest : Union['Object', Surface]):
        '''Blits this object onto the given Object or Surface. Manipulates the destination Surface/Object in-place.
        
        Parameters
        ----------
            dest : Object | Surface
                The destination to blit onto.
        '''
        if isinstance(dest, Object):
            dest.surface.blit(self.surface, self.rect)
        else:
            dest.blit(self.surface, self.rect)



# an object that contains other objects, adjusts origins, etc.
class Structure(Object, ABC):
    '''An Object that holds other Objects and may simultanenously manipulate them.

    Each time that the position of this Structure is changed, the origins of its contained Objects are recursively updated.
    '''
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
        if displacement != (0, 0):
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
        val.__container__ = self

    # sets the origin of a list of newly adding internal objects
    def _wrap_arr(self, vals : Iterable[Object]):
        for val in vals:
            val._set_origin(self._global_topleft)
            val.__container__ = self


    def __setattr__(self, name: str, value: Any):
        # if the value is a RECT_EDGE, we adjust this rect and then adjust origins     
        if name in ('shape', 'width', 'height'):
            raise PermissionError(f'Attribute {name} is immutable.')
        elif name in RECT_ATTRS:
            if value != getattr(self.rect, name):
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
        '''Multiplies the RGBA values of the this Object by those of the given Color. If given a nonzero recursion depth, phases child objects as well.

        Parameters
        ----------
            color : Color
                The color to phase with.
            recursion_depth : int
                If 0, only tints this Object. If a positive integer n, recursively phases this Object and contained Objects up to n layers down.
                If a negative integer, recursively phases all contained Objects.
        '''
        return self._recurse_color_func(Object.phase, color, recursion_depth)
    
    def tint(self, color : Color, recursion_depth : int = 0):
        '''Tints this Object with the given Color. If given a nonzero recursion depth, tints child objects as well. 

        Essentially, blits a surface filled with the given color onto this Object.

        Parameters
        ----------
            color : Color
                The color to tint with.
            recursion_depth : int
                If 0, only tints this Object. If a positive integer n, recursively tints this Object and contained Objects up to n layers down.
                If a negative integer, recursively tints all contained Objects.
        '''
        return self._recurse_color_func(Object.tint, color, recursion_depth)

    def fill(self, color : Color, recursion_depth : int = 0):
        '''Fills this Object with the given color. If given a nonzero recursion depth, fills child objects as well.
        
        Parameters
        ----------
            color : Color 
                The color to fill with.
            recursion_depth : int
                If 0, only fills this Object. If a positive integer n, recursively fills this Object and contained Objects up to n layers down.
                If a negative integer, recursively fills all contained Objects.
        '''
        return self._recurse_color_func(Object.fill, color, recursion_depth)

    
    def shift(self, displacement : Coords):
        '''Moves the topleft of this Object by the given displacement. Adjusts the origins of all contained Objects.
        
        Parameters
        ----------
            displacement : Coords
                The difference between the desired position and the current position.
        '''
        if displacement != (0, 0):
            super().shift(displacement)
            self._global_topleft = add(self._global_topleft, displacement)
            
            for internal in self._internal_iter:
                internal._shift_origin(displacement)

    def blit_onto(self, dest : Union['Object', Surface]):
        '''Recursively (layer by layer, each layer in the order of definition) blits this Object and its contained Objects onto the given Object or Surface.
        Manipulates the destination Surface/Object in-place.
        
        Parameters
        ----------
            dest : Object | Surface
                The destination to blit onto.
        '''
        surface = self.surface.copy()

        for internal in self._internal_iter:
            internal.blit_onto(surface)
        
        if isinstance(dest, Object):
            dest.surface.blit(surface, self.rect)
        else:
            dest.blit(surface, self.rect)


class View(Structure):
    '''An Structure that holds a "view" on another Object.
    '''
    def __init__(
        self,
        surface_or_shape : Surface | Coords,
        item : Object,
        origin : Coords = (0, 0)
    ):
        '''Parameters
        ----------
            surface_or_shape : Surface | Coords
                The Surface to wrap, or a set of coordinates denoting the size of the desired surface. If passed coordinates,
                creates a transparent Surface of the given width and height.
            item : Object
                The Object to hold a view on.
            origin : Coords
                The global coordinate of the topleft point of the Structure that stores this Object. By default set to (0, 0) (the topleft of the screen window).
        '''
        super().__init__(surface_or_shape, origin=origin)
        self._global_topleft = add(origin, self.rect.topleft)
        
        self.item = item
    
    @property
    def _internal_iter(self) -> Iterable[Object]:
        return (self.item,)
    
    @property
    def _max_disp(self) -> Coords:
        return (
            -self.item.rect.left,
            -self.item.rect.top
        )

    @property
    def _min_disp(self) -> Coords:
        return (
            self.rect.width - self.item.rect.right,
            self.rect.height - self.item.rect.bottom,
        )


    def __setattr__(self, name: str, value: Any):
        # if the value is item, wraps first.    
        if name == 'item':
            self._wrap(value)
            object.__setattr__(self, name, value)
        else:
            Structure.__setattr__(self, name, value)

        
    def scroll(self, displacement : Coords):
        '''Moves the viewed item by the given displacement, but confines the view to be within bounds of the viewed item.
        
        Parameters
        ----------
            displacement : Coords
                The difference between the desired item position and the current item position.
        '''
        confined = mins(
            self._max_disp,
            maxs(
                self._min_disp, 
                displacement
            )
        )
    
        self.item.shift(confined)
    

        



from collections import UserList, UserDict

# an array that contains other objects, adjusts origins, etc.
# stores contained objects in a list.
class Array(Structure, UserList[Object]):
    '''A Structure that holds a list of Objects.
    '''
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
        '''The index of the Object in this list that is hit by the given sets of coordinates. Returns -1 if none of the contained Objects are hit.
        
        Parameters
        ----------
            coords : Coords 
                The set of coordinates to check. If prev_coords is None, returns
                
                >>> i s.t. self[i].hits(coords) or -1
            
            prev_coords : Coords | None 
                If not None, returns 
                
                >>> i s.t. self[i].hits(coords, prev_coords) or -1
            
            from_global : bool
                Whether the given coordinates are global (relative to the topleft of the screen).
        
        Returns
        -------
        >>> i s.t. self[i].hits(coords, prev_coords, from_global).

        If the given coordinates don't hit any of the contained Objects, returns -1.
        '''
        # we transmit to local coordinates by default
        if from_global:
            coords = self.global_to_local(coords)
            if prev_coords is not None:
                prev_coords = self.global_to_local(prev_coords)
        
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
    '''A Structure that holds a dictionary of Objects.
    '''
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
        '''The name of the Object in this dictionary that is hit by the given sets of coordinates. Returns None if none of the contained Objects are hit.
        
        Parameters
        ----------
            coords : Coords 
                The set of coordinates to check. If prev_coords is None, returns
                
                >>> name s.t. self[name].hits(coords) or None
            
            prev_coords : Coords | None 
                If not None, returns 
                
                >>> name s.t. self[name].hits(coords, prev_coords) or None
            
            from_global : bool
                Whether the given coordinates are global (relative to the topleft of the screen).
        
        Returns
        -------
        >>> name s.t. self[name].hits(coords, prev_coords, from_global).
            
        If the given coordinates don't hit any of the contained Objects, returns None.
        '''
        # we transmit to local coordinates by default
        if from_global:
            coords = self.global_to_local(coords)
            if prev_coords is not None:
                prev_coords = self.global_to_local(prev_coords)
        
        # we transmit to internal local coordinates
        coords = sub(coords, self.rect.topleft)
        if prev_coords is not None:
            prev_coords = sub(prev_coords, self.rect.topleft)

        for key, internal in self.data.items():
            if internal.hits(coords, prev_coords, from_global=False):
                return key 
        
        return None