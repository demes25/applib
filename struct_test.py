from gamelib.objects import Environment, Object
from gamelib.colors import Color
from gamelib.utils import add, sub

import pygame as pg


e = Environment((248, 248))
obj = Object((64, 64))
obj.topleft = (142, 12)

e.update({'obj' : obj})


red = Color.from_hex('#FF1100')
blue = Color.from_hex('#1100FF')
green = Color.from_hex("#00d80e")

print(red.hex)


obj.surface.fill(red.rgb)
e.surface.fill(blue.rgb)

se = Environment((496, 496))
se['e'] = e 
e.center = sub(se.center, (15, 23))

se.fill(green)

pg.init()
pg.display.init()
screen = pg.display.set_mode((496, 496))

moving = False
prev_pos = (0, 0)

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit()
        if event.type == pg.MOUSEBUTTONDOWN:
            if e.hits(event.pos) and not obj.hits(event.pos):
                print('CLICK')
                se.tint(Color.from_hex("#6aff00").new_opacity(23), recursion_depth=-1)
                moving = True
                prev_pos = event.pos 
        
        if event.type == pg.MOUSEBUTTONUP:
            moving = False
    
    screen.fill((0,0,0))

    if moving:
        curr_pos = pg.mouse.get_pos()
        e.shift(sub(curr_pos, prev_pos))
        prev_pos = curr_pos

    se.blit_onto(screen)
    pg.display.flip()
    


