import pygame
from src.tools.load_image import load_image


def player_setup_image(tile_size):
    image = load_image("src/assets/data/lunar.png")
    image = pygame.transform.scale(image, (tile_size, tile_size))
    image = pygame.transform.rotate(image, 270)

    return image


class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, box_on_board: bool, energy: int, rockets: int,
                 tile_size: int, player_group: pygame.sprite.Group, all_sprites: pygame.sprite.Group, board):
        super().__init__(player_group, all_sprites)
        self.current_angle = 0
        self.x, self.y = x, y
        self.board = board
        self.tile_size = tile_size
        self.pr_x, self.pr_y = x - 1, y
        self.pr_velocity = None

        self.box_on_board = box_on_board
        self.energy = energy
        self.rockets = rockets

        # self.image = player_zaglushka((255, 0, 0), tile_size).copy()
        self.image = player_setup_image(tile_size).copy()

        self.rect = self.image.get_rect().move(
            tile_size * self.x + board[0][0].offset_x,
            tile_size * self.y + board[0][0].offset_y)

        self.setup = True

    def update(self, velocity=None):
        if velocity:
            self.pr_x, self.pr_y = self.x, self.y

            if self.energy > 0:
                if velocity == 1:
                    self.x -= 1
                if velocity == 2:
                    self.x += 1
                if velocity == 3:
                    self.y -= 1
                if velocity == 4:
                    self.y += 1

            if not (0 <= self.x < len(self.board[0])) or not (
                    0 <= self.y < len(self.board)) or self.board[self.y][self.x].tile_type in ["W", "S", "I"]:
                self.x, self.y = self.pr_x, self.pr_y
            else:
                self.energy -= 1
                # TODO: СЮДА АНИМАЦИЮ
                self.rect.x = self.tile_size * self.x + self.board[0][0].offset_x
                self.rect.y = self.tile_size * self.y + self.board[0][0].offset_y

                if self.pr_velocity != velocity:
                    if self.pr_x - self.x < 0:
                        self.image = pygame.transform.rotate(player_setup_image(self.tile_size), 0)
                        self.current_angle = 0

                    if self.pr_x - self.x > 0:
                        self.image = pygame.transform.rotate(player_setup_image(self.tile_size), 180)
                        self.current_angle = 180

                    if self.pr_y - self.y > 0:
                        self.image = pygame.transform.rotate(player_setup_image(self.tile_size), 90)
                        self.current_angle = 90

                    if self.pr_y - self.y < 0:
                        self.image = pygame.transform.rotate(player_setup_image(self.tile_size), 270)
                        self.current_angle = 270

                self.pr_velocity = velocity

        if self.box_on_board:
            box_image = load_image("src/assets/data/box.png")
            box_image = pygame.transform.scale(box_image, (self.tile_size, self.tile_size))
            self.image.blit(box_image, (0, 0))
        else:
            self.image = pygame.transform.rotate(player_setup_image(self.tile_size), self.current_angle)

    def rocket_launch(self):
        global direction
        if self.rockets:
            self.rockets -= 1

            if self.pr_x - self.x != 0:
                direction = ["x", 0]
            if self.pr_y - self.y != 0:
                direction = ["y", 0]

            if direction[0] == "x":
                if self.pr_x - self.x > 0:
                    direction[1] = -1

                if self.pr_x - self.x < 0:
                    direction[1] = +1

            if direction[0] == "y":
                if self.pr_y - self.y > 0:
                    direction[1] = -1

                if self.pr_y - self.y < 0:
                    direction[1] = +1

            if direction[0] == "x":
                if direction[1] == +1:
                    for x in range(self.x + 1, len(self.board[0])):
                        # TODO: И СЮДА АНИМАЦИЮ НАДО
                        if self.board[self.y][x].tile_type == "I" or self.board[self.y][x].tile_type == "S":
                            print("BOOM")
                            self.board[self.y][x].tile_type = "."
                            break
                else:
                    for x in range(self.x - 1, 0 - 1, -1):
                        # TODO: И СЮДА АНИМАЦИЮ НАДО ТОЖЕ
                        if self.board[self.y][x].tile_type == "I" or self.board[self.y][x].tile_type == "S":
                            print("BOOM")
                            self.board[self.y][x].tile_type = "."
                            break

            if direction[0] == "y":
                if direction[1] == +1:
                    for y in range(self.y + 1, len(self.board)):
                        # TODO: ДА И СЮДА ТОЖЕ
                        if self.board[y][self.x].tile_type == "I" or self.board[y][self.x].tile_type == "S":
                            print("BOOM")
                            self.board[y][self.x].tile_type = "."
                            break
                else:
                    for y in range(self.y - 1, 0 - 1, -1):
                        # TODO: УГАДАЙ, ЧТО
                        if self.board[y][self.x].tile_type == "I" or self.board[y][self.x].tile_type == "S":
                            print("BOOM")
                            self.board[y][self.x].tile_type = "."
                            break

    def laser_launch(self):
        # TODO: ЗДЕСЬ АНАЛОГИЧНО С ROCKET_LAUNCH
        global direction
        if self.energy:
            self.energy -= 1

            if self.pr_x - self.x != 0:
                direction = ["x", 0]
            if self.pr_y - self.y != 0:
                direction = ["y", 0]

            if direction[0] == "x":
                if self.pr_x - self.x > 0:
                    direction[1] = -1

                if self.pr_x - self.x < 0:
                    direction[1] = +1

            if direction[0] == "y":
                if self.pr_y - self.y > 0:
                    direction[1] = -1

                if self.pr_y - self.y < 0:
                    direction[1] = +1

            if direction[0] == "x":
                if direction[1] == +1:
                    for x in range(self.x + 1, len(self.board[0])):
                        if self.board[self.y][x].tile_type == "S":
                            print("BOOM")
                            self.board[self.y][x].tile_type = "."
                            break
                else:
                    for x in range(self.x - 1, 0 - 1, -1):
                        if self.board[self.y][x].tile_type == "S":
                            print("BOOM")
                            self.board[self.y][x].tile_type = "."
                            break

            if direction[0] == "y":
                if direction[1] == +1:
                    for y in range(self.y + 1, len(self.board)):
                        if self.board[y][self.x].tile_type == "S":
                            print("BOOM")
                            self.board[y][self.x].tile_type = "."
                            break
                else:
                    for y in range(self.y - 1, 0 - 1, -1):
                        if self.board[y][self.x].tile_type == "S":
                            print("BOOM")
                            self.board[y][self.x].tile_type = "."
                            break
