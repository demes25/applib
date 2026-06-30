# Demetre Seturidze
# GameLib
# Text -- text windows and manipulation.

from .fonts import Font 
from .colors import Color
from .utils import new_surface, alpha_blend, Coords, Surface
from .objects import Object
       
# carries a buffer that dynamically writes onto a fixed-width object.
class TextEntry(Object):
    def __init__(
        self, 
        font : Font, 
        width : int, # a fixed width for the font environment

        color : Color | None = None,

        origin : Coords = (0, 0)
    ):
        self.augmented_glyph_width = font.glyph_height + font.gap_size
        self.augmented_glyph_height = font.glyph_width + font.gap_size

        self.glyphs_per_line = (width + font.gap_size) // self.augmented_glyph_width

        self.width = width
        self.height = font.glyph_height

        self.font = font 
        self.color = color 
        super().__init__(self.shape, origin=origin)

        self.string : str = ''
        self.lengths = []

        self.pointer = 0
            
        _pointer = new_surface((font.gap_size, font.glyph_height))
        _pointer.fill((0, 0, 0))

        self.pointer_surface = alpha_blend(_pointer, color=color, opacity=200)
        self.pointer_coords = (0, 0)
        self.pointer_shown = False

    @property
    def shape(self) -> Coords:
        return self.width, self.height

    def pointer_to_coord(self, pointer : int) -> Coords:
        y_coord = 0

        for l in self.lengths:
            if pointer > l:
                pointer -= l
                y_coord += self.font.glyph_height + self.font.gap_size
        
        x_coord = pointer * (self.font.glyph_height + self.font.gap_size) - self.font.gap_size

        return (x_coord, y_coord)

    def coord_to_pointer(self, coords : Coords):
        x_coord, y_coord = coords

        height = y_coord // (self.font.glyph_height + self.font.gap_size)

        pointer = x_coord // (self.font.glyph_width + self.font.gap_size)
        if height > 0:
            pointer += sum(self.lengths[:height])
    
    def blit_onto(self, dest : Surface | Object):
        surface = self.surface.copy()
        if self.pointer_shown:
            surface.blit(self.pointer_surface, self.pointer_coords)

        if isinstance(dest, Object):
            dest.surface.blit(surface, self.rect)
        else:
            dest.blit(surface, self.rect)

    

    def _update_lines_and_get(self) -> list[str]:
        lines = self.font.as_lines(self.string, self.glyphs_per_line)
        self.lengths = [len(line) for line in lines]
        self.height = max(len(self.lengths), 1) * self.augmented_glyph_height - self.font.gap_size
        return lines
    
    def _update_surface(self, lines : list[str]):
        Y = 0
        surface = new_surface(self.shape)

        for line in lines:
            surface.blit(
                self.font.render(line), (0, Y)
            )
            Y += self.augmented_glyph_height

        self.surface = alpha_blend(surface, color=self.color)

    def _update(self):
        lines = self._update_lines_and_get()
        self._update_surface(lines)
    


    def move_ptr_left(self):
        if self.pointer > 0:
            self.pointer -= 1
            self.pointer_coords = self.pointer_to_coord(self.pointer)
    
    def move_ptr_right(self):
        if self.pointer < len(self.string):
            self.pointer += 1
            self.pointer_coords = self.pointer_to_coord(self.pointer)
    


    def show_pointer(self):
        self.pointer_shown = True 
    
    def hide_pointer(self):
        self.pointer_shown = False



    def backspace(self):
        if self.pointer > 0:
            remainder = self.string[self.pointer:]
            self.pointer -= 1
            self.pointer_coords = self.pointer_to_coord(self.pointer)

            self.string = self.string[:self.pointer] + remainder

            self._update()

        
    
    def register(self, text : str):
        if text != '':
            self.string = self.string[:self.pointer] + text + self.string[self.pointer:]
            self.pointer += len(text)
            self.pointer_coords = self.pointer_to_coord(self.pointer)

            self._update()


    def clear(self) -> str:
        string = self.string

        self.string = '' 
        self.pointer = 0
        self.pointer_coords = (0, 0)

        self.lengths = []

        self.height = self.font.glyph_height

        self.surface = new_surface(self.shape)

        return string 
    

class TextRecord(Object):
    def __init__(
        self, 
        font : Font,
        width : int, # a fixed width for the environment
        text_gap_ratio : float = 5.0 # the ratio of the gap between texts to the gap between lines
    ):
        self.augmented_glyph_width = font.glyph_height + font.gap_size
        self.augmented_glyph_height = font.glyph_width + font.gap_size

        self.glyphs_per_line = (width + font.gap_size) // self.augmented_glyph_width
        
        self.width = width
        self.height = 0

        self.surface = new_surface((width, font.glyph_height))
        self.font = font 

        self.additional_gap = int(text_gap_ratio*font.gap_size)

    @property
    def shape(self) -> Coords:
        return (self.width, self.height)

    def register(self, string : str, color : Color | None = None):
        lines = self.font.as_lines(string, glyphs_per_line=self.glyphs_per_line)

        add_height = len(lines) * self.augmented_glyph_height + self.additional_gap

        current_height = self.height
        self.height += add_height

        updated_surface = new_surface(self.shape)

        if current_height != 0:
            updated_surface.blit(self.surface, (0, 0))
        
        for line in lines:
            line_surface = self.font.render(line, color=color)

            updated_surface.blit(line_surface, (0, current_height))
            current_height += self.augmented_glyph_height

        self.surface = updated_surface
            
        



