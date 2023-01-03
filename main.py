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
    global level, level_num
    level_num += 1
    Time.sleep(0.5)
    level.__del__()
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
        'end': pg.image.load('data/img/exit.png')
    }
    size = 50

    def __init__(self, tile_type, tile_pos, *groups):
        super().__init__(*groups)
        self.image = Tile.images[tile_type]
        self.rect = self.image.get_rect().move(tile_pos[0] * Tile.size,
                                               tile_pos[1] * Tile.size)
        self.type = tile_type

    def step_camera(self, dx, dy):  # фметод перемещения для работы перемещения камеры
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
                            Tile('end', (x, y), self.tile_group)
                        elif sym == 'u':
                            Tile('empty', (x, y), self.tile_group)
                            player = Player((x * Tile.size, y * Tile.size), self.player_group)
                        elif sym == 'e':
                            Tile('empty', (x, y), self.tile_group)
                            enemy = Enemy((x * Tile.size, y * Tile.size), self.enemy_group,
                                          speed=random.randint(200, 350) / 100, diff_level=1)
                        elif sym == 'E':
                            Tile('empty', (x, y), self.tile_group)
                            enemy = Enemy((x * Tile.size, y * Tile.size), self.enemy_group,
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
            else:
                print('-1')
            self.kill()
            return
        '''for enemy in level.get_enemys():  # столкновение с другим иврагом
            if pg.sprite.spritecollideany(self, (enemy,)) and \
                    self != enemy and is_negative(self.speed) == is_negative(enemy.speed):
                self.step(-self.speed, 0, level)'''

    def step_camera(self, dx, dy):  # метод перемещения для работы перемещения камеры
        self.rect = self.rect.move(-1 * dx, -1 * dy)

    def get_info(self):
        return 'enemy', (self.rect.x, self.rect.y)


level = Level('data/levels/1_lvl.txt')

pg.init()
size = width, height = 1000, 650
screen = pg.display.set_mode(size)

clock = pg.time.Clock()
running = True
jump = 0
time = 0

while running:
    screen.fill('black')
    dt = clock.tick(30) / 1000

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

    # физика падения
    level.get_player().physic(dt)

    for enemy in level.enemy_group:  # изика и ии противника
        enemy.ai(level)
        enemy.physic(dt)

    level.draw(screen)
    pg.display.flip()

pg.quit()
