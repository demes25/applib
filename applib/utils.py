# Demetre Seturidze
# GameLib
# Tools -- for loading and manipulating assets

from typing import Callable, Any
from pathlib import Path 

import pygame as pg

from .colors import Color

# TODO: add pg.Vector2 functionality - better than numpy.

Coords = tuple[int, int]
Vector = pg.Vector2
ZERO_VEC = Vector(0, 0)

Surface = pg.surface.Surface
Sound = pg.mixer.Sound 

# iterates through files of the given extension, yields the file stem name and the path object.
# applies func before yielding if specified
def file_iter(dir : Path, ext : str, func : Callable[[Path], Any] | None = None):
    '''Iterates through the files with the given extension in the given directory.
    If func is None, yields tuples of the following structure:
    >>> (file_stem_name, file_path).

    If func is not None, yields tuples of the following structure
    >>> (file_stem_name, func(file_path)).
    
    Parameters
    ----------
        dir : Path
            The directory to search.
        ext : str 
            The desired file extension
        func : [(Path) -> Any] | None
            The function to apply to the path objects before yielding, if any.
    '''
    if func is None:
        for path in Path(dir).glob(f'*.{ext}'):
            yield (path.stem, path)
    else:
        for path in Path(dir).glob(f'*.{ext}'):
            yield (path.stem, func(path))

# iterates through all files with a given extension in the given directory and returns a dictionary of them,
# keyed by the 'stems' (i.e. extensionless names) of the files in question
def dict_from_dir(dir : Path, ext : str, func : Callable[[Path], Any] | None = None):
    '''Iterates through all files with the given extension in the given directory.
    If func is None, returns a dictionary of the following structure
    >>> {
            file_stem_name : file_path,
            ...
        }

    If func is specified, returns a dictionary of the following structure
    >>> {
            file_stem_name : func(file_path),
            ...
        }
    
    Parameters
    ----------
        dir : Path
            The directory to search.
        ext : str 
            The desired file extension
        func : [(Path) -> Any] | None
            The function to apply to the path objects, if any.
    '''
    return dict(file_iter(dir=dir, ext=ext, func=func))

# creates a blank transparent surface of the given dimensions
def new_surface(shape : Coords):
    '''Creates a transparent Surface of the given shape.
    
    Parameters
    ----------
        shape : Coords
            The shape of the Surface.
    
    Returns
    -------
        A transparent Surface of the given shape.
    '''
    return Surface(shape, pg.SRCALPHA)

# returns a function that loads images and scales them to the given dimension
def scaled_loader(scaling : Coords | tuple[float, float] | int | float | None = None):
    '''A generator that returns a function that loads images from file paths and scales them to the given shape (if any).
    
    Parameters
    ----------
        scaling : Coords | None
            If not None, the resulting function scales the dimensions of loaded images by the given ratios before returning.
    
    Returns
    -------
        A function that loads images from file paths and scales them by the given scale (if any).
    '''

    if scaling is None:
        return pg.image.load
    
    elif isinstance(scaling, tuple):
        def _load(path : Path):
            image = pg.image.load(path)
            shape = mul(scaling, image.get_rect().size)
            return pg.transform.scale(pg.image.load(path), shape)
    
    else:
        def _load(path : Path):
            image = pg.image.load(path)
            shape = scale(scaling, image.get_rect().size)
            return pg.transform.scale(pg.image.load(path), shape)
        
    return _load 

# tints an image in-place (and returns)
def phase(surface : Surface, color : Color, copy : bool = True) -> Surface:
    '''Multiplies the RGBA values of the given surface by those of the given Color. 
    
    Parameters
    ----------
        surface : Surface
            The surface to manipulate.
        color : Color
            The color to multiply by.
        copy : bool
            If False, manipulates in-place. Otherwise, manipulates a copy.
    
    Returns
    -------
        The resulting surface.
    '''
    if copy:
        surface = surface.copy()
    
    surface.fill(color.rgba, special_flags=pg.BLEND_RGBA_MULT)
    return surface

def fill(surface : Surface, color : Color, copy : bool = True) -> Surface:
    '''Fills the given surface with the given color.
    
    Parameters
    ----------
        surface : Surface
            The surface to fill.
        color : Color
            The color to fill with.
        copy : bool
            If False, manipulates in-place. Otherwise, manipulates a copy.
    
    Returns
    -------
        The resulting surface.
    '''
    if copy:
        surface = surface.copy()

    surface.fill(color.rgba)
    return surface

# Creates a copy where all visible pixels take on target_color.
# The original alpha channel is multiplied by alpha_scale.
def alpha_blend(surface : Surface, color : Color, copy : bool = True) -> Surface:
    '''Isolates the alpha layer of the given surface and fills with the given color.
    
    Parameters
    ----------
        surface : Surface
            The surface to manipulate.
        color : Color
            The color to fill with.
        copy : bool
            If False, manipulates in-place. Otherwise, manipulates a copy.
    
    Returns
    -------
        The resulting surface.
    '''
    if copy:
        surface = surface.copy()

    # 1. Zero out the RGB channels, leaving the original alpha intact
    surface.fill((0, 0, 0, 255), special_flags=pg.BLEND_RGBA_MULT)

    # 2. Add your fixed color into the RGB channels (ignoring alpha for now)
    surface.fill(color.rgb + (0, ), special_flags=pg.BLEND_RGBA_ADD)
    
    # 4. Scale the alpha channel
    alpha_mask = pg.Surface(surface.get_size(), pg.SRCALPHA)
    alpha_mask.fill((255, 255, 255, color.alpha))
    surface.blit(alpha_mask, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        
    return surface

def reshape(surface : Surface, shape : Coords) -> Surface:
    '''Reshapes a copy of the given Surface to the given shape, returns.
    
    Parameters
    ----------
        surface : Surface
            The surface to reshape.
        shape : Coords
            The desired end shape.
    
    Returns
    -------
        The reshaped surface.
    '''

    return pg.transform.scale(surface=surface, size=shape)


def hadamard(v1 : Vector, v2 : Vector) -> Vector:
    '''Multiplies two Vectors termwise.
    
    Parameters
    ----------
        v1 : Vector
            The multiplier.
        v2 : Vector
            The multiplicand.
    
    Returns
    -------
    >>> Vector(v1.x * v2.x, v1.y * v2.y)
    '''
    return Vector(v1.x * v2.x, v1.y * v2.y)

# TUPLE MANIPULATORS

def add(c1 : Coords, c2 : Coords) -> Coords:
    '''Adds two sets of coordinates termwise.
    
    Parameters
    ----------
        c1 : Coords 
            The augend.
        c2 : Coords
            The addend.
    
    Returns
    -------
    >>> (
            c1[0] + c2[0], 
            c1[1] + c2[1]
        )
    '''
    return (c1[0] + c2[0], c1[1] + c2[1])

def sub(c1 : Coords, c2 : Coords) -> Coords:
    '''Subtracts two sets of coordinates termwise.
    
    Parameters
    ----------
        c1 : Coords 
            The minuend.
        c2 : Coords
            The subtrahend.
    
    Returns
    -------
    >>> (
            c1[0] - c2[0], 
            c1[1] - c2[1]
        )
    '''
    return (c1[0] - c2[0], c1[1] - c2[1])

def mul(a : Coords | tuple[float, float], c : Coords) -> Coords:
    '''Multiplies two sets of coordinates, or a pair of floats and a set of coordinates, termwise.
    
    Parameters
    ----------
        a : Coords | tuple[float, float] 
            The multiplier.
        c : Coords
            The multiplicand.
    
    Returns
    -------
    >>> (
            int(a[0] * c[0]), 
            int(a[1] * c[1])
        )
    '''
    return (int(a[0] * c[0]), int(a[1] * c[1]))

def scale(a : int | float, c : Coords) -> Coords:
    '''Scales a set of coordinates by the given scalar.
    
    Parameters
    ----------
        a : int | float 
            The scalar.
        c : Coords
            The coordinates to scale.
    
    Returns
    -------
    >>> (
            int(a * c[0]), 
            int(a * c[1])
        )
    '''
    return (int(a*c[0]), int(a*c[1]))


def mul_or_scale(a : int | float | Coords | tuple[float, float], c : Coords) -> Coords:
    '''Scales a set of coordinates by the given scalar, or termwise given a set of coordinates or a pair of floats.
    
    Parameters
    ----------
        a : int | float | tuple[float, float] | Coords
            The scalar.
        c : Coords
            The coordinates to scale.
    
    Returns
    -------
    >>> mul(a, c) if isinstance(a, tuple) else scale(a, c)
    '''
    return mul(a, c) if isinstance(a, tuple) else scale(a, c)
    
def neg(c : Coords) -> Coords:
    '''Flips the sign of a set of coordinates.
    
    Parameters
    ----------
        c : Coords
            The set of coordinates.
    
    Returns
    -------
    >>> (
            -c[0],
            -c[1]
        )
    '''
    return (-c[0], -c[1])

def mins(c1 : Coords, c2 : Coords) -> Coords:
    '''Reduces to the minimum value termwise.
    
    Parameters
    ----------
        c1 : Coords
            The first set of coordinates.
        c2 : Coords 
            The second set of coordinates.
    
    Returns
    -------
    >>> (
            min(c1[0], c2[0]),
            min(c1[1], c2[1])
        )
    '''
    return (
        min(c1[0], c2[0]),
        min(c1[1], c2[1])
    )

def maxs(c1 : Coords, c2 : Coords) -> Coords:
    '''Reduces to the maximum value termwise.
    
    Parameters
    ----------
        c1 : Coords
            The first set of coordinates.
        c2 : Coords 
            The second set of coordinates.
    
    Returns
    -------
    >>> (
            max(c1[0], c2[0]),
            max(c1[1], c2[1])
        )
    '''
    return (
        max(c1[0], c2[0]),
        max(c1[1], c2[1])
    )
