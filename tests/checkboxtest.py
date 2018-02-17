import pygame
import gui
screen = pygame.display.set_mode((600,600))
bg = pygame.Surface((600,600))
bg.fill((0,55,189))


gp = pygame.sprite.RenderUpdates()
clock = pygame.time.Clock()
test=gui.RadioButton(size=100)
test.rect.center = (100,100)
gp.add(test)
screen.blit(bg,(0,0))
pygame.display.flip()

while True:
    na=clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONUP:
            for each in gp:
                each.on_mouse_click(event)
        elif event.type == pygame.QUIT:
            raise SystemExit
    gp.clear(screen,bg)
    gp.update()
    ds=gp.draw(screen)
    pygame.display.update(ds)


