# Demetre Seturidze
# GameLib
# Colors

class Color:
    '''Holds a color as separate R, G, B, and alpha values. May be converted to a hexadecimal color string using str(...), to a tuple of four integers by accessing the "rgba" attribute, or a tuple of three integers by accessing the "rgb" attribute.'''

    __slots__ = ('_r', '_g', '_b', '_alpha', '_string', 'rgb', 'rgba')

    def __init__(self, RGBA : str):
        '''Parameters
----------
RGBA : str
    A string that represents the desired color in hexadecimal, of the form

    >>> '#RRGGBBaa',

    where aa is optional and represents the alpha value.
''' 
        self._string = RGBA 
        _regex_string = RGBA.removeprefix('#')

        match len(_regex_string):
            case 8:
                self._r = int(_regex_string[:2], 16)
                self._g = int(_regex_string[2:4], 16)
                self._b = int(_regex_string[4:6], 16)
                self._alpha = int(_regex_string[6:], 16)
            
            case 6:
                self._r = int(_regex_string[:2], 16)
                self._g = int(_regex_string[2:4], 16)
                self._b = int(_regex_string[4:6], 16)
                self._alpha = 255
            
            case _:
                raise ValueError('Color string must be of the form "#RRGGBBaa".')
        
        self.rgba = (
            self._r,
            self._g,
            self._b,
            self._alpha
        )

        self.rgb = (
            self._r,
            self._g,
            self._b
        )

    def __repr__(self):
        return self._string