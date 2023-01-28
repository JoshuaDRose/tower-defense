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
import mysql.connector as database
import pygame
import os
import json
import colorama
import subprocess
from loguru import logger
from pygame import K_ESCAPE, KEYDOWN, K_q
from datetime import datetime as dt

pygame.init()
colorama.deinit()

logger.remove()


class Formatter:

    def __init__(self):
        self.padding = 0
        self.fmt = "[{time}] <level>{name}:{function}{extra[padding]}</level> {message}\n{exception}"

    def format(self, record):
        length = len("{name}:{function}:{line}".format(**record))
        self.padding = max(self.padding, length)
        record["extra"]["padding"] = " " * (self.padding - length)
        return self.fmt


formatter = Formatter()

logger.remove()
logger.add(sys.stderr, format=formatter.format)


class User:
    def __init__(self):
        self.name = os.environ.get("username")
        self.psw = os.environ.get("password")


"""
+---------+------------+------+-----+---------+-------+
| Field   | Type       | Null | Key | Default | Extra |
+---------+------------+------+-----+---------+-------+
| RunID   | int(11)    | YES  |     | NULL    |       |
| Date    | date       | YES  |     | NULL    |       |
| Success | tinyint(1) | YES  |     | NULL    |       |
+---------+------------+------+-----+---------+-------+
"""


class Database(object):
    """ Database records test runs and errors """
    def __init__(self):
        self.user = User()
        self.config = dict()
        with open(os.path.join(
                'src', 'connector.json'), 'r', 1, 'utf-8') as fp:
            self.config = json.load(fp)
        self.connection = database.connect(**self.config)
        self.cursor = self.connection.cursor()
        logger.debug("connected to {} as {}".format(
            self.config['host'], self.config['user']))
        self.tables = ["Run"]
        self.current_table = 0

    def add_entry(self, success=True) -> None:
        """ States if run is success (bool) """
        try:
            date = dt.now().strftime("%Y-%m-%d")
            statement = """INSERT INTO Run (RunID,Date,Success) VALUES (%s, %s, %s)"""
            success = 1 if success else 0
            self.cursor.execute(statement, (self.id, date, success))
        except database.Error as error:
            logger.error(f"Error adding entry to database: {error}")

    @property
    def id(self) -> int:
        stdout = subprocess.check_output(['bash', 'mariadb_run.sh'])
        return int(stdout.decode('utf-8').strip())

    @staticmethod
    def increment_id() -> None:
        subprocess.run(['source', 'mariadb_run.sh'])


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


db = Database()

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
    db.connection.close()
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

db.add_entry(success=True)

db.connection.close()
pygame.quit()
sys.exit()
