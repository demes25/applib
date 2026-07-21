# Demetre Seturidze
# AppLib
# Objects and Structures

from typing import Any, Union, Iterable, Iterator, TYPE_CHECKING, Callable, Literal
from abc import ABC, abstractmethod

from .utils import Surface, Coords, Vector, ZERO_VEC, new_surface, fill, phase
from .colors import Color


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

        height : int 
        width : int
        
        shape : Vector
        pos : Vector 
        origin : Vector
        midpoint : Vector


    def __init__(
        self, 
        surface_or_shape : Surface | Coords, 

        origin : Vector = ZERO_VEC # the origin of the containing environment. by default, (0, 0)
    ):
        '''Parameters
        ----------
            surface_or_shape : Surface | Coords
                The Surface to wrap, or a set of coordinates denoting the size of the desired surface. If passed coordinates,
                creates a transparent Surface of the given width and height.
            origin : Vector
                The global Vector of the topleft point of the Structure that stores this Object. By default set to Vector(0, 0) (the topleft of the screen window).
        '''
        if isinstance(surface_or_shape, Surface):
            surface = surface_or_shape
        else:
            surface = new_surface(surface_or_shape)

        self._set(surface)

        object.__setattr__(self, 'origin', origin.copy())

        self.__container__ = None

        super().__init__()
    
    def _set(self, surface : Surface, fixed : Literal['topleft', 'topright', 'bottomleft', 'bottomright', 'center'] | None = None):
        self.surface = surface
        
        if fixed is not None:
            f = getattr(self.rect, fixed)
            self.rect = surface.get_rect()
            setattr(self.rect, fixed, f)
        else:
            self.rect = surface.get_rect()

        # INTRINSIC 

        object.__setattr__(self, 'shape', Vector(self.rect.size))
        self.midpoint = self.shape / 2

        # EXTRINSIC
        object.__setattr__(self, 'pos', Vector(self.rect.topleft))


    # we make it so that any reference to the edges of the surface points immediately through self.rect
    def __getattr__(self, name : str) -> Any:
        if name in RECT_ATTRS:
            return getattr(self.rect, name)
        else:
            raise AttributeError(name)
    
    def __setattr__(self, name: str, value: Any):
        if name == 'pos':
            self._set_pos(value)

        elif name == 'origin':
            raise PermissionError(f'Attribute origin is immutable from this scope.')
        
        elif name in ('shape', 'width', 'height'):
            raise PermissionError(f'Attribute {name} is immutable.')
        
        elif name in RECT_ATTRS:
            self._set_rect_attr(name, value)

        else:
            object.__setattr__(self, name, value)


    def _recurse_color_func(self, _color_func : Callable[['Object', Color], None], color : Color, recursion_depth : int = 0):
        _color_func(self, color)


    def _set_pos(self, value):
        object.__setattr__(self, 'pos', value)
        self.rect.topleft = value

    def _set_rect_attr(self, name, value):
        setattr(self.rect, name, value)
        object.__setattr__(self, 'pos', Vector(self.rect.topleft))

    # we set the origin.
    # this is called under-the-hood for environments
    def _set_origin(self, origin : Vector):
        object.__setattr__(self, 'origin', origin)
    
    def _shift_origin(self, displacement : Vector):
        object.__setattr__(self, 'origin', self.origin + displacement)

    
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

    def shift(self, displacement : Vector):
        '''Moves the topleft of this Object by the given displacement.
        
        Parameters
        ----------
            displacement : Vector
                The difference between the desired position and the current position.
        '''
        object.__setattr__(self, 'pos', self.pos + displacement)
        self.rect.topleft = self.pos


    # returns true if both (or the one given) sets of coordinates collide with this object
    
    def hits(self, vec : Vector, prev_vec : Vector | None = None, from_global : bool = True) -> bool:
        '''Whether or not the given Vector collides with this Object. If prev_vec is given, checks if both
        Vectors collide with this Object. If the immediate encompassing Structure is a View, ensures that the given Vector also hits the View.
        
        Parameters
        ----------
            vec : Vector 
                The Vector to check.
            
            prev_vec : Vector | None 
                If not None, essentially returns 

                >>> hits(vec) and hits(prev_vec)
            
            from_global : bool
                Whether the given Vectors are global (relative to the topleft of the screen).
        
        Returns
        -------
            True if the given Vectors collide with this Object, False otherwise.
        '''
        
            
        if prev_vec is None:
            if from_global:
                vec = vec - self.origin

            if isinstance(self.__container__, View):
                vec_relative_to_container = vec + self.__container__.pos
                if not self.__container__.rect.collidepoint(vec_relative_to_container):
                    return False

            return self.rect.collidepoint(vec)
       
        else:
            # we transmit to local coordinates by default
            if from_global:
                vec = vec - self.origin
                prev_vec = prev_vec - self.origin
            
            if isinstance(self.__container__, View):
                vec_relative_to_container = vec + self.__container__.pos
                prev_vec_relative_to_container = prev_vec + self.__container__.pos

                if not (
                    self.__container__.rect.collidepoint(vec_relative_to_container) 
                    and self.__container__.rect.collidepoint(prev_vec_relative_to_container)
                ):
                    return False

            return self.rect.collidepoint(vec) and self.rect.collidepoint(prev_vec)
    

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
class Structure(Object, Iterable[Object], ABC):
    '''An Object that holds other Objects and may simultanenously manipulate them.

    Each time that the position of this Structure is changed, the origins of its contained Objects are recursively updated.
    '''
    def __init__(
        self,
        surface_or_shape : Surface | Coords,
        origin : Vector = ZERO_VEC
    ):
        super().__init__(surface_or_shape, origin=origin)
    
    @abstractmethod
    def __iter__(self) -> Iterator[Object]:
        pass 


    def _set_pos(self, value):
        if value != self.pos:
            diff = value - self.pos 

            self.rect.topleft = value
            object.__setattr__(self, 'pos', value)
            
            for internal in self:
                internal._shift_origin(diff)

    def _set_rect_attr(self, name, value):
        rect = self.rect
        if value != getattr(rect, name):
            pos = self.pos

            rect.__setattr__(name, value)
            object.__setattr__(self, 'pos', Vector(self.rect.topleft))

            diff = self.pos - pos
            
            for internal in self:
                internal._shift_origin(diff)

                
    def _shift_origin(self, displacement : Vector):
        if displacement != ZERO_VEC:
            object.__setattr__(self, 'origin', self.origin + displacement)

            for internal in self:
                internal._shift_origin(displacement)

    def _set_origin(self, origin : Vector):  
        self._shift_origin(origin - self.origin)




    def _recurse_color_func(self, _color_func : Callable[['Object', Color], None], color : Color, recursion_depth : int = 0):
        _color_func(self, color)
        if recursion_depth != 0:
            for internal in self:
                internal._recurse_color_func(_color_func, color, recursion_depth-1)



    # sets the origin of a newly adding internal object
    def _wrap(self, val : Object):
        val._set_origin(self.origin + self.pos)
        val.__container__ = self

    # sets the origin of a list of newly adding internal objects
    def _wrap_arr(self, vals : Iterable[Object]):
        for val in vals:
            val._set_origin(self.origin + self.pos)
            val.__container__ = self

    

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

    
    def shift(self, displacement : Vector):
        '''Moves the topleft of this Object by the given displacement. Adjusts the origins of all contained Objects.
        
        Parameters
        ----------
            displacement : Vector
                The difference between the desired position and the current position.
        '''
        if displacement != ZERO_VEC:
            object.__setattr__(self, 'pos', self.pos + displacement)
            self.rect.topleft = self.pos

            for internal in self:
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

        for internal in self:
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
        origin : Vector = ZERO_VEC
    ):
        '''Parameters
        ----------
            surface_or_shape : Surface | Coords
                The Surface to wrap, or a set of coordinates denoting the size of the desired surface. If passed coordinates,
                creates a transparent Surface of the given width and height.
            item : Object
                The Object to hold a view on.
            origin : Vector
                The global Vector of the topleft point of the Structure that stores this Object. By default set to Vector(0, 0) (the topleft of the screen window).
        '''
        super().__init__(surface_or_shape, origin=origin)
        self.item = item
    
    def __iter__(self) -> Iterator[Object]:
        yield self.item


    def __setattr__(self, name: str, value: Any):
        # if the value is item, wraps first.    
        if name == 'item':
            self._wrap(value)
            object.__setattr__(self, name, value)
        else:
            Structure.__setattr__(self, name, value)

    
    def _clamp(self, displacement : Vector):
        max_disp = -self.item.pos
        min_disp = self.shape - (self.item.pos + self.item.shape)

        x = min(max_disp.x, max(min_disp.x, displacement.x))
        y = min(max_disp.y, max(min_disp.y, displacement.y))

        return Vector(x, y)
    
    def scroll(self, displacement : Vector):
        '''Moves the viewed item by the given displacement, but confines the view to be within bounds of the viewed item.
        
        Parameters
        ----------
            displacement : Vector
                The difference between the desired item position and the current item position.
        '''
        self.item.shift(self._clamp(displacement))
    

        



from collections import UserList, UserDict

# an array that contains other objects, adjusts origins, etc.
# stores contained objects in a list.
class Array(Structure, UserList[Object]):
    '''A Structure that holds a list of Objects.
    '''
    def __init__(
        self,
        surface_or_shape : Surface | Coords,
        origin : Vector = ZERO_VEC
    ):
        super().__init__(surface_or_shape, origin=origin)
        UserList.__init__(self)


    def __iter__(self) -> Iterator[Object]:
        yield from self.data

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
    def which_hits(self, vec : Vector, prev_vec : Vector | None = None, from_global : bool = True) -> int:
        '''The index of the Object in this list that is hit by the given Vectors. Returns -1 if none of the contained Objects are hit.
        
        Parameters
        ----------
            vec : Vector 
                The set of coordinates to check. If prev_vec is None, returns
                
                >>> i s.t. self[i].hits(vec) or -1
            
            prev_vec : Vector | None 
                If not None, returns 
                
                >>> i s.t. self[i].hits(vec, prev_vec) or -1
            
            from_global : bool
                Whether the given Vectors are global (relative to the topleft of the screen).
        
        Returns
        -------
        >>> i s.t. self[i].hits(vec, prev_vec, from_global).

        If the given coordinates don't hit any of the contained Objects, returns -1.
        '''
        # we transmit to local coordinates by default
        if from_global:
            vec = vec - self.origin
            if prev_vec is not None:
                prev_vec = prev_vec - self.origin
        
        # we transmit to internal local coordinates
        vec = vec - self.pos
        if prev_vec is not None:
            prev_vec = prev_vec - self.pos

        for index, internal in enumerate(self.data):
            if internal.hits(vec, prev_vec, from_global=False):
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
        origin : Vector = ZERO_VEC
    ):
        super().__init__(surface_or_shape, origin=origin)
        UserDict.__init__(self)

    def __iter__(self) -> Iterator[Object]:
        yield from self.values()

    # internal objects are blitted in the order of self._internals
    def __setitem__(self, key : str, val : Object):
        self._wrap(val)
        self.data[key] = val
     
    # returns the key of the hit object. None if none hits
    def which_hits(self, vec : Vector, prev_vec : Vector | None, from_global : bool = True) -> str | None:
        '''The name of the Object in this dictionary that is hit by the given Vectors. Returns None if none of the contained Objects are hit.
        
        Parameters
        ----------
            vec : Vector 
                The set of coordinates to check. If prev_vec is None, returns
                
                >>> name s.t. self[name].hits(vec) or None
            
            prev_vec : Vector | None 
                If not None, returns 
                
                >>> name s.t. self[name].hits(vec, prev_vec) or None
            
            from_global : bool
                Whether the given Vectors are global (relative to the topleft of the screen).
        
        Returns
        -------
        >>> name s.t. self[name].hits(vec, prev_vec, from_global).
            
        If the given coordinates don't hit any of the contained Objects, returns None.
        '''
        # we transmit to local coordinates by default
        if from_global:
            vec = vec - self.origin
            if prev_vec is not None:
                prev_vec = prev_vec - self.origin
        
        # we transmit to internal local coordinates
        vec = vec - self.pos
        if prev_vec is not None:
            prev_vec = prev_vec - self.pos

        for key, internal in self.data.items():
            if internal.hits(vec, prev_vec, from_global=False):
                return key 
        
        return None