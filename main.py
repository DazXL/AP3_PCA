import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path
import main

pygame.mixer.pre_init(44100, -16, 2, 512)  # configuração de audio
mixer.init()  # inicializa o mixer para sons
pygame.init()  # inicializa o pygame

clock = pygame.time.Clock()
fps = 60


# tamanho da tela
screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height)) # a tela
pygame.display.set_caption(f'Jogo da Matemática') # Título no topo da janela

# definir fonte
font = pygame.font.SysFont('Arial', 70)
font_score = pygame.font.SysFont('Arial', 30)  # (nome da fonte, tamanho da fonte)
font_text = pygame.font.SysFont('Arial', 14)

# define variaveis
tile_size = 50  # tamanho em pixel do tile
game_over = 0  # estado de game_over
main_menu = True  # menu principal ao iniciar o jogo
level = 8  # inicia na primeira fases
max_levels = 19  # máximo número de fases
score = 0  # pontuação inicial
level_score = 4  #pontuação do level

# define cores
white = (255, 255, 255)
blue = (0, 0, 255)

# carrega imagens
sun_img = pygame.image.load('img/sun.png')
bg_img = pygame.image.load('img/sky.png')
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')

# carrega sons
pygame.mixer.music.load('img/music.wav')  # carrega música de fundo
pygame.mixer.music.play(-1, 0.0, 5000)  # configura e toca a música
coin_sfx = pygame.mixer.Sound('img/coin.wav') # carrega o som
coin_sfx.set_volume(0.5)  # volume do som
jump_sfx = pygame.mixer.Sound('img/jump.wav')
jump_sfx.set_volume(0.5)
game_over_sfx = pygame.mixer.Sound('img/game_over.wav')
game_over_sfx.set_volume(0.5)

# desenha uma grade de tiles
'''def draw_grid():
	for line in range(0, 20):
		pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
		pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))'''


# desenha texto na tela

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# função para reiniciar o level
def reset_level(level):
    player.reset(100, screen_height - 130)
    blob_group.empty()
    lava_group.empty()
    exit_group.empty()
    coin_group.empty()
    platform_group.empty()
    main.score = 0

    # load level data and create world
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    # muda a pontuação necessária de acordo com a fase
    if level == 8:

        main.level_score = 4
    if level == 9:
        main.level_score = 7
    if level == 10:
        main.level_score = 6
    if level == 11:
        main.level_score = 1
    if level == 12:
        main.level_score = 2
    if level == 13:
        main.level_score = 3
    if level == 14:
        main.level_score = 10
    if level == 15:
        main.level_score = 9
    if level == 16:
        main.level_score = 6
    if level == 17:
        main.level_score = 1
    if level == 18:
        main.level_score = 3
    if level == 19:
        main.level_score = 2

    return world


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button
        screen.blit(self.image, self.rect)

        return action

class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        #variaveis delta
        dx = 0
        dy = 0
        walk_cooldown = 5
        col_thresh = 20

        if game_over == 0:
            # botões pressionados
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and  self.jumped == False and self.in_air == False:
                jump_sfx.play()
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False

            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]


            #animação do personagem

            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            #adiciona gravidade
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # check de colisão
            self.in_air = True
            for tile in world.tile_list:
                #colisão horizontal
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                #colisão na vertical
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #check se está pulando
                    if self.vel_y < 0:
                        dy  = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # check se está caindo
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # check colisão de inimigos
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
                game_over_sfx.play()

            # check colisão de lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_sfx.play()

            # check colisão de exit
            if pygame.sprite.spritecollide(self, exit_group, False) and score == level_score:
                game_over = 1

            #check de colisão com plataformas

            for platform in platform_group:
                # colisão na horizontal
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # colisão na vertical
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # check se embaixo da plataforma
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    # check se em cima da plataforma
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    # move junto com a plataforma
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction



            #atualização de posição do jogador

            self.rect.x += dx
            self.rect.y += dy

            '''if self.rect.bottom > screen_height:
                self.rect.bottom = screen_height
                dy = 0'''
        elif game_over == -1:
            self.image = self.dead_image
            draw_text('GAME OVER!', font, blue, (screen_width // 2) - 200, screen_height // 2)
            if self.rect.y > 200:
                self.rect.y -= 5

        #exibe personagem
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (255, 255, 255), self.rect, 2) #desenha retangulo para colisão

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f'img/guy{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('img/ghost.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True


class World():
    def __init__(self, data):
        self.tile_list = []

        # carrega tiles do mapa
        dirt_img = pygame.image.load('img/dirt.png')
        grass_img = pygame.image.load('img/grass.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                # desenha terra
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                # desenha grama
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                # desenha inimigos
                if tile == 3:
                    # + 15 para o inimigo ficar em cima do chão e não flutuando
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    blob_group.add(blob)
                if tile == 4:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 5:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                # desenha lava
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                if tile == 7:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                col_count += 1
            row_count += 1



    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            # desenha retangulos nos tiles do mapa
            # pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/blob.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/platform.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/coin.png')
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/exit.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y



'''world_data = [
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1],
[1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1],
[1, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1],
[1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1],
[1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1],
[1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
[1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
[1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]'''

player = Player(100, screen_height - 130)

blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# cria moeda ao lado do o contador
'''score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)'''

#load level data and create world
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)

# create buttons

restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)


# MAIN GAME LOOP
run = True
while run:
    clock.tick(fps)

    screen.blit(bg_img, (0, 0))
    screen.blit(sun_img, (100, 100))

    if main_menu == True:
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        # carrega a fase
        world.draw()
        # draw_text('FASE ' + str(level), font_score, white, tile_size + 825, 10)
        if game_over == 0:
            blob_group.update()
            platform_group.update()
            # update score
            #checa se pegou moedas
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
                coin_sfx.play()
            draw_text('MOEDAS = '+ str(score),font_score, white, tile_size - 10, 10)

        blob_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)

        game_over = player.update(game_over)
        # exibir os textos explicativos na tela
        if level == 8:
            draw_text('A adição é o ato de juntar elementos', font_text, blue, (screen_width // 2) - 140, screen_height // 2)
            draw_text('O símbolo usado é o +', font_text, blue, (screen_width // 2) - 140, (screen_height // 2) + 20)
            draw_text('Colete 2+2 moedas para avançar', font_text, blue, (screen_width // 2) - 140, (screen_height // 2) + 40)

        if level == 9:
            draw_text('Colete 4+3 moedas para avançar', font_text,
                      blue, (screen_width // 2) - 140, screen_height // 2)

        if level == 10:
            draw_text('Colete 1+5 moedas para avançar', font_text,
                      blue, (screen_width // 2) + 60, screen_height // 2)

        if level == 11:
            draw_text('Subtração é a operação inversa da adição', font_text, blue, (screen_width // 2) -140,
                      screen_height // 2)
            draw_text('é tirada uma quantidade de um número', font_text, blue, (screen_width // 2) - 140, (screen_height // 2) + 20)
            draw_text('O símbolo usado é o -', font_text, blue, (screen_width // 2) - 140, (screen_height // 2) + 40)
            draw_text('Colete 3-2 moedas para avançar', font_text, blue, (screen_width // 2) - 140,
                      (screen_height // 2) + 60)

        if level == 12:
            draw_text('Colete 5-3 moedas para avançar', font_text, blue, (screen_width // 2) - 140,
                      (screen_height // 2) + 40)

        if level == 13:
            draw_text('Colete 8-5 moedas para avançar', font_text, blue, (screen_width // 2) - 140,
                      (screen_height // 2) + 40)

        if level == 14:
            draw_text('Multiplicação é a adição sucessiva de um numero por ele mesmo', font_text, blue, (screen_width // 2) - 140,
                      (screen_height // 2) - 60)
            draw_text('O símbolo usado é o X', font_text, blue, (screen_width // 2) - 140, (screen_height // 2) - 40)
            draw_text('Colete 2 X 5 moedas para avançar', font_text, blue, (screen_width // 2) - 140,
                      (screen_height // 2) - 20)

        if level == 15:
            draw_text('Colete 3 X 3 moedas para avançar', font_text, blue, (screen_width // 2) - 140,
                      (screen_height // 2) + 40)

        if level == 16:
            draw_text('Colete 2 X 3 moedas para avançar', font_text, blue, (screen_width // 2) - 140,
                      (screen_height // 2) + 40)

        if level == 17:
            draw_text('Divisão é a operação inversa da multiplicação.', font_text, blue,
                      (screen_width // 2) - 140,
                      screen_height // 2)
            draw_text('É a fragmentação de um número', font_text, blue, (screen_width // 2) - 140, (screen_height // 2) + 20)
            draw_text('O símbolo usado é o ÷', font_text, blue, (screen_width // 2) - 140, (screen_height // 2) + 40)
            draw_text('Colete 10 ÷ 10 moedas para avançar', font_text, blue, (screen_width // 2) - 140,
                      (screen_height // 2) + 60)

        if level == 18:
            draw_text('Colete 6 ÷ 2 moedas para avançar', font_text, blue, (screen_width // 2) - 140,
                      (screen_height // 2) + 60)

        if level == 19:
            draw_text('Colete 8 ÷ 4 moedas para avançar', font_text, blue, (screen_width // 2) - 140,
                      (screen_height // 2) + 60)

        # quando jogador "morre"
        if game_over == -1:
            if restart_button.draw():
                # print("Reset") # debug do botão reset
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0
        # print(game_over) # debug de gameover

        # quando jogador finaliza a fase
        if game_over == 1:
            #reset game and go to next level
            level += 1
            if level <= max_levels:
                #reset level
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                # desenha texto de vitória
                draw_text('Parabéns, você venceu!', font, blue, (screen_width // 2) - 350, screen_height // 2)
                # restart the game
                if restart_button.draw():
                    level = 7

        #draw_grid()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
