import pygame as pg


class Tile(pg.sprite.Sprite):#класс стен и препятствий

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

    def step(self, dx, dy):# фметод перемещения для работы перемещения камеры
        self.rect = self.rect.move(-1 * dx * Tile.size, -1 * dy * Tile.size)


class Level:# класс уровня
    def __init__(self, level_path):
        self.tile_group = pg.sprite.Group()
        self.player_group = pg.sprite.Group()
        flag = 0
        while flag == 0:
            try:
                with open(level_path, mode='r', encoding='UTF-8') as level_file: # загрузка уровня
                    for x, line in enumerate(level_file):
                        line = line.strip()
                        for y,sym in enumerate(line[::-1]):
                            if sym == '*':
                                Tile('empty', (x, y), self.tile_group)
                            elif sym == '#':
                                Tile('wall', (x, y), self.tile_group)
                            elif sym == 'u':
                                Tile('empty', (x, y), self.tile_group)
                                player = Player((x * Tile.size, y * Tile.size), self.player_group)
                flag = 1
            except:
                print('файл не найден, попробуйте ещё раз')
                level_path = input()


    def get_tiles(self):
        return self.tile_group

    def get_player(self):
        return next(iter(self.player_group))

    def draw(self, surface):
        self.tile_group.draw(surface)
        self.player_group.draw(surface)



class Player(pg.sprite.Sprite):# класс игрока

    image = pg.image.load('data/img/mar.png')

    def __init__(self, pos, *groups):
        super().__init__(*groups)
        self.image = Player.image
        self.rect = self.image.get_rect().move(pos)

    def step(self, dx, dy, level):# метод перемещения игрока
        self.rect = self.rect.move(dx * Tile.size, dy * Tile.size)
        for tile in pg.sprite.spritecollide(self, level.get_tiles(), False):
            if tile.type == 'wall':# в случае если перемещение происходит на препятствие, игрок перемещается на последний пиксель перед ним
                if dy < 0:
                    self.rect = self.image.get_rect().move(self.rect.x, tile.rect.y + 50)
                else:
                    self.rect = self.image.get_rect().move(self.rect.x, tile.rect.y - 50 + (50 - self.rect.height))
                return - 1

    def camera_step(self, dx, dy, level): # метод перемещения камеры
        self.rect = self.rect.move(dx * Tile.size, dy * Tile.size)
        flag = 1
        for tile in pg.sprite.spritecollide(self, level.get_tiles(), False):
            if tile.type == 'wall':
                self.rect = self.rect.move(-1 * dx * Tile.size, -1 * dy * Tile.size)
                flag = 0
        if flag:
            self.rect = self.rect.move(-1 * dx * Tile.size, -1 * dy * Tile.size)
            for tile in level.get_tiles():
                tile.step(dx, dy)

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
    dt = clock.tick(60) / 1000

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_w or event.key == pg.K_UP:# прыжок
                jump = 2.5

    if pg.key.get_pressed()[pg.K_LEFT]:# хождение вперед, назад
        level.get_player().camera_step(-0.07, 0, level)
    if pg.key.get_pressed()[pg.K_RIGHT]:
        level.get_player().camera_step(0.07, 0, level)

    if jump > 0: # физика прыжка
        jump_height = 0.15 * jump
        level.get_player().step(0, -jump_height, level)
        jump -= jump_height
        if jump_height <= dt:
            jump = -1
    else:# физика падения
        time += dt
        if level.get_player().step(0, time, level) == -1:
            time = 0
    level.draw(screen)
    pg.display.flip()

pg.quit()
