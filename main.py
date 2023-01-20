import pygame as pg
import random
import time as Time
from datetime import datetime
import sqlite3

db_name = "data/DB/mario.db"
level_num = 1
tile_size = 50
FPS = 30  # frames per second
time_per_level = 150  # время, отведенное на прохождение уровня
saved_to_db = False  # флаг для однократного сохранения
user_text = ''
blink_counter = 6  # счетчик "миганий" сообщения о событии (т.ч. срабатывания события BLINK_EVENT)
text_to_blink = ""  # тест сообщения о событии в игре


# заставка
def start_screen(w, h, scrn, msc, clk):
    global user_text
    msc.load("data/sounds/start_track.mp3")
    msc.set_volume(0.5)
    msc.play(0)
    active = False
    text_w = 260  # ширина поля ввода по умолчанию. если длины не хватит, расширяем
    # поле ввода имени - зеленый прямоугольник
    input_rect = pg.Rect(230, 3 * h / 4 - 230, text_w, 50)
    color_user_label = (255, 255, 255)
    fon = pg.transform.scale(pg.image.load('data/img/start.png'), (w, h))
    scrn.blit(fon, (0, 0))
    mouse = pg.mouse.get_pos()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:  # закрыли игру во время заставки
                exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                # кликнули над кнопкой QUIT (по координатам)
                if 80 <= mouse[0] <= 80 + 200 and 3 * h / 4 - 85 + 5 <= mouse[1] <= 3 * h / 4 - 85 + 5 + 50:
                    exit()
                # кликнули над кнопкой START
                elif 80 <= mouse[0] <= 80 + 200 and 3 * h / 4 - 165 + 5 <= mouse[1] <= 3 * h / 4 - 165 + 5 + 50:
                    if user_text == '':  # пyстое имя нельзя
                        color_user_label = (255, 0, 0)
                        break
                    return  # начинаем игру
                else:
                    # кликнули над полем ввода имени
                    if 230 <= mouse[0] <= 230 + text_w and 3 * h / 4 - 230 <= mouse[1] <= 3 * h / 4 - 230 + 50:
                        active = True
                    else:
                        active = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_BACKSPACE:
                    user_text = user_text[:-1]  # убрать последний символ
                elif event.key == pg.K_RETURN:  # enter = кнопка START
                    if user_text == '':  # пyстое имя нельзя
                        color_user_label = (255, 0, 0)
                        break
                    return  # начинаем игру
                else:
                    # длина имени - не больше 18 символов, используем Unicode
                    if len(user_text) <= 18:
                        user_text += event.unicode

        btn_font = pg.font.SysFont('Super Mario 128', 50)
        color_font = (255, 255, 255)
        color_btn = (0, 177, 32)
        color_btn1 = (127, 127, 127)
        # отрисуем две кнопки quit и start ("двойной" прямойгольник с тенью)
        text_quit = btn_font.render('Q U I T', True, color_font)
        text_start = btn_font.render('S T A R T', True, color_font)
        pg.draw.rect(scrn, color_btn1, [85, 3 * h / 4 - 165 + 5, 200, 50])
        pg.draw.rect(scrn, color_btn, [80, 3 * h / 4 - 165, 200, 50])
        pg.draw.rect(scrn, color_btn1, [85, 3 * h / 4 - 85, 200, 50])
        pg.draw.rect(scrn, color_btn, [80, 3 * h / 4 - 85, 200, 50])

        scrn.blit(text_start, (100, 3 * h / 4 - 155))
        scrn.blit(text_quit, (120, 3 * h / 4 - 75))

        # для поля ввода имени
        color_active = pg.Color(190, 255, 190)
        color_passive = pg.Color(0, 177, 32)
        enter_name = btn_font.render('Your name:', True, color_user_label)
        scrn.blit(enter_name, (30, 3 * h / 4 - 225))
        if active:
            color = color_active
        else:
            color = color_passive
        pg.draw.rect(scrn, color, input_rect)
        text_surface = btn_font.render(user_text, True, (0, 0, 0))
        scrn.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))

        input_rect.w = max(260, text_surface.get_width() + 10)
        text_w = input_rect.w

        mouse = pg.mouse.get_pos()
        pg.display.flip()
        clk.tick(FPS)


def is_negative(num):
    if num < 0:
        return -1
    elif num > 0:
        return 1
    else:
        return 0


def end_world(world_name=''):  # завершение уровня и подготовка к началу следующего
    global level, level_num, ftime, timer
    level_num += 1

    if level_num > 3:
        end_game()
    else:
        level.__del__()

        if Player.deaths <= 3:
            Player.levels_score += Player.score + Player.all_score + (Player.hp - Player.deaths) * 100 + \
                                   ((time_per_level - timer) * 2)
        else:
            Player.levels_score += Player.score + Player.all_score + ((time_per_level - timer) * 2)

        Player.score = 0
        Player.hp += 1
        Player.all_score = 0
        Player.all_time += time_per_level - timer
        Player.deaths = 0

        music.load("data/sounds/win_track.mp3")
        music.set_volume(0.5)
        music.play(1)

        Time.sleep(6.5)
        clock.tick()

        ftime = pg.time.get_ticks()
        timer = time_per_level

        music.load("data/sounds/main_track.mp3")
        music.set_volume(0.5)
        music.play(-1)

        if world_name != '':
            level = Level(world_name)
        else:
            level = Level(f'data/levels/{level_num}_lvl.txt')


def end_game():
    global running, is_end
    is_end = True
    now = pg.time.get_ticks()
    if (pg.time.get_ticks() - now) / 1000 >= 30:
        running = False
    print('end')


class Tile(pg.sprite.Sprite):  # класс стен и препятствий
    images = {
        'wall': pg.image.load('data/img/box.png'),
        'brick': pg.image.load('data/img/brick.png'),
        'spike': pg.image.load('data/img/spike_grass.png'),
        'empty': pg.image.load('data/img/grass.png'),
        'end': pg.image.load('data/img/door.png'),
        'open_door': pg.image.load('data/img/open_door.png'),
        'question': pg.image.load('data/img/question.png')
    }
    size = tile_size

    def __init__(self, tile_type, tile_pos, *groups, in_pixels=0):
        super().__init__(*groups)
        self.image = Tile.images[tile_type]
        if in_pixels:
            self.rect = self.image.get_rect().move(tile_pos[0], tile_pos[1])
        else:
            self.rect = self.image.get_rect().move(tile_pos[0] * Tile.size, tile_pos[1] * Tile.size)
        self.type = tile_type

    def step_camera(self, dx, dy):  # метод перемещения для работы перемещения камеры
        self.rect = self.rect.move(-1 * dx, -1 * dy)
        self.rect = self.image.get_rect().move(self.rect.x,
                                               self.rect.y)

    def get_pos(self):  # номер плитки по горизонтали и вертикали
        return self.rect.x // tile_size, self.rect.y // tile_size


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
                        elif sym == 'b':
                            Tile('empty', (x, y), self.tile_group)
                            Tile('brick', (x, y), self.tile_group)
                        elif sym == '>':
                            Tile('spike', (x, y), self.tile_group)
                        elif sym == 'w':
                            Tile('empty', (x, y), self.tile_group)
                            Tile('end', (x, y), self.tile_group)
                        elif sym == 'q':
                            Tile('empty', (x, y), self.tile_group)
                            Tile('question', (x, y), self.tile_group)
                        elif sym == 'u':
                            Tile('empty', (x, y), self.tile_group)
                            Player((x * Tile.size, y * Tile.size), self.player_group)
                        elif sym == 'e':
                            Tile('empty', (x, y), self.tile_group)
                            Enemy((x * Tile.size, y * Tile.size), self.enemy_group,
                                  speed=random.randint(100, 300) // 100, diff_level=1)
                        elif sym == 'E':
                            Tile('empty', (x, y), self.tile_group)
                            Enemy((x * Tile.size, y * Tile.size), self.enemy_group,
                                  speed=random.randint(300, 500) // 100, diff_level=2)
        except BaseException:
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

    def add_tile(self, x, y, tile_type):  # добавить тайл на указанную позицию
        Tile(tile_type, (x, y), self.tile_group, in_pixels=1)


class Entity(pg.sprite.Sprite):  # базовый класс движущихся сущностей
    def __init__(self, pos, image, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect().move(pos)
        self.time = 0

    def step(self, dx, dy, level):  # метод перемещения сущности
        global blink_counter, BLINK_EVENT, text_to_blink
        self.rect = self.rect.move(dx, dy)

        for tile in pg.sprite.spritecollide(self, level.get_tiles(), False):
            if tile.type == 'wall' or tile.type == 'brick' or tile.type == 'question':
                # в случае если перемещение происходит на препятствие,
                # сущность перемещается на последний пиксель перед ним

                if dy:
                    if dy < 0:
                        self.rect = self.image.get_rect().move(self.rect.x, tile.rect.y + Tile.size)
                        if tile.rect.x < self.rect.x + self.rect.width and self.time * 50 < self.jump_speed * dt:
                            if tile.type == 'brick':
                                tile.kill()
                                level.get_player().jump_speed = 0
                                level.get_player().time = 0
                            elif tile.type == 'question':
                                tile.kill()
                                level.get_player().jump_speed = 0
                                level.get_player().time = 0
                                rnd_val = random.randint(0, 9)
                                if rnd_val == 0:  # добавить жизнь
                                    plus_hp()
                                    text_to_blink = "hp+1"
                                    blink_counter = 6  # счетчик миганий начать сначала
                                    BLINK_EVENT = pg.USEREVENT + 0  # "включить" событие о событии для мигания
                                elif rnd_val in (1, 2):  # убрать жизнь
                                    minus_hp(False, 3)
                                    text_to_blink = "hp-1"
                                    blink_counter = 6  # счетчик миганий начать сначала
                                    BLINK_EVENT = pg.USEREVENT + 0  # "включить" событие о событии для мигания
                                elif rnd_val in (0, 1, 2):  # превратить в кирпич
                                    level.add_tile(tile.rect.x, tile.rect.y, 'brick')
                                    tile.kill()
                                    print(1)
                                elif rnd_val in (6, 7):  # превратить в стену
                                    level.add_tile(tile.rect.x, tile.rect.y, 'wall')
                                elif rnd_val == 6:  # добавить очки
                                    plus_xp()
                                    text_to_blink = "points+50"
                                    blink_counter = 6
                                    BLINK_EVENT = pg.USEREVENT + 0
                                elif rnd_val == 7:  # добавить время
                                    plus_time()
                                    text_to_blink = "time+5"
                                    blink_counter = 6
                                    BLINK_EVENT = pg.USEREVENT + 0
                                else:
                                    text_to_blink = "empty box"
                                    blink_counter = 6
                                    BLINK_EVENT = pg.USEREVENT + 0
                            return -1
                        else:
                            return

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


now = 100


def plus_hp():  # увеличить количество жизней на 1
    Player.hp += 1


def plus_xp():  # добавляет 50 очков к сумме
    Player.score += 50

    if Player.score >= 100:
        Player.score -= 100
        Player.hp += 1


def plus_time():  # увеличить время на уровень на 5 секунд
    global timer, is_other_music
    timer += 5
    if timer > 60 and is_other_music:
        music.load("data/sounds/main_track.mp3")
        music.play(-1)
        is_other_music = False


def minus_hp(hit=False, enemy_type=1):  # уменьшить количество жизней на 1
    global now

    if enemy_type == 1:  # из-за гриба
        print(-1)
        Player.hp -= 1
    elif enemy_type == 2 and not hit:  # из-за дракона
        Player.hp -= 1
        print(-1.2)
        now = pg.time.get_ticks()
    elif enemy_type == 3:  # из-за коробки с вопросом
        Player.hp -= 1
    # Player.image = pg.image.load('data/img/hit_mar.png')
    # Enemy.is_hit = True
    # Enemy.start = pg.time.get_ticks()

    # смерть - жизни кончились
    if Player.hp == 0:
        print('no more lives')
        Player.is_died = True
        Player.deaths += 1

        music.load("data/sounds/death_sound.mp3")
        music.set_volume(0.5)
        music.play(1)


class Player(Entity):  # класс игрока

    image = pg.image.load('data/img/mar.png')
    hp = 3
    score = 0
    all_score = 0
    all_time = 0
    levels_score = 0
    deaths = 0
    is_died = False
    name = user_text
    x = 0

    def __init__(self, pos, *groups):
        super().__init__(pos, Player.image, *groups)
        self.can_jump = 0
        self.jump_speed = 0
        self.jump_time = 0
        self.x = pos[0]

    def camera_step(self, dx, dy, level):  # метод перемещения камеры
        self.rect = self.rect.move(dx, dy)
        flag = 1

        for tile in pg.sprite.spritecollide(self, level.get_tiles(), False):
            if tile.type == 'wall' or tile.type == 'brick' or tile.type == 'question':
                flag = 0

            if tile.type == 'end':
                tile.image = Tile.images['open_door']
                level.draw(screen)
                pg.display.flip()

                music.load("data/sounds/win_track.mp3")
                music.set_volume(0.5)
                music.play(1)

                end_world()

        self.rect = self.rect.move(-1 * dx, -1 * dy)

        if flag:
            for tile in level.get_tiles():
                tile.step_camera(dx, dy)
            for tile in level.get_enemys():
                tile.step_camera(dx, dy)

    def get_info(self):
        return 'player', (self.rect.x, self.rect.y)

    def physic(self, delta_t):
        if level.get_player().step(0, -self.jump_speed * delta_t, level) == -1:
            self.jump_speed = 0
            self.time = 0
        if self.step(0, self.time * 50, level) == -1:
            level.get_player().step(0, self.jump_speed * (delta_t + 0.001), level)
            self.time = 0
            self.jump_speed = 0
            self.can_jump = 2
        else:
            self.time += delta_t
        for tile in pg.sprite.spritecollide(self, level.get_tiles(), False):
            if tile.type == 'end':
                tile.image = Tile.images['open_door']
                level.draw(screen)
                pg.display.flip()
                end_world()

            if tile.type == 'spike' and level.get_player().rect.bottom >= tile.rect.center[1]:
                minus_hp(True if (pg.time.get_ticks() - now) / 1000 <= 2 else False, 2)

    def jump(self, h):
        if self.can_jump > 0:
            self.jump_speed = h ** 0.5 * Tile.size
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
    count = 0

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
            if not (level.get_tile((self.rect.x // tile_size - 1, self.rect.y // tile_size)).type == 'wall' and
                    level.get_tile((self.rect.x // tile_size + 1, self.rect.y // tile_size)).type == 'wall'):
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

                self.kill()

            elif self.can_die:
                minus_hp()
                self.kill()

            else:
                Enemy.count += 1
                if Enemy.count == 1:
                    minus_hp(False, 2)
                else:
                    # когда стоит неподвижно, то урон не наносится. Не баг, а фича
                    minus_hp(True if 0 < (pg.time.get_ticks() - now) / 1000 <= 1.5 else False, 2)
            return

    def step_camera(self, dx, dy):  # метод перемещения для работы перемещения камеры
        self.rect = self.rect.move(-1 * dx, -1 * dy)

    def get_info(self):
        return 'enemy', (self.rect.x, self.rect.y)


# сохранение результатов и получение top-5 лучших игроков
def SaveResult(scrn):
    global save_to_db
    res = []
    res.append(['N', 'Имя игрока', 'Результат'])
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = '''
                        insert into players (NAME, PLAY_TIME, GAME_RESULT) 
                        values (?,?,?)    
                         '''
    cur.execute(query, (Player.name, datetime.now(), Player.all_score))
    con.commit()
    cur.close()
    cur = con.cursor()
    query = '''
                SELECT NAME, GAME_RESULT FROM players order by  game_result desc limit 5
            '''
    tmp = cur.execute(query).fetchall()
    for i, row in enumerate(tmp):
        res.append([i + 1] + list(row))
    cur.close()
    save_to_db = False
    return res


level_path = f'data/levels/{level_num}_lvl.txt'
level = Level(level_path)
top5 = []
BLINK_EVENT = pg.USEREVENT + 0
empty = (255, 255, 255, 0)
pg.init()

# ftime = pg.time.get_ticks()
timer = time_per_level
clock = pg.time.Clock()

music = pg.mixer.music
size = width, height = 1000, 700
screen = pg.display.set_mode(size)
start_screen(width, height, screen, music, clock)
Player.name = user_text
ftime = pg.time.get_ticks()

music.load("data/sounds/main_track.mp3")
music.play(-1)
music.set_volume(0.5)

is_other_music = False
tooMuch_time = False
is_end = False
blink_font = pg.font.SysFont('Super Mario 128', 30, italic=True)
blink_surface = blink_font.render(text_to_blink, True, (255, 242, 0), (0, 0, 0))
blink_rect = blink_surface.get_rect(center=(300, 670))
font = pg.font.SysFont('Super Mario 128', 50)

running = True
jump = 0
time = 0
pg.time.set_timer(BLINK_EVENT, 500)
while running:
    screen.fill('black')
    dt = clock.tick(FPS) / 1000

    if is_end:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        congrat_label = font.render(f"The End!", False, (255, 255, 255), (0, 0, 0))
        score_label = font.render(f"Score: {Player.levels_score}", True, (255, 255, 255), (0, 0, 0))
        alltime_label = font.render(f"Time:  0{Player.all_time // 60}:{Player.all_time % 60}",
                                    False, (255, 255, 255),
                                    (0, 0, 0))
        # сохраняю в БД имя игрока, дату игры и результат
        if not saved_to_db:
            top5 = SaveResult(screen)
            saved_to_db = True

        screen.blit(congrat_label, (422, 80))
        screen.blit(score_label, (415, 130))
        screen.blit(alltime_label, (400, 175))

        FontBig = pg.font.SysFont('Super Mario 128', 50)
        FontSmall = pg.font.SysFont('Super Mario 128', 25)
        pg.draw.rect(screen, (0, 80, 15), [20, 300, 950, 375])
        pg.draw.rect(screen, (0, 0, 0), [25, 305, 940, 365])
        TOP5_label = FontBig.render("TOP 5 BEST RESULTS", False, (0, 177, 32))
        screen.blit(TOP5_label, (300, 320))

        for i, row in enumerate(top5):
            lab = FontSmall.render(str(row[0]), False, (255, 255, 255))
            screen.blit(lab, (50, 320 + (i + 1) * 50))
            lab = FontSmall.render(str(row[1]), False, (255, 255, 255))
            screen.blit(lab, (150, 320 + (i + 1) * 50))
            lab = FontSmall.render(str(row[2]), False, (255, 255, 255))
            if i == 0:
                screen.blit(lab, (520, 320 + (i + 1) * 50))
                pg.draw.rect(screen, (255, 255, 255), [50, 320 + 70, 890, 3])
            else:
                screen.blit(lab, (550, 320 + (i + 1) * 50))

    else:
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
                    if event.key == pg.K_w or event.key == pg.K_UP or event.key == pg.K_SPACE:  # прыжок
                        level.get_player().jump(135)
                if event.type == BLINK_EVENT:
                    if blink_counter % 2 == 0:  # на четный счет создаем тест
                        blink_surface = blink_font.render(text_to_blink, True, (255, 242, 0), (0, 0, 0))
                    else:  # на нечетный счет удаляем его
                        del blink_surface
                    blink_counter -= 1
                    if blink_counter == 0:  # если счетчик миганий "кончится", выключить событие
                        BLINK_EVENT = 0
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
            # если "мигания не кончились и счет четный, отобразить сообщение о событии
            if blink_counter > 0 and blink_counter % 2 == 0:
                blink_surface = blink_font.render(text_to_blink, True, (255, 242, 0), (0, 0, 0))
                screen.blit(blink_surface, blink_rect)
        else:
            # сохраняю в БД имя игрока, дату игры и результат
            if not saved_to_db:
                top5 = SaveResult(screen)
                saved_to_db = True  # подняли флаг, чтобы избежать повторного сохранения

            game_over = font.render(f"Game over!", False, (255, 255, 255), (0, 0, 0))
            final_score = font.render(f"Your score: {Player.all_score}", True, (255, 255, 255), (0, 0, 0))
            if not tooMuch_time:
                time_table = font.render(f"Time: {time_per_level - timer}", True, (255, 255, 255), (0, 0, 0))
                screen.blit(time_table, (440, 225))
            else:
                time_table = font.render(f"Time: Too Much!", True, (255, 150, 150), (0, 0, 0))
                screen.blit(time_table, (370, 225))
            advice = font.render(f"Press any button to continue", True, (255, 255, 255), (0, 0, 0))

            screen.blit(game_over, (405, 80))  # (405, 250)
            screen.blit(final_score, (385, 130))  # (385, 300)
            screen.blit(advice, (267, 175))  # (267, 425)

            FontBig = pg.font.SysFont('Super Mario 128', 50)
            FontSmall = pg.font.SysFont('Super Mario 128', 25)
            pg.draw.rect(screen, (0, 80, 15), [20, 300, 950, 375])
            pg.draw.rect(screen, (0, 0, 0), [25, 305, 940, 365])
            TOP5_label = FontBig.render("TOP 5 BEST RESULTS", False, (0, 177, 32))
            screen.blit(TOP5_label, (300, 320))

            for i, row in enumerate(top5):
                lab = FontSmall.render(str(row[0]), False, (255, 255, 255))
                screen.blit(lab, (50, 320 + (i + 1) * 50))
                lab = FontSmall.render(str(row[1]), False, (255, 255, 255))
                screen.blit(lab, (150, 320 + (i + 1) * 50))
                lab = FontSmall.render(str(row[2]), False, (255, 255, 255))
                if i == 0:
                    screen.blit(lab, (520, 320 + (i + 1) * 50))
                    pg.draw.rect(screen, (255, 255, 255), [50, 320 + 70, 890, 3])
                else:
                    screen.blit(lab, (550, 320 + (i + 1) * 50))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.KEYDOWN or event.type == pg.MOUSEBUTTONDOWN:
                    Player.is_died = False
                    tooMuch_time = False
                    Player.hp = 3
                    Player.score = 0
                    Player.all_score = 0
                    level_path = f'data/levels/{level_num}_lvl.txt'
                    level = Level(level_path)

                    timer = time_per_level
                    ftime = pg.time.get_ticks()

                    music.load("data/sounds/main_track.mp3")
                    music.play(-1)

    pg.display.flip()

pg.quit()
