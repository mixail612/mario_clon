import pygame as pg
import random
import time as Time

level_num = 1


def is_negative(num):
    if num < 0:
        return -1
    elif num > 0:
        return 1
    else:
        return 0


def end_world(world_name=''):
    global level, level_num, ftime, timer
    level_num += 1
    Time.sleep(0.5)
    level.__del__()
    Player.score = 0
    Player.hp = 3
    Player.all_score = 0
    ftime = pg.time.get_ticks()
    timer = 150

    music.load("data/sounds/main_track.mp3")
    music.set_volume(0.5)
    music.play(-1)

    if world_name:
        level = Level(world_name)
    else:
        level = Level(f'data/levels/{level_num}_lvl.txt')


def end_game():
    global running
    running = False
    print('end')


class Tile(pg.sprite.Sprite):  # класс стен и препятствий

    images = {
        'wall': pg.image.load('data/img/box.png'),
        'empty': pg.image.load('data/img/grass.png'),
        'end': pg.image.load('data/img/door.png'),
        'open_door': pg.image.load('data/img/open_door.png')
    }
    size = 50

    def __init__(self, tile_type, tile_pos, *groups):
        super().__init__(*groups)
        self.image = Tile.images[tile_type]
        self.rect = self.image.get_rect().move(tile_pos[0] * Tile.size,
                                               tile_pos[1] * Tile.size)
        self.type = tile_type

    def step_camera(self, dx, dy):  # метод перемещения для работы перемещения камеры
        self.rect = self.rect.move(-1 * dx, -1 * dy)

    def get_pos(self):
        return self.rect.x // 50, self.rect.y // 50


class Level:  # класс уровня
    def __init__(self, level_path):
        self.tile_group = pg.sprite.Group()
        self.player_group = pg.sprite.Group()
        self.enemy_group = pg.sprite.Group()
        try:
            with open(level_path, mode='r', encoding='UTF-8') as level_file:  # загрузка уровня
                for x, line in enumerate(level_file):
                    line = line.strip()
                    for y, sym in enumerate(line[::-1]):
                        if sym == '*':
                            Tile('empty', (x, y), self.tile_group)
                        elif sym == '#':
                            Tile('wall', (x, y), self.tile_group)
                        elif sym == 'w':
                            Tile('empty', (x, y), self.tile_group)
                            Tile('end', (x, y), self.tile_group)
                        elif sym == 'u':
                            Tile('empty', (x, y), self.tile_group)
                            Player((x * Tile.size, y * Tile.size), self.player_group)
                        elif sym == 'e':
                            Tile('empty', (x, y), self.tile_group)
                            Enemy((x * Tile.size, y * Tile.size), self.enemy_group,
                                  speed=random.randint(200, 350) / 100, diff_level=1)
                        elif sym == 'E':
                            Tile('empty', (x, y), self.tile_group)
                            Enemy((x * Tile.size, y * Tile.size), self.enemy_group,
                                  speed=random.randint(300, 500) / 100, diff_level=2)
        except BaseException as ex:
            end_game()

    def get_tiles(self):
        return self.tile_group

    def get_tile(self, pos):
        for tile in self.tile_group:
            if pos == tile.get_pos():
                return tile

    def get_enemys(self):
        return self.enemy_group

    def get_player(self):
        return next(iter(self.player_group))

    def draw(self, surface):
        self.tile_group.draw(surface)
        self.player_group.draw(surface)
        self.enemy_group.draw(surface)

    def __del__(self):
        for tile in self.tile_group:
            tile.kill()
        for player in self.player_group:
            player.kill()
        for enemy in self.enemy_group:
            enemy.kill()


class Entity(pg.sprite.Sprite):  # базовый класс движущихся сущностей
    def __init__(self, pos, image, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect().move(pos)
        self.time = 0

    def step(self, dx, dy, level):  # метод перемещения сущности
        self.rect = self.rect.move(dx, dy)

        for tile in pg.sprite.spritecollide(self, level.get_tiles(), False):
            if tile.type == 'wall':
                # в случае если перемещение происходит на препятствие,
                # сущность перемещается на последний пиксель перед ним
                if dy:
                    if dy < 0:
                        self.rect = self.image.get_rect().move(self.rect.x, tile.rect.y + Tile.size)
                    else:
                        self.rect = self.image.get_rect().move(self.rect.x,
                                                               tile.rect.y - Tile.size + (Tile.size - self.rect.height))
                    return - 1
                else:
                    if dx < 0:
                        self.rect = self.image.get_rect().move(tile.rect.x + Tile.size, self.rect.y)
                    else:
                        self.rect = self.image.get_rect().move(tile.rect.x - Tile.size + (Tile.size - self.rect.width),
                                                               self.rect.y)
                    return - 1

    def physic(self, dt):  # метод отвечающий за физику падения

        if self.step(0, self.time * 50, level) == -1:
            self.time = 0
        else:
            self.time += dt

    def get_pos(self):
        return self.rect.x, self.rect.y


class Player(Entity):  # класс игрока

    image = pg.image.load('data/img/mar.png')
    hp = 3
    score = 0
    all_score = 0
    is_died = False

    def __init__(self, pos, *groups):
        super().__init__(pos, Player.image, *groups)
        self.can_jump = 0
        self.jump_speed = 0
        self.jump_time = 0

    def camera_step(self, dx, dy, level):  # метод перемещения камеры
        self.rect = self.rect.move(dx, dy)
        flag = 1

        for tile in pg.sprite.spritecollide(self, level.get_tiles(), False):
            if tile.type == 'wall':
                flag = 0
            if tile.type == 'end':
                tile.image = Tile.images['open_door']
                level.draw(screen)
                pg.display.flip()

                music.load("data/sounds/win_track.mp3")
                music.set_volume(0.5)
                music.play(1)

                # Time.sleep(7) <--- Из-за этого не рисуются сущности

                end_world()

        self.rect = self.rect.move(-1 * dx, -1 * dy)

        if flag:
            for tile in level.get_tiles():
                tile.step_camera(dx, dy)
            for tile in level.get_enemys():
                tile.step_camera(dx, dy)

    def get_info(self):
        return 'player', (self.rect.x, self.rect.y)

    def physic(self, dt):
        if self.step(0, self.time * 50, level) == -1:
            self.time = 0
            self.jump_speed = 0
            self.can_jump = 2
        else:
            level.get_player().step(0, -self.jump_speed * (dt + 0.001) * 50, level)
            self.time += dt
        for tile in pg.sprite.spritecollide(self, level.get_tiles(), False):
            if tile.type == 'end':
                tile.image = Tile.images['open_door']
                level.draw(screen)
                pg.display.flip()
                end_world()

    def jump(self, height):
        if self.can_jump > 0:
            self.jump_speed = height ** 0.5
            level.get_player().step(0, -0.1, level)
            self.can_jump -= 1
            self.time = 0


class Enemy(Entity):
    image = {
        'right': pg.image.load('data/img/dragon_right.png'),
        'left': pg.image.load('data/img/dragon_left.png'),
        'mushroom': pg.image.load('data/img/mushroom.png')
    }

    # start = 0
    # is_hit = False

    def __init__(self, pos, *groups, speed=-2, diff_level=1):
        self.speed = speed
        self.diff_level = diff_level
        if diff_level == 1:
            super().__init__(pos, Enemy.image['mushroom'], *groups)
            self.can_die = True
        elif diff_level == 2:
            super().__init__(pos, Enemy.image['right'], *groups)
            self.can_die = False

    def ai(self, level):
        cant_step = self.step(self.speed, 0, level)
        if cant_step:
            if not (level.get_tile((self.rect.x // 50 - 1, self.rect.y // 50)).type == 'wall' and
                    level.get_tile((self.rect.x // 50 + 1, self.rect.y // 50)).type == 'wall'):
                self.speed *= cant_step
            if self.diff_level == 2:
                if self.speed < 0:
                    self.image = Enemy.image['left']
                else:
                    self.image = Enemy.image['right']

        if pg.sprite.spritecollideany(self, level.player_group):  # обработка столкновение с игроком
            if self.rect.y - self.rect.height // 2 > level.get_player().rect.y and self.can_die:
                print('+1')
                Player.score += 10
                Player.all_score += 10

                if Player.score == 100:
                    Player.score = 0
                    Player.hp += 1

            else:
                print('-1')
                Player.hp -= 1

                # Player.image = pg.image.load('data/img/hit_mar.png')
                # Enemy.is_hit = True
                # Enemy.start = pg.time.get_ticks()

                if Player.hp == 0:
                    print('gg')
                    Player.is_died = True

                    music.load("data/sounds/death_sound.mp3")
                    music.set_volume(0.5)
                    music.play(1)

            self.kill()
            return

    def step_camera(self, dx, dy):  # метод перемещения для работы перемещения камеры
        self.rect = self.rect.move(-1 * dx, -1 * dy)

    def get_info(self):
        return 'enemy', (self.rect.x, self.rect.y)


level_path = 'data/levels/1_lvl.txt'
level = Level('data/levels/1_lvl.txt')

pg.init()

ftime = pg.time.get_ticks()
timer = 150

music = pg.mixer.music
music.load("data/sounds/main_track.mp3")
music.play(-1)
music.set_volume(0.5)

is_other_music = False
tooMuch_time = False

font = pg.font.SysFont('Super Mario 128', 50)

size = width, height = 1000, 700

screen = pg.display.set_mode(size)

clock = pg.time.Clock()
running = True
jump = 0
time = 0

while running:
    screen.fill('black')
    dt = clock.tick(30) / 1000

    if (pg.time.get_ticks() - ftime) // 1000 == 1 and not Player.is_died:
        ftime = pg.time.get_ticks()
        timer -= 1

        if timer <= 60 and not is_other_music:
            music.load("data/sounds/hurry_track.mp3")
            music.play(-1)
            is_other_music = True

        elif timer <= 0:
            Player.is_died = True
            music.load("data/sounds/death_sound.mp3")
            music.play(1)
            tooMuch_time = True

    if not Player.is_died:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_w or event.key == pg.K_UP:  # прыжок
                    level.get_player().jump(135)

        if pg.key.get_pressed()[pg.K_LEFT] or pg.key.get_pressed()[pg.K_a]:  # хождение вперед, назад
            level.get_player().camera_step(-7, 0, level)
        if pg.key.get_pressed()[pg.K_RIGHT] or pg.key.get_pressed()[pg.K_d]:
            level.get_player().camera_step(7, 0, level)

        # if Enemy.is_hit:
        #     sec = (pg.time.get_ticks() - Enemy.start) / 1000
        #
        #     if sec >= 1:
        #         print(1)
        #         Player.image = pg.image.load('data/img/mar.png')
        #         Enemy.is_hit = False

        # физика падения
        level.get_player().physic(dt)

        for enemy in level.enemy_group:  # физика и ии противника
            enemy.ai(level)
            enemy.physic(dt)

        score_label = font.render(f"Score: {Player.score}", True, (255, 255, 255), (0, 0, 0))
        hp_label = font.render(f"hp x {Player.hp}", True, (255, 255, 255), (0, 0, 0))
        time_label = font.render(f"Time: {timer}", False, (255, 255, 255), (0, 0, 0))

        level.draw(screen)
        screen.blit(time_label, (440, 660))
        screen.blit(score_label, (30, 660))
        screen.blit(hp_label, (870, 660))
    else:
        game_over = font.render(f"Game over!", False, (255, 255, 255), (0, 0, 0))
        final_score = font.render(f"Your score: {Player.all_score}!", True, (255, 255, 255), (0, 0, 0))
        if not tooMuch_time:
            time_table = font.render(f"Time: {150 - timer}", True, (255, 255, 255), (0, 0, 0))
            screen.blit(time_table, (440, 350))
        else:
            time_table = font.render(f"Time: Too Much!", True, (255, 150, 150), (0, 0, 0))
            screen.blit(time_table, (370, 350))
        advice = font.render(f"Press any button to continue", True, (255, 255, 255), (0, 0, 0))

        screen.blit(game_over, (405, 250))
        screen.blit(final_score, (385, 300))
        screen.blit(advice, (267, 425))

        Time.sleep(0.8)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN or event.type == pg.MOUSEBUTTONDOWN:
                Player.is_died = False
                Player.hp = 3
                Player.score = 0
                Player.all_score = 0
                level = Level(level_path)
                timer = 150
                ftime = pg.time.get_ticks()

                music.load("data/sounds/main_track.mp3")
                music.play(-1)

    pg.display.flip()

pg.quit()
