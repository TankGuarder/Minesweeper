import sys
import time
import numpy as np
from scipy.ndimage import convolve
import pygame
from pygame.locals import *

class Minesweeper:
    def __init__(self):
        self.W = 600
        self.H = 400
        self.grid = 25
        self.mine_num = 25

        self.cell_width = self.grid - 2
        self.H_step = self.H // self.grid
        self.W_step = self.W // self.grid

        self.fail = False
        self.win = False
        self.begin = False
        self.middle_click = False

        self.total_time = 0

        self.matrix_init()

        pygame.init()
        pygame.font.init()
        self.Surface = pygame.display.set_mode((self.W + self.W // 2, self.H))
        self.Font = pygame.font.Font('./DATA/ARLRDBD.TTF', 20)
        self.TEXT = PygameText(self)
        self.IMAGE = PygameImage(self)
        return

    def matrix_init(self):
        self.define_matrix_mine()
        self.define_matrix_clicked()
        self.define_matrix_count()
        self.define_matrix_flag()
        return

    def define_matrix_mine(self):
        self.matrix_mine = np.zeros((self.H_step, self.W_step))
        random_indices = np.random.choice(np.arange(self.H_step * self.W_step), size=self.mine_num, replace=False)
        self.matrix_mine[np.unravel_index(random_indices, self.matrix_mine.shape)] = 1
        '''
        mine_put = 0
        while mine_put < self.mine_num:
            ind = np.random.randint(self.H_step), np.random.randint(self.W_step)
            if self.matrix_mine[ind] != 1:
                self.matrix_mine[ind] = 1
                mine_put += 1
        '''
        return

    def define_matrix_clicked(self):
        self.matrix_clicked = np.zeros((self.H_step, self.W_step))
        return

    def define_matrix_count(self):
        kernel = np.array([[1, 1, 1],
                           [1, 0, 1],
                           [1, 1, 1]])
    
        # Use convolution to sum the neighboring cells
        self.matrix_count = convolve(self.matrix_mine, kernel, mode='constant', cval=0)
        '''
        self.matrix_count = self.mine \
                          + np.concatenate([np.zeros([self.H_step, 1]), self.mine[:, :-1]], axis=1) \
                          + np.concatenate([self.mine[:, 1:], np.zeros([self.H_step, 1])], axis=1) \
                          + np.concatenate([np.zeros([1, self.W_step]), self.mine[:-1, :]], axis=0) \
                          + np.concatenate([self.mine[1:, :], np.zeros([1, self.W_step])], axis=0) \
                          + np.concatenate([np.zeros([1, self.W_step]), np.concatenate([np.zeros([self.H_step - 1, 1]), self.mine[:-1, :-1]], axis=1)], axis=0) \
                          + np.concatenate([np.concatenate([self.mine[1:, 1:], np.zeros([self.H_step - 1, 1])], axis=1), np.zeros([1, self.W_step])], axis=0) \
                          + np.concatenate([np.zeros([1, self.W_step]), np.concatenate([self.mine[:-1, 1:], np.zeros([self.H_step - 1, 1])], axis=1)], axis=0) \
                          + np.concatenate([np.concatenate([np.zeros([self.H_step - 1, 1]), self.mine[1:, :-1]], axis=1), np.zeros([1, self.W_step])], axis=0)
        '''
        return

    def define_matrix_flag(self):
        self.matrix_flag = np.zeros((self.H_step, self.W_step))
        return

    def check_left_click(self, i, j):
        if not self.begin:
            # The first step is on the mine => reset
            while self.matrix_mine[i, j] == 1:
                self.matrix_init()
            # Game begins
            self.begin = True
            self.total_time = time.time()

        # On flag -> pass
        if self.matrix_flag[i, j] == 1:
            return

        # Hit the mine -> game over
        elif self.matrix_mine[i, j] == 1:
            self.fail = True

        # No any mines surrounded -> continuously click the safe regions
        elif self.matrix_count[i, j] == 0:
            self.fill_empty(i, j)

        # Some mines surrounded -> click the cell and display the count
        elif self.matrix_count[i, j] > 0:
            self.fill_one_cell(i, j)

        return

    def check_right_click(self, i, j):
        x = j * self.grid
        y = i * self.grid

        # Already clicked -> pass
        if self.matrix_clicked[i, j] == 1:
            return

        # Put a flag
        elif self.matrix_flag[i, j] == 0:
            self.matrix_flag[i, j] = 1
            self.Surface.blit(self.IMAGE.pika, [x, y])

        # Take off the flag
        else:
            self.matrix_flag[i, j] = 0
            pygame.draw.rect(self.Surface, [0, 0, 0], [x, y, self.cell_width, self.cell_width])
        return

    def check_middle_click_down(self, i, j):
        self.middle_click = True

        # Only functional on the place where count > 0
        if self.matrix_clicked[i,j] == 0 or (self.matrix_clicked[i,j] == 1 and self.matrix_count[i,j] == 0):
            return

        # Make the unclicked blocks gray
        for ii in [i - 1, i, i + 1]:
            for jj in [j - 1, j, j + 1]:
                if 0 <= ii < self.H_step and 0 <= jj < self.W_step:
                    if self.matrix_clicked[ii, jj] == 0 and self.matrix_flag[ii, jj] == 0:
                        x = jj * self.grid
                        y = ii * self.grid
                        pygame.draw.rect(self.Surface, [100, 100, 100], [x, y, self.cell_width, self.cell_width])
        return

    def check_middle_click_up(self, i, j):
        self.middle_click = False

        # Recover the gray cells
        for ii in [i - 1, i, i + 1]:
            for jj in [j - 1, j, j + 1]:
                if 0 <= ii < self.H_step and 0 <= jj < self.W_step:
                    if self.matrix_clicked[ii, jj] == 0 and self.matrix_flag[ii, jj] == 0:
                        x = jj * self.grid
                        y = ii * self.grid
                        pygame.draw.rect(self.Surface, [0, 0, 0], [x, y, self.cell_width, self.cell_width])

        # Count the number of flags around the cell
        flag_count = self.matrix_flag[max(i-1, 0):min(i+2, self.H_step+1), max(j-1, 0):min(j+2, self.W_step+1)].sum()

        # If the number of flags equals the mine count in the cell, reveal surrounding cells
        if flag_count == self.matrix_count[i, j]:
            for ii in [i - 1, i, i + 1]:
                for jj in [j - 1, j, j + 1]:
                    if 0 <= ii < self.H_step and 0 <= jj < self.W_step:
                        self.check_left_click(ii, jj)
        return

    def check_status_win(self):
        if not np.any((self.matrix_clicked + self.matrix_mine) == 0):
            self.win = True
            self.TEXT.text_time()
            self.TEXT.text_win()
        return

    def action_fail(self):
        self.show_all_bomb(self.IMAGE.bomb)
        self.TEXT.text_over()
        return

    def fill_empty(self, i, j):
        # Click center cell
        self.fill_one_cell(i, j)

        # Check surrounding cells
        for ii in [i - 1, i, i + 1]:
            for jj in [j - 1, j, j + 1]:
                if 0 <= ii < self.H_step and 0 <= jj < self.W_step:
                    if self.matrix_clicked[ii, jj] or self.matrix_mine[ii, jj] or self.matrix_flag[ii, jj]: continue

                    if self.matrix_count[ii, jj] == 0:
                        self.fill_empty(ii, jj)
                    elif self.matrix_count[ii, jj] > 0:
                        self.fill_one_cell(ii, jj)
        return

    def fill_one_cell(self, i, j):
        x = j * self.grid
        y = i * self.grid
        self.matrix_clicked[i, j] = 1
        pygame.draw.rect(self.Surface, [255, 255, 255], [x, y, self.cell_width, self.cell_width])

        if self.matrix_count[i, j] > 0:
            text = self.Font.render(str(int(self.matrix_count[i, j])), True, [0, 0, 0])
            text_rect = text.get_rect(center=(x + self.cell_width / 2, y + self.cell_width / 2))
            self.Surface.blit(text, text_rect)
        return
        

    def show_all_bomb(self, image_bomb):
        for i in range(self.H_step):
            for j in range(self.W_step):
                if self.matrix_mine[i, j] == 1:
                    x = j * self.grid
                    y = i * self.grid
                    pygame.draw.rect(self.Surface, [100, 100, 100], [x, y, self.cell_width, self.cell_width])
                    self.Surface.blit(image_bomb, [x, y])
                    pygame.display.flip()
                    pygame.time.delay(20)
        return

class PygameText:
    def __init__(self, game):
        self.game = game
        self.font = game.Font
        return

    def text_cover(self):
        text_cover = self.font.render('POKEMON BOMB!', True, [255, 255, 255])
        text_cover_rect = text_cover.get_rect(center=(self.game.W + self.game.W // 4, self.game.H // 3))
        self.game.Surface.blit(text_cover, text_cover_rect)
        return

    def text_over(self):
        text_over = self.font.render('GAME OVER', True, [255, 46, 10])
        text_over_rect = text_over.get_rect(center=(self.game.W + self.game.W // 4, self.game.H * 2 // 3))
        self.game.Surface.blit(text_over, text_over_rect)
        return

    def text_win(self):
        text_win = self.font.render('YOU WIN!', True, [255, 255, 255])
        text_win_rect = text_win.get_rect(center=(self.game.W + self.game.W // 4, self.game.H * 2 // 3))
        self.game.Surface.blit(text_win, text_win_rect)
        return

    def text_time(self):
        text_time = self.font.render('time: %3.2f' % (time.time() - self.game.total_time), True, [255, 255, 255])
        text_time_rect = text_time.get_rect(center=(self.game.W + self.game.W // 4, self.game.H * 3 // 4))
        self.game.Surface.blit(text_time, text_time_rect)
        return

class PygameImage:
    def __init__(self, game):
        self.game = game
        pika_raw = pygame.image.load('./DATA/pika.png').convert_alpha()
        self.pika = pygame.transform.scale(pika_raw, (self.game.cell_width, self.game.cell_width))
        bomb_raw = pygame.image.load('./DATA/bomb.png').convert_alpha()
        self.bomb = pygame.transform.scale(bomb_raw, (self.game.cell_width, self.game.cell_width))
        return

def main():
    MINE = Minesweeper()
    pygame.draw.rect(MINE.Surface, [10, 10, 10], [MINE.W, 0, 250, MINE.H])
    MINE.TEXT.text_cover()
    pygame.display.flip()

    while True:
        for event in pygame.event.get():

            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            if MINE.win or MINE.fail:
                continue

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pressed_mouse = pygame.mouse.get_pressed()
                grid_x = pygame.mouse.get_pos()[0] // MINE.grid
                grid_y = pygame.mouse.get_pos()[1] // MINE.grid

                if grid_x >= MINE.W_step:
                    continue

                ### LEFT button ###
                if pressed_mouse[0]:
                    MINE.check_left_click(grid_y, grid_x)

                ### RIGHT button ###
                elif pressed_mouse[2]:
                    MINE.check_right_click(grid_y, grid_x)

                ### Middle button ###
                elif pressed_mouse[1] or (pressed_mouse[0] and pressed_mouse[2]):
                    MINE.check_middle_click_down(grid_y, grid_x)


            elif event.type == pygame.MOUSEBUTTONUP and MINE.middle_click:
                MINE.check_middle_click_up(grid_y, grid_x)
                continue

            MINE.check_status_win()

            if MINE.fail:
                MINE.action_fail()

        pygame.display.flip()

if __name__ == "__main__":
    main()
