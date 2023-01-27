import pygame


def pygame_init() -> None:
    """ Tests all pygame libraries' init status """
    init = True
    if not pygame.display.get_init():
        init = False
    if not pygame.mixer.get_init():
        init = False
    if not pygame.font.get_init():
        init = False
    if not pygame.base.get_init():
        init = False
    assert init is True


if __name__ == "__main__":
    pygame_init()
    print("Tests passed")
