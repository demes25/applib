# Demetre Seturidze
# AppLib
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
def loader(scaling : Coords | tuple[float, float] | int | float | None = None) -> Callable[[Path], Surface]:
    '''A generator that returns a function that loads images from file paths and scales them by the given scaling (if any).
    
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
            surface = pg.image.load(path)
            shape = surface.get_size()

            shape = (shape[0]*scaling[0], shape[1]*scaling[1])

            return pg.transform.scale(surface, shape)
    
    else:
        def _load(path : Path):
            surface = pg.image.load(path)
            shape = surface.get_size()

            shape = (shape[0] * scaling, shape[1] * scaling)

            return pg.transform.scale(surface, shape)
        
    return _load 

def saver(scaling : Coords | tuple[float, float] | int | float | None = None) -> Callable[[Surface, Path], None]:
    '''A generator that returns a function that scales images to the given shape (if any) and saves them.
    
    Parameters
    ----------
        scaling : Coords | None
            If not None, the resulting function scales the dimensions of loaded images by the given ratios before saving.
    
    Returns
    -------
        A function that scales images to the given shape (if any) and saves them.
    '''

    if scaling is None:
        return pg.image.save
    
    elif isinstance(scaling, tuple):
        def _save(surface : Surface, path : Path):
            shape = surface.get_size()
            shape = (shape[0]*scaling[0], shape[1]*scaling[1])
            surface = pg.transform.scale(surface, shape)
            pg.image.save(surface, path)
    
    else:
        def _save(surface : Surface, path : Path):
            shape = surface.get_size()
            shape = (shape[0]*scaling, shape[1]*scaling)
            surface = pg.transform.scale(surface, shape)
            pg.image.save(surface, path)
        
    return _save 

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

def scale(surface : Surface, scaling : Coords | tuple[float, float] | int | float) -> Surface:
    '''Scales a copy of the given Surface by the given ratios.
    
    Parameters
    ----------
        scaling : Coords | tuple[float, float] | int | float
            The scaling ratios. If an integer or float, scales both dimensions by the same number. Otherwise, scales each dimension by the corresponding ratio.
    
    Returns
    -------
        The scaled surface.
    '''

    shape = surface.get_size()
    
    if isinstance(scaling, tuple):
        shape = (shape[0]*scaling[0], shape[1]*scaling[1])
    else:
        shape = (int(shape[0]*scaling), int(shape[1]*scaling))

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