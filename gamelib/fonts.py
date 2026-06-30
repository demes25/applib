# Demetre Seturidze
# GameLib
# Fonts

from typing import Dict, List 
from pathlib import Path 
import pygame as pg 
from .utils import Color, Coords, Surface, new_surface, alpha_blend, reshape
from collections import UserDict


# we load an ALPHABET, as well as some additional metadata.
# the alphabet MUST be monospaced and have a set size ratio. 
class Alphabet(UserDict):
    '''An Alphabet -- a dictionary of glyphs structured like
    >>> {
            char : glyph
        }
    
    where chars are single-character strings, and the glyphs are Surfaces. 
    
    This requires a specific ordering/protocol. Namely, the glyphs must all be of equal shape, say (n, m), and are imported from an image file
    of size (95*n, m), where each consecutive region of width n contains a glyph for a character and parallels the ASCII encoding protocol. 

    The image file must be a contiguous image of the following 95 characters in the following order, all located directly side-by-side with no spaces in between:

    >>> [space] ! " # $ % & ' ( ) * + , - . / 0 1 2 3 4 5 6 7 8 9 : ; < = > ? @ A B C D E F G H I J K L M N O P Q R S T U V W X Y Z [ \ ] ^ _ ` a b c d e f g h i j k l m n o p q r s t u v w x y z { | } ~ 
    '''
    ASCII = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
    ASCII_COUNT = len(ASCII)

    # saves a template for the given font size, includes divisors if so wanted
    # the general font template 
    @staticmethod
    def template(glyph_shape : Coords, include_placeholders : bool = True, path : str | Path | None = None) -> Surface:
        '''Creates a template for an alphabet with the given letter shape. Includes placeholder characters if desired. If given a path object, saves
        this template to the given path.
        
        Parameters
        ----------
            glyph_shape : Coords 
                The shape of each letter
            include_placeholders : bool
                If True, we include placeholders where each glyph should go
            path : str | Path | None
                If not None, saves this template to the given file path.

        Returns
        -------
        A transparent Surface of shape
        >>> (95*glyph_width, glyph_height),

        where
        >>> glyph_width, glyph_height == glyph_shape 
        '''
        
        width, height = glyph_shape 
        total_width = width * Alphabet.ASCII_COUNT

        template = new_surface((total_width, height))

        if include_placeholders:
            # creates a default placeholder
            placeholder = new_surface(glyph_shape)

            single_pixel = new_surface((1, 1))
            single_pixel.fill((127, 127, 127))

            Y_VAL = height-1

            for X_VAL in range(width-1):
                placeholder.blit(single_pixel, (X_VAL, Y_VAL))
                
            placeholder.blit(single_pixel, (0, Y_VAL-1))

            for X_VAL in range(0, total_width, width):
                template.blit(placeholder, (X_VAL, 0))
        
        if path is not None:
            pg.image.save(template, path)

        return template 


    def __init__(
        self, 
        path : str | Path, # the file name of the font file. should be an image with dimensions (font_width * 95, font_height)
                           # which is a contiguous image of all writable symbols in ASCII.
    ):  
        '''Parameters
        ----------
            path : str | Path
                The file path of the image to load from.
        '''
        # we load the font image
        font_image = pg.image.load(path)
        font_rect = font_image.get_rect()

        # find the dimensions of each letter

        glyph_height = self.glyph_height = font_rect.height 

        # if the font_width is not a multiple of 95, this does not fit our requirements
        if font_rect.width % Alphabet.ASCII_COUNT != 0:
            raise ValueError('Alphabet image width must be a multiple of 95.')
        
        glyph_width = self.glyph_width = font_rect.width//Alphabet.ASCII_COUNT


        # store the specs per-letter
        self.glyph_shape = (glyph_width, glyph_height) # the dimensions of the font, in pixels.

        # the rect which we will use to parse the letters of the alphabet
        glyph_rect = pg.rect.Rect(0, 0, glyph_width, glyph_height)

        super().__init__()

        # we store the alphabet
        for char in Alphabet.ASCII:
            self.data[char] = font_image.subsurface(glyph_rect)    
            glyph_rect.left += glyph_width

    
    def __setitem__(self, _, __):
        raise PermissionError('Alphabet objects are immutable.')
    

    def get_scaled(
        self,
        shape : Coords | None, # pixel-dimensions height of each letter
    ) -> Dict[str, Surface]:
        '''Returns a scaled copy of this dictionary.
        
        Parameters
        ----------
            shape : Coords | None
                If None, returns a copy of this dictionary. Otherwise, returns a scaled copy where each glyph is reshaped to this shape.

        Returns
        -------
            >>> self.copy() if shape is None else {
                char : reshape(glyph, shape) for char, glyph in self.items()
            } 
        '''
        
        if shape is None:
            return self.data.copy()
        else:    
            return {
                char : reshape(glyph, shape=shape) for char, glyph in self.items()
            }
        
    

# carries an instance of alphabet which is sized in some way.
class Font(UserDict):
    '''A dictionary wrapper that stores a scaled Alphabet. Equipped with text-to-Surface rendering funcionality.
    '''

    def __init__(
        self,
        alphabet_or_path : str | Path | Alphabet, # the alphabet object or the path to its generating image
        fontsize : int, # pixel height of each letter
    ):
        '''Parameters
        ----------
            alphabet_or_path : str | Path | Alphabet
                The alphabet object for this font, or a path to the file containing the alphabet image.
            fontsize : int
                The target height of each glyph. Scales the width to maintain relative proportions.
        '''
        
        super().__init__()

        if isinstance(alphabet_or_path, Alphabet): 
            self.alphabet = alphabet_or_path
        else:
            self.alphabet = Alphabet(alphabet_or_path)

        self.set(
            fontsize=fontsize
        )
    
    def __setitem__(self, _, __):
        raise PermissionError('Font entries are immutable.')
    
    def set(
        self,
        fontsize : int
    ):  
        '''Sets this font to the given fontsize. Updates the internal dictionary and dimension info.
        
        Parameters
        ----------
            fontsize : int 
                The target height of each glyph. Scales the width to maintain relative proportions.
        '''
        self.glyph_height = fontsize
        self.glyph_width = (self.alphabet.glyph_width * fontsize) // self.alphabet.glyph_height
        
        self.glyph_shape = (self.glyph_width, self.glyph_height)

        self.gap_size = fontsize // self.alphabet.glyph_height # we leave gaps, equivalent to one alphabet-pixel in between.

        self.data = self.alphabet.get_scaled(shape=self.glyph_shape)

    
    def render(
        self,
        text : str,
        color : Color | None = None,
        background_color : Color | None = None
    ) -> Surface:
        '''Renders the given text into a Surface. If a color is specified, alpha-blends the text with the given color (see utils.alpha_blend). If a background is specified,
        fills the background with the given color.
        
        Parameters
        ----------
            text : str
                The text to render.
            color : Color | None 
                If None, retains the original color of the Alphabet glyphs. Otherwise alpha-blends each glyph with the given color.
            background_color : Color | None
                If None, retains transparent background. Otherwise fills the background with the given color.
        
        Returns
        -------
            The rendered text Surface.
        '''
        
        glyph_and_gap = self.glyph_width + self.gap_size
        width = glyph_and_gap * len(text) - self.gap_size
        surface = new_surface((width, self.glyph_height))

        X = 0

        for char in text:
            surface.blit(self[char], (X, 0))
            X += self.glyph_width + self.gap_size
        
        if color is not None:
            surface = alpha_blend(surface=surface, color=color)

        if background_color is not None:
            background = new_surface((width, self.glyph_height))
            background.fill(background_color)
            background.blit(surface, (0, 0))
            return background
        
        else:
            return surface
    
    
    def as_lines(self, text : str, glyphs_per_line : int) -> List[str]:
        '''Splits the given text into lines according to the specified number of glyphs per line. Avoids mid-word line breaks when possible.
        
        Parameters
        ----------  
            text : str 
                The text to split.
            
            glyphs_per_line : int
                The maximum number of glyphs per line.
                
        Returns
        -------
            The list of lines, as strings.
        '''
        lines = []

        while text != '':
            if len(text) > glyphs_per_line:
                candidate = text[:glyphs_per_line]
                text = text[glyphs_per_line:]
            else:
                candidate = text
                text = ''

            if '\n' in candidate:
                candidate, remainder = candidate.split('\n', maxsplit=1)

                text = remainder + text 
            elif len(text) > 0:
                if text[0] == ' ':
                    text = text[1:]
                elif len(candidate) > 0:
                    for i in range(len(candidate)-1, 0, -1):
                        if candidate[i] == ' ':
                            text = candidate[i+1:] + text
                            candidate = candidate[:i]
                            break
            
            if len(text) > 0 or len(candidate) > 0:
                lines.append(candidate)
        
        return lines
