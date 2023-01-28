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
import json
import pygame
import mysql.connector as database
from pygame import K_ESCAPE, KEYDOWN, K_q

pygame.init()


class User:
    def __init__(self):
        self.name = os.environ.get("username")
        self.psw = os.environ.get("password")


user = User()

connection = database.connect(
        user=user.name,
        password=user.psw,
        host='localhost',
        database="workplace")


class Database(connection.cursor):
    """ Database records test runs and errors """
    def __init__(self):
        super().__init__()
        self.tables = ["empolyees"]
        self.current_table = 0

    def add_entry(self, fname, lname) -> None:
        """ Accepts first and last names of empolyees """
        try:
            statement = "INSERT INTO {} ({}) VALUES (%s, %s)".format(
                    self.tables[self.current_table], "first_name, last_name")
            self.execute(statement, (fname, lname))
        except database.Error as error:
            print(f"Error adding entry to database: {error}")


class Button(pygame.sprite.Sprite):
    """ A clickable, animated button for UI and menus. """
    FONT = pygame.font.SysFont(
            name=pygame.font.get_default_font(),
            size=55)

    def __init__(
            self,
            text: str,
            position_y: int,
            group: pygame.sprite.Group,
            position_x=None):
        super().__init__(group)
        self.image: pygame.surface.Surface = Button.FONT.render(
                text,
                True,
                (255, 255, 255, 255))
        position_x = pygame.display.get_surface().get_rect().width // 2 - \
            self.image.get_rect().width // 2  # Center text on X axis
        self.rect: pygame.rect.Rect = pygame.Rect(
                position_x,
                position_y,
                self.image.get_width(),
                self.image.get_height())
        self.border: pygame.surface.Surface = pygame.Surface(
                (self.rect.width, self.rect.height))
        self.border.set_colorkey((0, 0, 0, 255))
        pygame.draw.rect(
                self.border,
                (255, 255, 255, 255),
                pygame.Rect(
                    0,
                    self.rect.height - 5,
                    self.image.get_width(),
                    5))
        self.hover: bool = False
        self._alpha = 0
        self.text: str = text

    def draw(self, surface: pygame.surface.Surface) -> None:
        """ Blit image to display """
        surface.blit(self.image, self.rect)
        if self.hover:
            if self._alpha < 255:
                self._alpha += 20
        else:
            if self._alpha > 0:
                self._alpha -= 20
        self.border.set_alpha(self._alpha)
        surface.blit(self.border, (self.rect.x, self.rect.y))

    @property
    def is_transparent(self) -> bool:
        """ Returns if the current surface is fully transparent """
        return self._alpha == 0


class Defenders:
    """ Panel that holds defender ui """
    def __init__(self):
        self.width = 100
        self.height = 550
        self.image = pygame.Surface((self.width, self.height))
        self.rect = pygame.Rect(
                650,
                100,
                self.width,
                self.height)
        pygame.draw.rect(
                self.image,
                (255, 255, 255, 255),
                self.rect,
                0,
                5)
        self._alpha = 255

    def draw(self, surface) -> None:
        """ Draw image and rect to surface """
        self.image.set_alpha(self._alpha)
        surface.blit(
                self.image,
                (self.rect.x, self.rect.y))

    @property
    def is_transparent(self) -> bool:
        """ Returns if the current surface is fully transparent """
        return self._alpha == 0


with open(os.path.join("src", "config.json"), 'r', 1, 'utf-8') as config:
    config = json.load(config)

size = (width, height) = config['screen']['width'], config['screen']['height']
fps: int = config.get('fps')
clock = pygame.time.Clock()
screen = pygame.display.set_mode(
        size,
        0,
        (pygame.DOUBLEBUF | pygame.HWACCEL | pygame.DOUBLEBUF),
        vsync=True)

pygame.display.set_caption(os.getcwd())

DONE = False
PLAY = False

buttons = pygame.sprite.Group()
Button(
        "Play",
        100,
        buttons,
        None)
Button(
        "Exit",
        200,
        buttons,
        None)

mouse = [0, 0]

while not DONE:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE or K_q:
                DONE = True
        if event.type == pygame.MOUSEMOTION:
            mouse: list[int] = list(pygame.mouse.get_pos())
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in buttons:
                if pygame.Rect.collidepoint(
                        button.rect,
                        (mouse[0], mouse[1])):
                    if button.text.lower() == 'exit':
                        DONE = True
                    else:
                        PLAY = True
                        DONE = True

    for button in buttons:
        if pygame.Rect.collidepoint(
                button.rect,
                (mouse[0], mouse[1])):
            button.hover = True
        else:
            button.hover = False

    screen.fill((0, 0, 0, 255))

    for button in buttons:
        button.draw(surface=screen)

    pygame.display.update()
    clock.tick(60)

if not PLAY:
    connection.close()
    pygame.quit()
    sys.exit()

DONE = False

ui = pygame.sprite.Group()
defender_panel = Defenders()

while not DONE:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE or K_q:
                DONE = True
        if event.type == pygame.MOUSEMOTION:
            mouse = list(pygame.mouse.get_pos())

    for button in buttons:
        if pygame.Rect.collidepoint(
                button.rect,
                (mouse[0], mouse[1])):
            button.hover = True
        else:
            button.hover = False

    screen.fill(
            (0, 0, 0, 255))

    defender_panel.draw(
            screen)

    pygame.display.update()
    clock.tick(fps)

connection.close()
pygame.quit()
sys.exit()
