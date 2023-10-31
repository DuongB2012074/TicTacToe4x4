import sys
import pygame
# Thư viện numpy giúp tính toán hiệu quả với ma trận và mảng
import numpy as np

import random
import copy

from constants import *

# Pygame setup
pygame.init()
# Dòng hiển thị cấu hình ứng dụng
screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
pygame.display.set_caption('Trò chơi TIC TAC TOE')
screen.fill( BG_COLOR )

# Hàm thiết kế bảng điều khiển khi chơi "Board"
class Board:
    def __init__(self):
        self.squares = np.zeros( (ROWS, COLS) )
        self.empty_sqrs = self.squares # [squares]
        self.marked_sqrs = 0
        
    def final_state(self, show = False):
        '''
            @return 0 nếu không có một người chơi nào win
            @return 1 nếu người chơi 1 (player 1) wins
            @return 2 nếu người chơi 2 (player 2) wins
        '''    
        # điều kiện thắng theo chiều dọc
        for col in range(COLS):
            if self.squares[0][col] == self.squares[1][col] == self.squares[2][col] == self.squares[3][col] != 0:
                if show:
                    color = O_COLOR if self.squares[0][col] == 2 else X_COLOR
                    iPos = (col * SQSIZE + SQSIZE // 2, 20)
                    fPos = (col * SQSIZE + SQSIZE // 2, HEIGHT - 20)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[0][col]
        # điều kiện thắng theo chiều ngang
        for row in range(ROWS):
            if self.squares[row][0] == self.squares[row][1] == self.squares[row][2] == self.squares[row][3] != 0:
                if show:
                    color = O_COLOR if self.squares[row][0] == 2 else X_COLOR
                    iPos = (20, row * SQSIZE + SQSIZE // 2)
                    fPos = (WIDTH - 20, row * SQSIZE + SQSIZE // 2)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[row][0]
        # điều kiện thắng theo chiều chéo từ trái sang phải
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] == self.squares[3][3] != 0:
            if show:
                    color = O_COLOR if self.squares[1][1] == 2 else X_COLOR
                    iPos = (20, 20)
                    fPos = (WIDTH - 20, HEIGHT - 20)
                    pygame.draw.line(screen, color, iPos, fPos, X_WIDTH)
            return self.squares[1][1]
        # điều kiện thắng theo đường chéo từ phải sang trái
        if self.squares[3][0] == self.squares[2][1] == self.squares[1][2] == self.squares[0][3] != 0:
            if show:
                    color = O_COLOR if self.squares[2][1] == 2 else X_COLOR
                    iPos = (20, HEIGHT - 20)
                    fPos = (WIDTH - 20, 20)
                    pygame.draw.line(screen, color, iPos, fPos, X_WIDTH)
            return self.squares[2][1]
        # không người chơi nào chiến thắng
        return 0
            
    def mark_sqr(self, row, col, player):
        self.squares[row][col] = player
        self.marked_sqrs += 1
    def empty_sqr(self,row,col):
        return self.squares[row][col] == 0
    
    def get_empty_sqrs(self):
        empty_sqrs = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.empty_sqr(row,col):
                    empty_sqrs.append( (row,col) )
        return empty_sqrs
    
    def isfull(self):
        # return self.marked_sqrs == MAX_MARK
        return self.marked_sqrs == 16
    def isempty(self):
        return self.marked_sqrs == 0

# Hàm thiết kế AI theo giải thuật Minimax
class AI:
    def __init__(self, level=1, player=2):
        self.level = level
        self.player = player
    # Hàm random
    def rnd(self, board):
        empty_sqrs = board.get_empty_sqrs()
        idx = random.randrange(0, len(empty_sqrs))
        
        return empty_sqrs[idx]  # trả về 1 (row, col) nào đó
    
    # Hàm minimax của AI
    def minimax(self, board, maximizing):
        # Trường hợp cuối (Terminal case)
        case = board.final_state()
        
        # Player 1 wins
        if case == 1:
            return 1, None # eval move
        # Player 2 wins (AI minimax)
        if case ==2:
            return -1, None
        #draw
        elif board.isfull():
            return 0, None
        
        if maximizing:
            max_eval = -100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()
            
            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, 1)
                eval = self.minimax(temp_board, False)[0]
                if eval <= max_eval:
                    break
                else:
                    max_eval = eval
                    best_move = (row, col)
            return max_eval, best_move
        
        elif not maximizing:
            min_eval = 100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()
            
            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, self.player)
                eval = self.minimax(temp_board, True)[0]
                if eval >= min_eval:
                    break
                else:
                    min_eval = eval
                    best_move = (row, col)
            return min_eval, best_move
    
    def eval(self, main_board):
        if self.level == 0:
            # AI chọn đường đi ngẫu nhiên khi bàn cờ ở giai đoạn đầu
            eval = 'random'
            move = self.rnd(main_board)
        else:
            # Chọn theo giải thuật minimax khi bàn cờ đã đi được tới 1 mức độ định hình
            eval, move = self.minimax(main_board, False)
            
        print(f'AI has chosen to mark the square in pos {move} with an eval of {eval}')
        
        return move # row, col

class Game:
    def __init__(self):
        # Lấy hàm board xuống
        self.board = Board()
        self.ai = AI()
        self.player = 1  # player1 là X  # player2 là O
        self.gamemode = 'ai' #pvp or AI
        self.running = True
        
        self.show_line()
        
    def make_move(self, row, col):
        self.board.mark_sqr(row,col,self.player)
        self.draw_fig(row,col)
        self.next_turn()
        
    # Hàm hiển thị dòng và cột
    def show_line(self):
        screen.fill( BG_COLOR )
        
        # Dòng để vẽ ra cột
        pygame.draw.line(screen, LINE_COLOR, (SQSIZE, 0), (SQSIZE, HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (WIDTH - SQSIZE, 0), (WIDTH - SQSIZE, HEIGHT), LINE_WIDTH)
        # vẽ ra dòng ở giữa nếu bàn cờ là 4x4
        pygame.draw.line(screen, LINE_COLOR, (WIDTH, SQSIZE*2), (0,SQSIZE*2), LINE_WIDTH)
        
        # Dòng để vẽ ra dòng
        pygame.draw.line(screen, LINE_COLOR, (0, SQSIZE), (WIDTH, SQSIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (0, HEIGHT - SQSIZE), (WIDTH, HEIGHT - SQSIZE), LINE_WIDTH)
        # vẽ ra cột ở giữa nếu bàn cờ là 4x4
        pygame.draw.line(screen, LINE_COLOR, (SQSIZE*2, HEIGHT), (SQSIZE*2,0), LINE_WIDTH)
        
    # hàm vẽ nút O và X cho player
    def draw_fig(self,row,col):
        if self.player == 1:
            # draw X
            # desc line vẽ đường chéo từ trái sang phải
            start_desc = (col * SQSIZE + OFFSET, row * SQSIZE + OFFSET)
            end_desc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            pygame.draw.line(screen, X_COLOR, start_desc, end_desc, X_WIDTH)
            # asc line vẽ đường chéo từ phải sang trái
            start_asc = (col * SQSIZE + OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            end_asc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + OFFSET)
            pygame.draw.line(screen, X_COLOR, start_asc, end_asc, X_WIDTH)
            
        elif self.player == 2:
            #draw O
            center = (col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2)
            pygame.draw.circle(screen, O_COLOR, center, RADIUS, O_WIDTH)
        
    def next_turn(self):
        self.player = self.player % 2 + 1
    
    def change_gamemode(self):
        self.gamemode = 'ai' if self.gamemode == 'pvp' else 'pvp'
    
    # Hàm kiểm tra tiến độ của game dừng khi 1 trong 2 win hoặc hòa
    def isover(self):
        return self.board.final_state(show=True) != 0 or self.board.isfull()
    
    def reset(self):
        self.__init__()

def main():
    # Gọi hàm "Game"
    game = Game()
    board = game.board
    ai = game.ai
    
    # Main loop
    while True:
        for event in pygame.event.get():
            # Hàm if để tắt ứng dụng
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                # g-gamemode
                if event.key == pygame.K_g:
                    game.change_gamemode()
                
                # r-restart
                if event.key == pygame.K_r:
                    game.reset()
                    board = game.board
                    ai = game.ai
                
                # 0-random ai
                if event.key == pygame.K_0:
                    ai.level = 0
                
                # 1-random ai
                if event.key == pygame.K_1:
                    ai.level = 1
            
            # Hàm if dùng để bắt event click chuột lên ma trận
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Câu lệnh để bắt các ô trong ma trận 3x3 (VD: [0][1], [1][1]...)
                pos = event.pos
                row = pos[1] // SQSIZE
                col = pos[0] // SQSIZE

                if board.empty_sqr(row,col) and game.running:
                    # Hàm bắt click chuột chọn vị trí trên ma trận
                    game.make_move(row, col)
                    # Lệnh để in ra tên player ma trận lưu lại click chột trên ma trận đó biển đổi từ 0 -> 1 player1 hoặc 0 -> 2 player2
                    # print(game.board.squares)
                    
                    # Lệnh để dừng khi 1 trong2 win hoặc hòa, tránh crash game
                    if game.isover():
                        game.running = False
            
                
        if game.gamemode == 'ai' and game.player == ai.player and game.running:
            # Update the screen
            pygame.display.update()
            
            # AI methods
            row, col = ai.eval(board)
            game.make_move(row, col)
            
            if game.isover():
                game.running = False
            
        # Hàm cập nhật lại ảnh nền cho ứng dụng
        pygame.display.update()

main()