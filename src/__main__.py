"""
The MIT License (MIT)

Copyright (c) 2023

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import sys
import os
import pygame
from pygame import K_ESCAPE, KEYDOWN, K_q
from typing import Literal

pygame.init()


class Button(pygame.sprite.Sprite):
    FONT = pygame.font.SysFont(
            name=pygame.font.get_default_font(),
            size=55)

    def __init__(
            self,
            text: str,
            y: int,
            group: pygame.sprite.Group,
            x=None):
        """ Creates a clickable button """
        super().__init__(group)
        self.image: pygame.surface.Surface = Button.FONT.render(
                text=text,
                antialias=True,
                color=(255, 255, 255, 255))
        x = pygame.display.get_surface().get_rect().width // 2 - \
            self.image.get_rect().width // 2  # Center text on X axis
        self.rect: pygame.rect.Rect = pygame.Rect(
                left=x,
                top=y,
                width=self.image.get_width(),
                height=self.image.get_height())
        self.border: pygame.surface.Surface = pygame.Surface(
                size=(self.rect.width, self.rect.height))
        self.border.set_colorkey(color=(0, 0, 0, 255))
        pygame.draw.rect(
                surface=self.border,
                color=(255, 255, 255, 255),
                rect=pygame.Rect(
                    left=0,
                    top=self.rect.height - 5,
                    width=self.image.get_width(),
                    height=5))
        self.hover: bool = False
        self._alpha = 0
        self.text: str = text

    def draw(self, surface: pygame.surface.Surface) -> None:
        """ Blit image to display """
        surface.blit(source=self.image, dest=self.rect)
        if self.hover:
            if self._alpha < 255:
                self._alpha += 20
        else:
            if self._alpha > 0:
                self._alpha -= 20
        self.border.set_alpha(value=self._alpha)
        surface.blit(source=self.border, dest=(self.rect.x, self.rect.y))


class Defenders:
    """ Panel that holds defender ui """
    def __init__(self):
        self.width = 100
        self.height = 550
        self.image = pygame.Surface(size=(self.width, self.height))
        self.rect = pygame.Rect(
                top=650,
                left=100,
                width=100,
                height=550)
        pygame.draw.rect(
                surface=self.image,
                color=(255, 255, 255, 255),
                rect=self.rect,
                width=0,
                border_radius=5)

    def draw(self, surface: pygame.surface.Surface) -> None:
        """ Draw image and rect to surface """
        surface.blit(
                source=self.image,
                dest=(self.rect.x, self.rect.y))


size: int | tuple[Literal[800], Literal[600]] = 800, 600
clock = pygame.time.Clock()
screen = pygame.display.set_mode(
        size=size,
        depth=0,
        flags=(
            pygame.DOUBLEBUF |
            pygame.HWACCEL |
            pygame.DOUBLEBUF),
        vsync=True)

pygame.display.set_caption(os.getcwd())

done: Literal[True] |\
      Literal[False] |\
      Literal[None] = False

play: Literal[True] |\
      Literal[False] |\
      Literal[None] = False

buttons: pygame.sprite.Group | None = pygame.sprite.Group()
Button(
        text="Play",
        y=100,
        group=buttons,
        x=None)
Button(
        text="Exit",
        y=200,
        group=buttons,
        x=None)

mouse: list[int | Literal[0]] = [0, 0]

while not done:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE or K_q:
                done = True
        if event.type == pygame.MOUSEMOTION:
            mouse: list[int] = list(pygame.mouse.get_pos())
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in buttons:
                if pygame.Rect.collidepoint(
                        self=button.rect,
                        x_y=(mouse[0], mouse[1])):
                    if button.text.lower() == 'exit':
                        done = True
                    else:
                        play = True
                        done = True

    for button in buttons:
        if pygame.Rect.collidepoint(
                self=button.rect,
                x_y=(mouse[0], mouse[1])):
            button.hover = True
        else:
            button.hover = False

    screen.fill(color=(0, 0, 0, 255))

    for button in buttons:
        button.draw(surface=screen)

    pygame.display.update()
    clock.tick(framerate=60)

if not play:
    pygame.quit()
    sys.exit()

done: Literal[False] | Literal[True] | Literal[None] = False

ui: pygame.sprite.Group | None = pygame.sprite.Group()
defender_panel: object | None | pygame.sprite.Group = Defenders()

while not done:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE or K_q:
                done = True
        if event.type == pygame.MOUSEMOTION:
            mouse = list(pygame.mouse.get_pos())

    for button in buttons:
        if pygame.Rect.collidepoint(
                self=button.rect,
                x_y=(mouse[0], mouse[1])):
            button.hover = True
        else:
            button.hover = False

    screen.fill(
            color=(0, 0, 0, 255))

    for button in ui:
        button.draw(
                surface=screen)

    defender_panel.draw(
            surface=screen)

    pygame.display.update()
    clock.tick(framerate=60)
