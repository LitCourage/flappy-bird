import pygame as pg
from random import randint

screen = pg.display.set_mode((600, 600))

clock = pg.time.Clock()

class Rect(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = pg.rect.Rect((randint(200, 400), 0), (25, 25))
    def update(self):
        self.rect.y += 2
    def draw(self, screen):
        pg.draw.rect(screen, 'red', self.rect)

rects = pg.sprite.Group()

timer = pg.time.get_ticks()

while True:
    screen.fill('black')

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            quit()
    
    for rect in rects:
        rect.update()
        rect.draw(screen)
        if rect.rect.y > 600:
            rects.remove(rect)

    if pg.time.get_ticks() - timer > 1000:
        rects.add(Rect())
        timer = pg.time.get_ticks()

    pg.display.flip()
    clock.tick(60)