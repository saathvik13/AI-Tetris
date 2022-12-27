# Simple quintris program! v0.2
# D. Crandall, Sept 2021

from AnimatedQuintris import *
from SimpleQuintris import *
from kbinput import *
import time, sys, math

class HumanPlayer:
    def get_moves(self, quintris):
        print("Type a sequence of moves using: \n  b for move left \n  m for move right \n  n for rotation\n  h for horizontal flip\nThen press enter. E.g.: bbbnn\n")
        moves = input()
        return moves

    def control_game(self, quintris):
        while 1:
            c = get_char_keyboard()
            commands =  { "b": quintris.left, "h": quintris.hflip, "n": quintris.rotate, "m": quintris.right, " ": quintris.down }
            commands[c]()

#####
# This is the part you'll want to modify!
# Replace our super simple algorithm with something better
#
class ComputerPlayer:
    ENCLOSE_COSTS = 20
    OPEN_COSTS = 1
    LINE_SCORE = 1000

    # ***** copying began: QuintrisGame.py in given repo *****
    PIECES = [ [ " x ", "xxx", " x "], [ "xxxxx" ], [ "xxxx", "   x" ], [ "xxxx", "  x " ], [ "xxx", "x x"], [ "xxx ", "  xx" ] ]
    @staticmethod
    def rotate_piece(piece):
        rotated_90 = [ "".join([ str[i] for str in piece[::-1] ]) for i in range(0, len(piece[0])) ]
        rotated_180 = [ str[::-1] for str in piece[::-1] ]
        rotated_270 = [ str[::-1] for str in rotated_90[::-1] ]
        return [piece, rotated_90, rotated_180, rotated_270]
    @staticmethod
    def place_piece(board, piece, row, col):
        return board[0:row] + \
                [ (board[i+row][0:col] + QuintrisGame.combine(r, board[i+row][col:col+len(r)]) + board[i+row][col+len(r):] ) for (i, r) in enumerate(piece) ] + \
                board[row+len(piece):]
    # ***** copying ended *****
    @staticmethod
    def check_collision(board, piece, row, col, non_empty_idx):
        # Optimization to quickly detect non-collision
        if row + len(piece) <= non_empty_idx:
            return False
        # ***** copying began: QuintrisGame.py in given repo *****
        return col+len(piece[0]) > len(board[0]) or row+len(piece) > len(board) \
            or any( [ any( [ (c != " " and board[i_r+row][col+i_c] != " ") for (i_c, c) in enumerate(r) ] ) for (i_r, r) in enumerate(piece) ] )
        # ***** copying ended *****
    @staticmethod
    def down(board, piece, col):
        for i in range(0, len(board)):
            if 'x' in board[i]:
                break
        non_empty_idx = i
        if ComputerPlayer.check_collision(board, piece, 0, col, non_empty_idx):
            return False
        row = 0
        # ***** copying began: QuintrisGame.py in given repo *****
        while not ComputerPlayer.check_collision(board, piece, row + 1, col, non_empty_idx):
            row += 1
        # ***** copying ended *****
        return ComputerPlayer.place_piece(board, piece, row, col)

    @staticmethod
    def heuristic(board):
        height = len(board)
        width = len(board[0])
        score = 0
        for i in range(height - 1, -1, -1):
            if ' ' not in board[i]:
                score += ComputerPlayer.LINE_SCORE
        for i in range(0, height):
            if 'x' in board[i]:
                break
        non_empty_idx = i

        costs = 0
        for x in range(0, width):
            if_enclosed = False
            for y in range(non_empty_idx, height):
                if board[y][x] == ' ':
                    c = ComputerPlayer.ENCLOSE_COSTS if if_enclosed else ComputerPlayer.OPEN_COSTS
                    costs += (y / height) * c
                else: # 'x'
                    if_enclosed = True
        # print("heuristic: ", '\n'.join(board), score-costs)
        return score - costs

    def dist_stats(self, piece):
        self.dist[self.piece2idx['\n'.join(piece)]] += 1
        self.dist_count += 1

    def __init__(self):
        self.dist = [0] * 6
        self.dist_count = 0
        self.piece2idx = dict()
        for i in range(0, len(ComputerPlayer.PIECES)):
            ps = ComputerPlayer.rotate_piece(ComputerPlayer.PIECES[i])
            for a in range(0, 4):
                k = '\n'.join(ps[a])
                # angle_to_shape = (360 - a * 90) % 360
                if k not in self.piece2idx: #or self.piece2idx[k][1] > angle_to_shape:
                    self.piece2idx[k] = i #(i, angle_to_shape)

    def max_node(self, cur_piece, board, depth, next_piece = None, pos = None):
        cur_rotates = ComputerPlayer.rotate_piece(cur_piece)
        s_cur_rotates = list(map(lambda x: '\n'.join(x), cur_rotates))
        visited = set()
        remained_rotates = []
        for i in range(0, 4):
            if s_cur_rotates[i] in visited:
                continue
            visited.add(s_cur_rotates[i])
            remained_rotates.append((cur_rotates[i], i))
        max_reward = -math.inf
        max_cmd = ''
        for r_piece, angle in remained_rotates:
            for x in range(0, len(board[0]) - len(r_piece[0]) + 1):
                new_board = ComputerPlayer.down(board, r_piece, x)
                if new_board == False:
                    continue
                r = self.rand_node(new_board, depth, next_piece)
                if r > max_reward:
                    max_reward = r
                    if pos is not None:
                        max_cmd = 'b' * pos + 'n' * angle + 'm' * x
        return max_reward, max_cmd

    def rand_node(self, board, depth, next_piece):
        if depth == 0:
            return ComputerPlayer.heuristic(board)
        if next_piece is not None:
            return self.max_node(next_piece, board, depth - 1)[0]
        else:
            s = 0.0
            for i in range(0, len(ComputerPlayer.PIECES)):
                if self.dist[i] > 0:
                    s += self.dist[i] * self.max_node(ComputerPlayer.PIECES[i], board, depth - 1)[0]
            return s / self.dist_count


    # This function should generate a series of commands to move the piece into the "optimal"
    # position. The commands are a string of letters, where b and m represent left and right, respectively,
    # and n rotates. quintris is an object that lets you inspect the board, e.g.:
    #   - quintris.col, quintris.row have the current column and row of the upper-left corner of the
    #     falling piece
    #   - quintris.get_piece() is the current piece, quintris.get_next_piece() is the next piece after that
    #   - quintris.left(), quintris.right(), quintris.down(), and quintris.rotate() can be called to actually
    #     issue game commands
    #   - quintris.get_board() returns the current state of the board, as a list of strings.
    #
    def get_moves(self, quintris):
        # super simple current algorithm: just randomly move left, right, and rotate a few times
        # input("---------")
        if self.dist_count == 0:
            self.dist_stats(quintris.get_piece()[0])
        self.dist_stats(quintris.get_next_piece())
        _, cmd = self.max_node(quintris.get_piece()[0], quintris.get_board(), 2, quintris.get_next_piece(), quintris.get_piece()[2])
        print(cmd)
        return cmd

    # This is the version that's used by the animted version. This is really similar to get_moves,
    # except that it runs as a separate thread and you should access various methods and data in
    # the "quintris" object to control the movement. In particular:
    #   - quintris.col, quintris.row have the current column and row of the upper-left corner of the
    #     falling piece
    #   - quintris.get_piece() is the current piece, quintris.get_next_piece() is the next piece after that
    #   - quintris.left(), quintris.right(), quintris.down(), and quintris.rotate() can be called to actually
    #     issue game commands
    #   - quintris.get_board() returns the current state of the board, as a list of strings.
    #
    def control_game(self, quintris):
        # another super simple algorithm: just move piece to the least-full column
        time.sleep(0.1)
        # ***** copying began: SimpleQuintris.py in given repo *****
        COMMANDS = { "b": quintris.left, "n": quintris.rotate, "m": quintris.right}
        # ***** copying ended *****
        while 1:

            if self.dist_count == 0:
                self.dist_stats(quintris.get_piece()[0])
            self.dist_stats(quintris.get_next_piece())

            _, cmd = self.max_node(quintris.get_piece()[0], quintris.get_board(), 1, quintris.get_next_piece(), quintris.get_piece()[2])
            print(cmd)
            # ***** copying began: SimpleQuintris.py in given repo *****
            for c in cmd:
                COMMANDS[c]()
            # ***** copying ended *****
            quintris.down()




###################
#### main program

(player_opt, interface_opt) = sys.argv[1:3]

try:
    if player_opt == "human":
        player = HumanPlayer()
    elif player_opt == "computer":
        player = ComputerPlayer()
    else:
        print("unknown player!")

    if interface_opt == "simple":
        quintris = SimpleQuintris()
    elif interface_opt == "animated":
        quintris = AnimatedQuintris()
    else:
        print("unknown interface!")

    quintris.start_game(player)

except EndOfGame as s:
    print("\n\n\n", s)



