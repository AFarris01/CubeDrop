import pygame
import gui
import logging

logger=logging.getLogger(__name__)
logging.basicConfig()

screen=pygame.display.set_mode((600,600))
bg=pygame.Surface((600,600)).convert()
bg.fill((255,255,255))
screen.blit(bg,(0,0))
pdu=pygame.display.update
pdu()
gp=pygame.sprite.RenderUpdates()
gp.add( gui.SpinButton() )
for each in gp:
    each.rect.center=screen.get_rect().center

clock=pygame.time.Clock()

while True:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise SystemExit
        elif event.type == pygame.MOUSEBUTTONUP:
            print event
            for each in gp:
                each.on_mouse_click(event)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                raise SystemExit
        
    
    gp.clear(screen,bg)  
    gp.update()      
    ds=gp.draw(screen)
    pdu(ds)

