import sys
import os
import pygame


def load_image(path, colorkey=None):
    if not os.path.isfile(path):
        print(f"Файл с изображением '{path}' не найден")
        sys.exit()
    image = pygame.image.load(path)
    return image
