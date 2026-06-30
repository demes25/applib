from .objects import Environment, Object, View
from .colors import Color
from .utils import Vector, hadamard

import pygame as pg



e = Environment((500, 500))
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
e.center = v.midpoint
v.center = se.midpoint - (15, 23)

se.fill(green)

pg.init()
pg.display.init()
screen = pg.display.set_mode((496, 496))

shifting = False
scrolling = False

prev_pos = v.origin

scroll_velocity = Vector(-3, 3)
c = pg.time.Clock()
c.tick(120)

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit()
        if event.type == pg.MOUSEWHEEL:
            if v.hits(Vector(pg.mouse.get_pos())):
                diff = Vector(event.x, event.y)
                v.scroll(hadamard(scroll_velocity, diff))
    
    screen.fill((0,0,0))

    se.blit_onto(screen)
    pg.display.flip()
    


