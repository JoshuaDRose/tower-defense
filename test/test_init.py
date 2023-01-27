import os
import pygame
from unittest import TestCase as tc


class test_init(tc):
    def test_pygame_init(self) -> None:
        """ Tests all pygame libraries' init status """
        flag = True
        try:
            pygame.init()
        finally:
            if not pygame.display.get_init():
                flag = False
            if not pygame.mixer.get_init():
                flag = False
            if not pygame.font.get_init():
                flag = False
            if not pygame.base.get_init():
                flag = False
        self.assertTrue(flag)

    def test_file_walk(self) -> None:
        """ Ensures all files are present """
        files = [file for file in os.listdir('src')]
        flag = '__main__.py' or 'config.json' in files
        self.assertTrue(flag)
