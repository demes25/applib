from gamelib.objects import Environment, Object, View
from gamelib.colors import Color
from gamelib.utils import add, sub

import pygame as pg



e = Environment((128, 128))
v = View((248, 248), e)

sube = Object((248, 248))
sube.center = e.midpoint

obj = Object((64, 64))
obj.center = e.midpoint
obj.bottom += v.height //2

e.update({'sube' : sube, 'obj' : obj})

red = Color.from_hex('#FF1100')
blue = Color.from_hex('#1100FF')
green = Color.from_hex("#00d80e")
black = Color.from_hex('#000000')



obj.fill(red)
sube.fill(blue)
e.fill(black)

se = Environment((496, 496))
se['v'] = v 
v.center = sub(se.midpoint, (15, 23))

se.fill(green)

pg.init()
pg.display.init()
screen = pg.display.set_mode((496, 496))

shifting = False
scrolling = False

prev_pos = (0, 0)

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit()
        if event.type == pg.MOUSEBUTTONDOWN:
            if obj.hits(event.pos):
                print('CLICK')
                shifting = False 
                scrolling = True 
                prev_pos = event.pos
            if e.hits(event.pos) and not obj.hits(event.pos):
                print('CLICK')
                shifting = True
                scrolling = False
                prev_pos = event.pos 
        
        if event.type == pg.MOUSEBUTTONUP:
            shifting = False
            scrolling = False
    
    screen.fill((0,0,0))

    if shifting:
        curr_pos = pg.mouse.get_pos()
        v.shift(sub(curr_pos, prev_pos))
        prev_pos = curr_pos
    elif scrolling:
        curr_pos = pg.mouse.get_pos()
        v.scroll(sub(curr_pos, prev_pos))
        prev_pos = curr_pos

    se.blit_onto(screen)
    pg.display.flip()
    


