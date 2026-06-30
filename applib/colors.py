# Demetre Seturidze
# AppLib
# Colors

from dataclasses import dataclass
from functools import cached_property

@dataclass(frozen=True)
class Color:
    '''Holds a color as separate R, G, B, and alpha values. May be converted to a hexadecimal color string using the .hex property, 
    to a tuple of four integers using the .rgba property, or a tuple of three integers using the .rgb property.'''

    r : int 
    g : int 
    b : int 
    alpha : int = 255

    @classmethod
    def from_hex(cls, hex : str) -> 'Color':
        '''Parameters
----------
hex : str
    A string that represents the desired color in hexadecimal, of the form

    >>> '#RRGGBBaa',

    where aa is optional and represents the alpha value.
''' 
        s = hex.lstrip("#")

        if len(s) == 6:
            return Color(
                r=int(s[0:2], 16), 
                g=int(s[2:4], 16), 
                b=int(s[4:6], 16)
            )
        
        elif len(s) == 8:
            return Color(
                r=int(s[0:2], 16),
                g=int(s[2:4], 16),
                b=int(s[4:6], 16),
                alpha=int(s[6:8], 16),
            )
        else:
            raise ValueError("Invalid hex color")

    @cached_property
    def rgb(self) -> tuple[int, int, int]:
        return (self.r, self.g, self.b)
    
    @cached_property
    def rgba(self) -> tuple[int, int, int]:
        return (self.r, self.g, self.b, self.alpha)
    
    @cached_property
    def hex(self) -> str:
        '''A string containing this color in hexadecimal, of the form
        >>> '#RRGGBBaa'
        '''
        fullnum = self.b + 256 * self.g + 65536 * self.r

        if self.alpha != 255:
            fullnum = self.alpha + 256*fullnum

        hexstr = hex(fullnum)
        hexstr = '#' + hexstr.removeprefix('0x')

        return hexstr

    def new_opacity(self, alpha : int = 255) -> 'Color':
        '''Returns a new color with the same RGB values but with the specified alpha value.
        
        Parameters
        ---------
            alpha : int 
                The desired alpha value, between 0 and 255.
        
        Returns
        ------
            >>> Color(self.r, self.g, self.b, alpha)
        '''
        return Color(self.r, self.g, self.b, alpha)


        