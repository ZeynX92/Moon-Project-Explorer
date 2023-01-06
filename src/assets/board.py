import os
import time
import pygame
from src.tools.load_image import load_image


def tile_image_setup(file, tile_size):
    image = load_image(f"assets/data/{file}.png")
    image = pygame.transform.scale(image, (tile_size, tile_size))
    pygame.draw.rect(image, (175, 238, 238), (0, 0, tile_size, tile_size), 1)
    pygame.draw.line(image, (175, 238, 238), (0, 0), (tile_size, tile_size))
    pygame.draw.line(image, (175, 238, 238), (0, tile_size), (tile_size, 0))

    return image


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type: str, x: int, y: int, offset_x: int, offset_y: int, tiles_group: pygame.sprite.Group,
                 all_sprites: pygame.sprite.Group, tile_size: int = None):
        super().__init__(tiles_group, all_sprites)
        self.player_start_x = None
        self.player_start_y = None
        self.tile_type = tile_type

        self.tile_size = tile_size

        self.x, self.y = x, y
        self.offset_x, self.offset_y = offset_x, offset_y

        self.tile_images = {
            "B": tile_image_setup("ground", tile_size),
            ".": tile_image_setup("ground", tile_size),
            "I": tile_image_setup("iron", tile_size),
            "S": tile_image_setup("stone", tile_size),
            "X": tile_image_setup("button_false", tile_size),
            "L": tile_image_setup("dispenser_false", tile_size),
            "W": tile_image_setup("water", tile_size),
            "P": tile_image_setup("ground", tile_size),
            "R": tile_image_setup("ground", tile_size),
            "E": tile_image_setup("ground", tile_size)
        }

        self.image = self.tile_images[self.tile_type].copy()
        self.rect = self.image.get_rect().move(
            self.tile_size * self.x + self.offset_x, self.tile_size * self.y + self.offset_y)

        if self.tile_type == "B":
            self.box_in_tile = True
        else:
            self.box_in_tile = False

        if self.tile_type == "R" or self.tile_type == "E":
            self.bonus = True
        else:
            self.bonus = False

    def update(self, player_group, player):
        if self.bonus:
            if self.tile_type == "R":
                rocket_image = load_image("assets/data/rocket.png")
                rocket_image = pygame.transform.scale(rocket_image, (self.tile_size, self.tile_size))
                self.image.blit(rocket_image, (0, 0))

            if self.tile_type == "E":
                battery_image = load_image("assets/data/battery.png")
                battery_image = pygame.transform.scale(battery_image, (self.tile_size, self.tile_size))
                self.image.blit(battery_image, (0, 0))

        elif self.box_in_tile:
            box_image = load_image("assets/data/box.png")
            box_image = pygame.transform.scale(box_image, (self.tile_size, self.tile_size))
            self.image.blit(box_image, (0, 0))
        else:
            self.image = self.tile_images[self.tile_type].copy()

        if pygame.sprite.spritecollideany(self, player_group):
            if self.tile_type == "B" and self.box_in_tile:
                # TODO: ЗДЕСЬ НУЖНО ВСТАВИТЬ АНИМАЦИЮ
                player.box_on_board = True
                self.box_in_tile = False
                player.update()

            if self.tile_type == "X" and not self.box_in_tile and player.box_on_board:
                # TODO: ЗДЕСЬ НУЖНО ВСТАВИТЬ АНИМАЦИЮ ТОЖЕ
                player.box_on_board = False
                self.box_in_tile = True

            if self.tile_type == "L" and not player.box_on_board:   # анимация при наезде на кнопку
                player.drop = True
                # player.box_on_board = True

            if self.tile_type == "R" and self.bonus:
                player.rockets += 1
                self.bonus = False

            if self.tile_type == "E" and self.bonus:
                player.energy += 2
                self.bonus = False


class Board:
    def __init__(self, tile_map_file: str, all_sprites: pygame.sprite.Group,
                 tiles_group: pygame.sprite.Group):
        self.board = []
        with open(tile_map_file, "r", encoding="utf8") as tile_map:
            data = tile_map.read().split("\n")
            tile_size = self.tile_size = min((720 - 36) // len(data), (1280 // len(data[0])))
            offset_x = (1280 - tile_size * len(data[0])) // 2
            offset_y = (720 - 36 - tile_size * len(data)) // 2 + 36
            for y in range(len(data)):
                tmp = []
                for x in range(len(data[y])):
                    tmp.append(Tile(data[y][x], x, y, offset_x, offset_y, tiles_group, all_sprites, tile_size))

                    if data[y][x] == "P":
                        self.player_start_x, self.player_start_y = x, y

                self.board.append(tmp)

    def check_win(self):
        cnt_X, cnt_activated_X = 0, 0
        for y in range(len(self.board)):
            for x in range(len(self.board[y])):
                if self.board[y][x].tile_type == "X":
                    cnt_X += 1
                    if self.board[y][x].box_in_tile:
                        cnt_activated_X += 1

        return cnt_X == cnt_activated_X
