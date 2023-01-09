import pygame
from tools.load_image import load_image


def player_setup_image(tile_size, image_name="lunar.png", rotate_direction=None):
    """А: Функция для подготовки изображения игрока для подгонки к адаптивного полю"""
    if image_name == "lunar.png":
        image = load_image(f"assets/data/{image_name}")
    else:
        image = load_image(f"{image_name}")
    image = pygame.transform.scale(image, (tile_size, tile_size))
    if rotate_direction == "вверх":
        image = pygame.transform.rotate(image, 0)
    elif rotate_direction == "вправо":
        image = pygame.transform.rotate(image, -90)
    elif rotate_direction == "влево":
        image = pygame.transform.rotate(image, -270)
    elif rotate_direction == "вниз":
        image = pygame.transform.rotate(image, -180)
    else:
        image = pygame.transform.rotate(image, 270)

    return image


"""От: В
ЕСЛИ УСПЕЮ/НЕ ЛЕНЬ БУДЕТ СДЕЛАТЬ ЛЕТЯЩИЙ СНАРЯД

class Ammunition(pygame.sprite.Sprite):
   def __init__(self, x: int, y: int, kudarotate, laser_or_rocket, tile_size):
       super().__init__()
       self.x = x
       self.y = y
       self.kudarotate = kudarotate
       self.tile_size = tile_size
       if laser_or_rocket == "laser":
           self.image = player_setup_image(self.tile_size, image_name="assets\data\laser.png",
                                           rotate_direction=self.kudarotate)
       else:
           # ЗАГЛУШКА ДЛЯ РАКЕТЫ
           self.image = player_setup_image(self.tile_size, image_name="assets\data\laser.png",
                                           rotate_direction=self.kudarotate)

   def fly(self):
       if self.kudarotate == "вверх":
           self.rect.y -= 12
       elif self.kudarotate == "вправо":
           self.rect.x += 12
       elif self.kudarotate == "вниз":
           self.rect.y += 12
       elif self.kudarotate == "влево":
           self.rect.x -= 12"""


class Player(pygame.sprite.Sprite):
    """A: Класс игрока, который обрабатывает управление пользователе и позволяет игроку взаимодействовать с полем"""
    def __init__(self, x: int, y: int, box_on_board: bool, energy: int, rockets: int,
                 tile_size: int, player_group: pygame.sprite.Group, all_sprites: pygame.sprite.Group,
                 board):
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

        # для анимации падания
        self.drop = False
        self.frame_counter = 1
        self.anim_active = False

        # для анимации езды
        self.rotate_direction = None
        self.is_drive = False
        self.steps = 3
        self.vel = None

        # для анимации стрельбы
        self.is_shooting = False
        self.numshoot = 1
        self.ammunition = "laser"

        self.image = player_setup_image(tile_size).copy()
        self.rect = self.image.get_rect().move(
            tile_size * self.x + board[0][0].offset_x,
            tile_size * self.y + board[0][0].offset_y)

        self.setup = True

    def update(self, velocity=None):
        """A: Функция, которая вызывается при обновлении состояния игрока"""
        if velocity:
            self.pr_x, self.pr_y = self.x, self.y
            if not self.is_drive and self.energy > 0:
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
            self.image = player_setup_image(self.tile_size, image_name=f"assets\data\sprites\drop\\5.png")
            self.image = pygame.transform.rotate(self.image,
                                                 self.current_angle)
        else:
            self.image = pygame.transform.rotate(player_setup_image(self.tile_size),
                                                 self.current_angle)

    def animation_drop(self):
        """В: Функция воспроизведения анимации падения ящика с небес"""
        if self.drop and self.frame_counter < 6:
            self.image = pygame.transform.rotate(player_setup_image(self.tile_size,
                                                                    image_name=f"assets\data\sprites\drop\\{self.frame_counter}.png"),
                                                 self.current_angle)
            self.frame_counter += 1
        else:
            self.drop = False
            self.frame_counter = 1

        if self.frame_counter == 6:
            self.image = pygame.transform.rotate(player_setup_image(self.tile_size,
                                                                    image_name=f"assets\data\sprites\drop\\{5}.png"),
                                                 self.current_angle)
            self.box_on_board = True

    def drive(self, vel=None):
        """B: Функция воспроизведения анимации езды"""
        if self.is_drive is False:
            return
        self.vel = vel
        if vel:
            try:
                if vel == 1:
                    if self.board[self.y][self.x - 1].tile_type in ["W", "S", "I"] or not (
                            0 <= self.x - 1 < len(self.board[0])):
                        self.is_drive = False
                        return
                if vel == 2:
                    if self.board[self.y][self.x + 1].tile_type in ["W", "S", "I"] or not (
                            0 <= self.x + 1 < len(self.board[0])):
                        self.is_drive = False
                        return
                if vel == 3:
                    if self.board[self.y - 1][self.x].tile_type in ["W", "S", "I"] or not (
                            0 <= self.y - 1 < len(self.board)):
                        self.is_drive = False
                        return
                if vel == 4:
                    if self.board[self.y + 1][self.x].tile_type in ["W", "S", "I"] or not (
                            0 <= self.y + 1 < len(self.board)):
                        self.is_drive = False
                        return
            except Exception:
                self.is_drive = False
                return
        if self.steps == 9:
            self.is_drive = False
            self.steps = 1
            self.update(self.vel)
        else:
            path = "drive"
            if self.box_on_board:
                path = "drivebox"
            self.image = player_setup_image(self.tile_size,
                                            image_name=f"assets\data\sprites\{path}\\{self.steps}.png",
                                            rotate_direction=self.rotate_direction)
            if self.rotate_direction == "вверх":
                self.rect.y -= 12
            elif self.rotate_direction == "вправо":
                self.rect.x += 12
            elif self.rotate_direction == "вниз":
                self.rect.y += 12
            elif self.rotate_direction == "влево":
                self.rect.x -= 12
            self.steps += 1

    def rocket_launch(self):
        """А: Функция обрабатывающая стрельбу по лунному железняку"""
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
                        if self.board[self.y][x].tile_type == "I" or self.board[self.y][x].tile_type == "S":
                            self.board[self.y][x].tile_type = "."
                            break
                else:
                    for x in range(self.x - 1, 0 - 1, -1):
                        if self.board[self.y][x].tile_type == "I" or self.board[self.y][x].tile_type == "S":
                            self.board[self.y][x].tile_type = "."
                            break

            if direction[0] == "y":
                if direction[1] == +1:
                    for y in range(self.y + 1, len(self.board)):
                        if self.board[y][self.x].tile_type == "I" or self.board[y][self.x].tile_type == "S":
                            self.board[y][self.x].tile_type = "."
                            break
                else:
                    for y in range(self.y - 1, 0 - 1, -1):
                        if self.board[y][self.x].tile_type == "I" or self.board[y][self.x].tile_type == "S":
                            self.board[y][self.x].tile_type = "."
                            break

    def shooting(self, ammunition=None):  # 1 - стрельба лазером, 2 - стрельба ракетой
        """В: Функция воспроизведение анимации стрельбы"""
        if ammunition is not None:
            self.ammunition = ammunition
        if self.is_shooting is False:
            return
        if self.box_on_board is True:
            self.is_shooting = False
            return
        if self.numshoot == 6:
            self.is_shooting = False
            self.numshoot = 1
            self.image = player_setup_image(self.tile_size,
                                            image_name=f"assets\data\lunar.png",
                                            rotate_direction=self.rotate_direction)
            if self.ammunition == "rocket":
                self.rocket_launch()
            else:
                self.laser_launch()
        else:
            path = "shoot_laser"
            if self.ammunition == "rocket":
                path = "shoot_rocket"
            self.image = player_setup_image(self.tile_size,
                                            image_name=f"assets\data\sprites\{path}\\{self.numshoot}.png",
                                            rotate_direction=self.rotate_direction)
            self.numshoot += 1

    def laser_launch(self):
        """А: Функция обрабатывающая стрельбу по лунной породе"""
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
                            self.board[self.y][x].tile_type = "."
                            break
                else:
                    for x in range(self.x - 1, 0 - 1, -1):
                        if self.board[self.y][x].tile_type == "S":
                            self.board[self.y][x].tile_type = "."
                            break

            if direction[0] == "y":
                if direction[1] == +1:
                    for y in range(self.y + 1, len(self.board)):
                        if self.board[y][self.x].tile_type == "S":
                            self.board[y][self.x].tile_type = "."
                            break
                else:
                    for y in range(self.y - 1, 0 - 1, -1):
                        if self.board[y][self.x].tile_type == "S":
                            self.board[y][self.x].tile_type = "."
                            break
