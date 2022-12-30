import pygame as pg
import random


def is_negative(num):
    if num < 0:
        return -1
    elif num > 0:
        return 1
    else:
        return 0


class Tile(pg.sprite.Sprite):  # класс стен и препятствий

    images = {
        'wall': pg.image.load('data/img/box.png'),
        'empty': pg.image.load('data/img/grass.png')
    }
    size = 50

    def __init__(self, tile_type, tile_pos, *groups):
        super().__init__(*groups)
        self.image = Tile.images[tile_type]
        self.rect = self.image.get_rect().move(tile_pos[0] * Tile.size,
                                               tile_pos[1] * Tile.size)
        self.type = tile_type

    def step_camera(self, dx, dy):  # фметод перемещения для работы перемещения камеры
        self.rect = self.rect.move(-1 * dx * Tile.size, -1 * dy * Tile.size)


class Level:  # класс уровня
    def __init__(self, level_path):
        self.tile_group = pg.sprite.Group()
        self.player_group = pg.sprite.Group()
        self.enemy_group = pg.sprite.Group()
        flag = 0
        while flag == 0:
            try:
                with open(level_path, mode='r', encoding='UTF-8') as level_file:  # загрузка уровня
                    for x, line in enumerate(level_file):
                        line = line.strip()
                        for y, sym in enumerate(line[::-1]):
                            if sym == '*':
                                Tile('empty', (x, y), self.tile_group)
                            elif sym == '#':
                                Tile('wall', (x, y), self.tile_group)
                            elif sym == 'u':
                                Tile('empty', (x, y), self.tile_group)
                                player = Player((x * Tile.size, y * Tile.size), self.player_group)
                            elif sym == 'e':
                                Tile('empty', (x, y), self.tile_group)
                                enemy = Enemy((x * Tile.size, y * Tile.size), self.enemy_group,
                                              speed=random.randint(30, 70) / 1000)
                            elif sym == 'E':
                                Tile('empty', (x, y), self.tile_group)
                                enemy = Enemy((x * Tile.size, y * Tile.size), self.enemy_group,
                                              speed=random.randint(70, 140) / 1000, can_die=False)
                flag = 1
            except BaseException as ex:
                print('файл не найден, попробуйте ещё раз', ex)
                level_path = input()

    def get_tiles(self):
        return self.tile_group

    def get_enemys(self):
        return self.enemy_group

    def get_player(self):
        return next(iter(self.player_group))

    def draw(self, surface):
        self.tile_group.draw(surface)
        self.player_group.draw(surface)
        self.enemy_group.draw(surface)


class Entity(pg.sprite.Sprite):  # базовый класс движущихся сущностей
    def __init__(self, pos, image, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect().move(pos)
        self.time = 0

    def step(self, dx, dy, level):  # метод перемещения сущности
        self.rect = self.rect.move(dx * Tile.size, dy * Tile.size)

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
        self.time += dt
        if self.step(0, self.time, level) == -1:
            self.time = 0


class Player(Entity):  # класс игрока

    image = pg.image.load('data/img/mar.png')

    def __init__(self, pos, *groups):
        super().__init__(pos, Player.image, *groups)
        self.can_jump = 0
        self.jump_height = 0
        self.jump_time = 0

    def camera_step(self, dx, dy, level):  # метод перемещения камеры
        self.rect = self.rect.move(dx * Tile.size, dy * Tile.size)
        flag = 1
        for tile in pg.sprite.spritecollide(self, level.get_tiles(), False):
            if tile.type == 'wall':
                self.rect = self.rect.move(-1 * dx * Tile.size, -1 * dy * Tile.size)
                flag = 0
        if flag:
            self.rect = self.rect.move(-1 * dx * Tile.size, -1 * dy * Tile.size)
            for tile in level.get_tiles():
                tile.step_camera(dx, dy)
            for tile in level.get_enemys():
                tile.step_camera(dx, dy)

    def get_info(self):
        return 'player', (self.rect.x, self.rect.y)

    def jump_physic(self, dt):
        if self.jump_height > 0:  # физика прыжка
            if self.jump_time == 0:
                self.jump_time = self.jump_height ** 0.5 / 4
            jump_delta = (self.jump_time * 4) ** 2 - ((self.jump_time - dt) * 4) ** 2
            level.get_player().step(0, -jump_delta, level)
            self.jump_height -= jump_delta
            self.jump_time -= dt
            if jump_delta <= 0.01:
                self.jump_height = -1
                self.time = 0

    def jump(self, height):
        if self.can_jump >= 0:
            self.jump_height = height
            self.jump_time = 0
            if self.can_jump >= 0.35:
                self.can_jump = 0
            else:
                self.can_jump = -0.35



class Enemy(Entity):
    image = pg.image.load('data/img/mar.png')

    def __init__(self, pos, *groups, speed=-0.05, can_die=True):
        super().__init__(pos, Enemy.image, *groups)
        self.speed = speed
        self.can_die = can_die

    def ai(self, level):
        cant_step = self.step(self.speed, 0, level)
        if cant_step:
            self.speed *= cant_step
        if pg.sprite.spritecollideany(self, level.player_group):  # обработка столкновение с игроком
            if self.rect.y > level.get_player().rect.y and self.can_die:
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
        self.rect = self.rect.move(-1 * dx * Tile.size, -1 * dy * Tile.size)

    def get_info(self):
        return 'enemy', (self.rect.x, self.rect.y)


level = Level(input())

pg.init()
size = width, height = 600, 450
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
                level.get_player().jump(2.5)

    if pg.key.get_pressed()[pg.K_LEFT] or pg.key.get_pressed()[pg.K_a]:  # хождение вперед, назад
        level.get_player().camera_step(-0.14, 0, level)
    if pg.key.get_pressed()[pg.K_RIGHT] or pg.key.get_pressed()[pg.K_d]:
        level.get_player().camera_step(0.14, 0, level)

    # физика падения
    if level.get_player().jump_height <= 0:
        level.get_player().physic(dt)
    level.get_player().can_jump += dt
    level.get_player().jump_physic(dt)

    for enemy in level.enemy_group: # изика и ии противника
        enemy.ai(level)
        enemy.physic(dt)

    level.draw(screen)
    pg.display.flip()

pg.quit()
