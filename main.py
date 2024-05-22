import pygame as pg
import pygame_menu
from random import randint, choice
import json
import io

pg.init()
pg.mixer.init()

class U:
    font = pg.font.Font(None, 50)
    score = 0
    difficulty = 0
    volume = 0.3

    @classmethod
    def init(cls):
        U.data = cls.load_data()

    @classmethod
    def save_data(cls):
        cls.save_best()
        with open('data.json', 'w') as file:
            file.write(json.dumps(U.data, ensure_ascii=False, indent=4))

    @classmethod
    def load_data(cls):
        with open('data.json', 'r') as file:
            data = json.loads(file.read())
        return data
    
    @classmethod
    def blit_text(cls, screen, text, x, y, font=font, color='black', bg=None):
        image = font.render(str(text), True, color, bg)
        screen.blit(image, image.get_rect(center=(x, y)))

    @classmethod
    def save_best(cls):
        if U.difficulty == 0:
            if U.data['best_easy'] < U.score:
                U.data['best_easy'] = U.score
            U.best = U.data['best_easy']
        elif U.difficulty == 1:
            if U.data['best_medium'] < U.score:
                U.data['best_medium'] = U.score
            U.best = U.data['best_medium']
        if U.difficulty == 2:
            if U.data['best_hard'] < U.score:
                U.data['best_hard'] = U.score
            U.best = U.data['best_hard']

U.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

# КЛАСС МЕНЮ
class Menu:
    def __init__(self):
        self.surface = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.menu = pygame_menu.Menu(
            height = SCREEN_HEIGHT,
            width = SCREEN_WIDTH,
            theme = pygame_menu.themes.THEME_SOLARIZED,
            title = 'Flappy Bird'
        )

        self.statistics_menu = pygame_menu.Menu(
            height = SCREEN_HEIGHT,
            width = SCREEN_WIDTH,
            theme = pygame_menu.themes.THEME_SOLARIZED,
            title = 'Статистика'
        )

        self.statistics_menu.add.label('Рекорды')
        self.statistics_menu.add.label(f'Лёгкий: {U.data["best_easy"]}')
        self.statistics_menu.add.label(f'Обычный: {U.data["best_medium"]}')
        self.statistics_menu.add.label(f'Сложный: {U.data["best_hard"]}')
        self.statistics_menu.add.button('Назад', lambda: self.menu.mainloop(self.surface))

        self.difficulty = 1
        self.skin = 0
        self.background = 0

        self.menu.add.button('Играть', self.play)
        self.menu.add.selector('Сложность ', [('Обычная', 1), ('Лёгкая', 0), ('Сложная', 2)], onchange=self.set_difficulty)
        self.menu.add.selector('Громкость звуков ', [('3', 0.3), ('4', 0.5), ('5', 1), ('0', 0), ('1', 0.05), ('2', 0.1)], onchange=self.set_volume)
        self.menu.add.selector('Скин птицы ', [('Жёлтый', 0), ('Чёрный', 1), ('Зелёный', 2), ('Красный', 3), ('Розовый', 4), ('Синий', 5)], onchange=self.set_skin)
        self.menu.add.selector('Фон ', [('Дневной', 0), ('Ночной', 1)], onchange=self.set_background)
        self.menu.add.button('Статистика', self.statistics)
        self.menu.add.button('Выйти', exit)

        self.menu.mainloop(self.surface)

    def play(self):
        U.difficulty = self.difficulty
        Game(self.difficulty, self.skin, self.background)

    def set_difficulty(self, selected, value):
        self.difficulty = value

    def set_volume(self, selected, value):
        U.volume = value
    
    def set_skin(self, selected, value):
        self.skin = value

    def set_background(self, selected, value):
        self.background = value
    
    def statistics(self):
        self.statistics_menu.mainloop(self.surface)

# КЛАСС ПТИЦЫ
class Bird(pg.sprite.Sprite):
    def __init__(self, x, y, skin):
        # активация класса спрайта
        super().__init__()
        # параметры
        self.is_alive = True
        self.skin = skin
        # загрузка анимаций
        self.load_animations()
        self.image = self.animation[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.current_image = 0
        self.timer = pg.time.get_ticks()
        self.interval = 200
        # скорость и гравитация
        self.velocity = 0
        self.gravity = 0.4
        # звуки
        self.jump_sound = pg.mixer.Sound('sounds/sfx_wing.wav') # звук прыжка
        self.jump_sound.set_volume(U.volume)
        self.die_sound = pg.mixer.Sound('sounds/sfx_die.wav') # звук смерти
        self.die_sound.set_volume(U.volume)

    def load_animations(self):
        self.animation = []
        num_images = 3
        spritesheet = pg.image.load(f'images/bird_spritesheet_{self.skin+1}.png')
        width = 92
        height = 64

        for i in range(num_images):
            x = i * width
            y = 0
            rect = pg.Rect(x, y, width, height)
            image = pg.transform.scale(spritesheet.subsurface(rect), (46, 32))
            self.animation.append(image)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        if self.velocity <= 0:
            self.image = pg.transform.rotate(self.animation[self.current_image], 45)
        else:
            self.image = pg.transform.rotate(self.animation[self.current_image], -self.velocity * 5)
        self.velocity += self.gravity

        self.rect.y += self.velocity

        if self.rect.bottom > SCREEN_HEIGHT-100:
            self.die_sound.play()
            self.is_alive = False
            U.save_data()

        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1
            if self.current_image >= len(self.animation):
                self.current_image = 0
            self.image = self.animation[self.current_image]
            if self.velocity <= 0:
                self.image = pg.transform.rotate(self.animation[self.current_image], 45)
            else:
                self.image = pg.transform.rotate(self.animation[self.current_image], -self.velocity * 5)
            self.timer = pg.time.get_ticks()

    def jump(self):
        if self.is_alive:
            self.velocity = -7
            self.jump_sound.play()

# КЛАСС ТРУБЫ   
class Pipe(pg.sprite.Sprite):
    def __init__(self, x, y, length, side):
        super().__init__()
        self.image_top = pg.transform.scale(pg.image.load('images/pipe_top.png'), (100, 40)) if side == 'down' else pg.transform.flip(pg.transform.scale(pg.image.load('images/pipe_top.png'), (100, 40)), False, True)
        self.image_bottom = pg.image.load('images/pipe_bottom.png')
        self.image_bottom = pg.transform.scale(self.image_bottom, (60, length))
        self.side = side
        if side == 'down':
            self.bottom_rect = self.image_bottom.get_rect(bottomleft=(x, y+3))
            self.top_rect = self.image_top.get_rect(topleft=(x-20, self.bottom_rect.top-38))
        elif side == 'up':
            self.bottom_rect = self.image_bottom.get_rect(topleft=(x, y))
            self.top_rect = self.image_top.get_rect(topleft=(x-20, self.bottom_rect.bottom-2))

    def update(self, bird):
        self.top_rect.x -= 5
        self.bottom_rect.x -= 5

        if bird.rect.colliderect(self.top_rect) or bird.rect.colliderect(self.bottom_rect):
            bird.die_sound.play()
            bird.is_alive = False
            U.save_data()

    def draw(self, screen):
        screen.blit(self.image_bottom, self.bottom_rect)
        screen.blit(self.image_top, self.top_rect)

class Game:
    def __init__(self, difficulty, skin, background):
        self.clock = pg.time.Clock()
        # Создание окна
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Flappy Bird")
        # параметры
        self.gap = (250, 200, 175)[difficulty]       # промежуток между трубами
        self.skin = skin
        self.background_num = background
        # загрузка игры
        self.setup()

    def setup(self):
        # фон
        self.background = pg.transform.scale(pg.image.load(f'images/background_{self.background_num+1}.png'), (SCREEN_WIDTH, SCREEN_HEIGHT))
        # птица
        self.bird = Bird(100, 250, self.skin)
        self.score_positions = []
        U.score = 0
        # параметры
        self.start = False
        self.start_timer = pg.time.get_ticks()
        self.seconds = 3
        # трубы
        self.pipes = pg.sprite.Group()
        self.timer = pg.time.get_ticks() # таймер
        self.interval = 1000             # задержка 
        down = randint(100, 350)          # высота нижней трубы
        up = abs(SCREEN_HEIGHT - down - self.gap)    # выстота верхней трубы
        self.pipes.add(Pipe(SCREEN_WIDTH, SCREEN_HEIGHT, down, 'down')) # добавление трубы в список
        self.pipes.add(Pipe(SCREEN_WIDTH, 0, up, 'up'))                 # добавление трубы в список
        self.score_positions.append(SCREEN_WIDTH)
        # камера
        self.camera_x = 0
        self.camera_y = 0
        # запуск цикла
        self.is_running = True
        self.run()

    def run(self):
        while self.is_running:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.start:
                    if event.button == 1:
                        self.bird.jump()
                        if not self.bird.is_alive:
                            self.setup()
                elif event.button == 1:
                    self.start = True
                    self.timer = pg.time.get_ticks()

            if event.type == pg.KEYDOWN:
                if self.start:
                    if event.key == pg.K_SPACE:
                        self.bird.jump()
                else:
                    self.start = True
                    self.timer = pg.time.get_ticks()
                if event.key == pg.K_ESCAPE:
                    Menu()
                if not self.bird.is_alive:
                    self.setup()

    def update(self):
        if self.bird.is_alive:
            if self.start:
                self.bird.update()

                if self.bird.rect.y < 0 and self.bird.rect.x >= self.score_positions[0]-55:
                    self.bird.is_alive = False
                    self.bird.die_sound.play()
                    U.save_data()

                if self.bird.rect.x > self.score_positions[0]:
                    U.score += 1
                    del self.score_positions[0]

                for pipe in self.pipes:
                    if pipe.top_rect.right < 0:
                        self.pipes.remove(pipe)
                    pipe.update(self.bird)

                self.score_positions = [score_pos - 5 for score_pos in self.score_positions]

                self.camera_x -= 1
                if -self.camera_x > SCREEN_WIDTH:
                    self.camera_x = 0
                if pg.time.get_ticks() - self.timer > self.interval:
                    down = randint(100, 350)          # высота нижней трубы
                    up = abs(SCREEN_HEIGHT - down - self.gap) # высота верхней трубы
                    self.pipes.add(Pipe(SCREEN_WIDTH, SCREEN_HEIGHT, down, 'down'))
                    self.pipes.add(Pipe(SCREEN_WIDTH, 0, up, 'up'))
                    self.timer = pg.time.get_ticks()
                    self.score_positions.append(SCREEN_WIDTH)
        else:
            if not self.bird.rect.y > SCREEN_HEIGHT-100:
                self.bird.rect.y += 7

    def draw(self):
        self.screen.blit(self.background, (self.camera_x, 0))
        self.screen.blit(self.background, (SCREEN_WIDTH+self.camera_x, 0))

        self.bird.draw(self.screen)
        
        for pipe in self.pipes:
            pipe.draw(self.screen)

        if not self.start:
            U.blit_text(self.screen, str(self.seconds), SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
            U.blit_text(self.screen, 'ПРИГОТОВЬТЕСЬ!', SCREEN_WIDTH/2, SCREEN_HEIGHT/2+100)
            U.blit_text(self.screen, 'нажмите любую клавишу, чтобы пропустить', SCREEN_WIDTH/2, SCREEN_HEIGHT/2+150)
            if pg.time.get_ticks() - self.start_timer >= 1000:
                self.seconds -= 1
                self.start_timer = pg.time.get_ticks()
            if self.seconds == 0:
                self.start = True
                self.timer = pg.time.get_ticks()

        if not self.bird.is_alive:
            U.blit_text(self.screen, 'игра окончена', SCREEN_WIDTH/2, SCREEN_HEIGHT/2, color='red')
            U.blit_text(self.screen, 'нажмите любую клавишу, чтобы начать сначала', SCREEN_WIDTH/2, SCREEN_HEIGHT/2+50)
            U.blit_text(self.screen, f'ВАШ СЧЁТ: {U.score}', SCREEN_WIDTH/2, SCREEN_HEIGHT/2+100)
            U.blit_text(self.screen, f'ВАШ РЕКОРД: {U.best}', SCREEN_WIDTH/2, SCREEN_HEIGHT/2+150)

        U.blit_text(self.screen, U.score, 50, 15)
        U.blit_text(self.screen, f"сложность: {('ЛЁГКАЯ', 'ОБЫЧНАЯ', 'СЛОЖНАЯ')[U.difficulty]}", 350, 15)

        pg.display.flip()


if __name__ == "__main__":
    Menu()