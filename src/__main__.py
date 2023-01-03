import sys
import pygame
import webbrowser
import csv
from assets.board import Board
from tools.load_image import load_image
from assets.player import Player

WIDTH, HEIGHT = 1280, 720

pygame.init()
size = width, height = WIDTH, HEIGHT
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


def start_screen():
    main_screen_image = pygame.transform.scale(load_image("src/assets/data/main_screen.png"), (WIDTH, HEIGHT))
    start_button_image = pygame.transform.scale(load_image("src/assets/data/start.png"), (151, 151))
    help_button_image = pygame.transform.scale(load_image("src/assets/data/help.png"), (151, 151))

    screen.blit(main_screen_image, (0, 0))
    screen.blit(start_button_image, (180, 385))
    screen.blit(help_button_image, (180 + 151 + 35, 385))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                cx_1, cy_1 = 180 + 151 * 0.5, 385 + 151 * 0.5
                cx_2, cy_2 = 180 + 151 + 35 + 151 * 0.5, 385 + 151 * 0.5
                if (x - cx_1) ** 2 + (y - cy_1) ** 2 <= (151 * 0.5) ** 2:
                    load_level(1)
                if (x - cx_2) ** 2 + (y - cy_2) ** 2 <= (151 * 0.5) ** 2:
                    webbrowser.open_new_tab(
                        "https://www.notion.so/moon-project-explorer-tutorial/Moon-Project-Explorer-10b9851795134a4891453298c8660669")
        pygame.display.flip()


def fin_screen(level_data, player, win: bool):
    with open(f'src/assets/data/levels.csv', "r", encoding="utf8") as csv_file:
        reader = csv.reader(csv_file, delimiter=';', quotechar='"')
        data = []
        for index, row in enumerate(reader):
            data.append(row)

    with open(f'src/assets/data/levels.csv', "w", encoding="utf8", newline="") as csv_file:
        writer = csv.writer(
            csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for line in data:
            line = [i.rstrip() for i in line]
            if line[0] == str(level_data[0]):
                line[-1] = min(int(level_data[-1]), int(100 - player.energy * 100 / int(level_data[-2])))
            writer.writerow(line)

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if win:
                    load_level(int(level_data[0]) + 1)
                else:
                    load_level(int(level_data[0]))

        pygame.draw.rect(screen, (0, 20, 132), (WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2))
        pygame.draw.rect(screen, (255, 255, 255), (WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2), 5)

        if win:
            font = pygame.font.Font(None, 60)
            title = font.render(f"Mission CLEARED", True, (175, 238, 238))
            screen.blit(title, (WIDTH // 2.75, HEIGHT // 3.75))

            font = pygame.font.Font(None, 40)
            result_1 = font.render(
                f"Total Energy Сonsumption: {int(level_data[1]) - player.energy}", True, (175, 238, 238))

            screen.blit(result_1, (WIDTH // 2.75, HEIGHT // 3.75 + title.get_height()))

            result_2 = font.render(
                f"Deviation from AI: {int(100 - player.energy * 100 / int(level_data[-2]))}%", True, (175, 238, 238)
            )
            screen.blit(result_2, (WIDTH // 2.75, HEIGHT // 3.75 + title.get_height() + result_1.get_height()))

            result_3 = font.render(
                f"The Best Result: {min(int(level_data[-1]), int(100 - player.energy * 100 / int(level_data[-2])))}%",
                True, (175, 238, 238))
            screen.blit(result_3, (
                WIDTH // 2.75, HEIGHT // 3.75 + title.get_height() + result_1.get_height() + result_2.get_height()))

        else:
            font = pygame.font.Font(None, 60)
            title = font.render(f"Mission FAILED", True, (175, 238, 238))
            screen.blit(title, (WIDTH // 2.75, HEIGHT // 3.75))

            result_3 = font.render(
                f"The Best Result: {min(int(level_data[-1]), int(100 - player.energy * 100 / int(level_data[-2])))}%",
                True,
                (175, 238, 238)
            )
            screen.blit(result_3, (
                WIDTH // 2.75, HEIGHT // 3.75 + title.get_height()))

        pygame.display.flip()


def load_level(level: int):
    with open(f'src/assets/data/levels.csv', encoding="utf8") as csv_file:
        reader = csv.reader(csv_file, delimiter=';', quotechar='"')
        for index, row in enumerate(reader):
            if index == level:
                level_data = [i.rstrip() for i in row]
                break

    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()

    board = Board(f"src/assets/levels/{level_data[3]}", tiles_group, all_sprites)
    player = Player(board.player_start_x, board.player_start_y, False, int(level_data[1]),
                    int(level_data[2]), board.tile_size,
                    player_group,
                    all_sprites, board.board)

    running = True
    FPS = 30
    while running:
        screen.fill((0, 0, 0))

        # СТРОКА СОСТОЯНИЯ
        pygame.draw.rect(screen, (0, 20, 132), (0, 0, WIDTH, HEIGHT // 20))
        font = pygame.font.Font(None, 50)
        text = font.render(f"Energy: {player.energy}    Rockets: {player.rockets}                   Level {level}",
                           True, (175, 238, 238))
        screen.blit(text, (0, 0))

        # ИГРОВОЙ ЦИКЛ
        tiles_group.draw(screen)
        player_group.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.update(1)
                if event.key == pygame.K_RIGHT:
                    player.update(2)
                if event.key == pygame.K_UP:
                    player.update(3)
                if event.key == pygame.K_DOWN:
                    player.update(4)
                if event.key == pygame.K_LCTRL:
                    player.rocket_launch()
                if event.key == pygame.K_SPACE:
                    player.laser_launch()
                if event.key == pygame.K_r:
                    load_level(level)
                if event.key == pygame.K_ESCAPE:
                    start_screen()

        tiles_group.update(player_group, player)

        clock.tick(FPS)
        pygame.display.flip()

        if board.check_win():
            tiles_group.draw(screen)
            player_group.draw(screen)
            fin_screen(level_data, player, 1)
            break

        if player.energy <= 0:
            tiles_group.draw(screen)
            player_group.draw(screen)
            fin_screen(level_data, player, 0)
            break


# load_level(1)
start_screen()
