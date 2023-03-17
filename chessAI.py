import sys

import chess
import chess.engine
import chess.polyglot

MAX_DEPTH = 3

#Initialize piece square tables
#Values taken from https://www.talkchess.com/forum3/viewtopic.php?f=2&t=68311&start=19
#Position 0 in table is a8, position 63 is h1 (Seen from white's perspective)
#Use directly for black, flip for white
pawntable = [
    0,   0,   0,   0,   0,   0,  0,   0,
     98, 134,  61,  95,  68, 126, 34, -11,
     -6,   7,  26,  31,  65,  56, 25, -20,
    -14,  13,   6,  21,  23,  12, 17, -23,
    -27,  -2,  -5,  12,  17,   6, 10, -25,
    -26,  -4,  -4, -10,   3,   3, 33, -12,
    -35,  -1, -20, -23, -15,  24, 38, -22,
      0,   0,   0,   0,   0,   0,  0,   0,
]

knighttable = [
    -167, -89, -34, -49,  61, -97, -15, -107,
     -73, -41,  72,  36,  23,  62,   7,  -17,
     -47,  60,  37,  65,  84, 129,  73,   44,
      -9,  17,  19,  53,  37,  69,  18,   22,
     -13,   4,  16,  13,  28,  19,  21,   -8,
     -23,  -9,  12,  10,  19,  17,  25,  -16,
     -29, -53, -12,  -3,  -1,  18, -14,  -19,
    -105, -21, -58, -33, -17, -28, -19,  -23,
    ]

bishoptable = [
    -29,   4, -82, -37, -25, -42,   7,  -8,
    -26,  16, -18, -13,  30,  59,  18, -47,
    -16,  37,  43,  40,  35,  50,  37,  -2,
     -4,   5,  19,  50,  37,  37,   7,  -2,
     -6,  13,  13,  26,  34,  12,  10,   4,
      0,  15,  15,  15,  14,  27,  18,  10,
      4,  15,  16,   0,   7,  21,  33,   1,
    -33,  -3, -14, -21, -13, -12, -39, -21,
    ]

rooktable = [
    32,  42,  32,  51, 63,  9,  31,  43,
     27,  32,  58,  62, 80, 67,  26,  44,
     -5,  19,  26,  36, 17, 45,  61,  16,
    -24, -11,   7,  26, 24, 35,  -8, -20,
    -36, -26, -12,  -1,  9, -7,   6, -23,
    -45, -25, -16, -17,  3,  0,  -5, -33,
    -44, -16, -20,  -9, -1, 11,  -6, -71,
    -19, -13,   1,  17, 16,  7, -37, -26,
]

queentable = [
    -28,   0,  29,  12,  59,  44,  43,  45,
    -24, -39,  -5,   1, -16,  57,  28,  54,
    -13, -17,   7,   8,  29,  56,  47,  57,
    -27, -27, -16, -16,  -1,  17,  -2,   1,
     -9, -26,  -9, -10,  -2,  -4,   3,  -3,
    -14,   2, -11,  -2,  -5,   2,  14,   5,
    -35,  -8,  11,   2,   8,  15,  -3,   1,
     -1, -18,  -9,  10, -15, -25, -31, -50,
]

kingtable = [
    -65,  23,  16, -15, -56, -34,   2,  13,
     29,  -1, -20,  -7,  -8,  -4, -38, -29,
     -9,  24,   2, -16, -20,   6,  22, -22,
    -17, -20, -12, -27, -30, -25, -14, -36,
    -49,  -1, -27, -39, -46, -44, -33, -51,
    -14, -14, -22, -46, -44, -30, -15, -27,
      1,   7,  -8, -64, -43, -16,   9,   8,
    -15,  36,  12, -54,   8, -28,  24,  14,
]

psqt = [pawntable, knighttable, bishoptable, rooktable, queentable, kingtable]

def board_evaluation(board):
    """
    Evaluate the given chess board and return a score for the current player.
    Positive scores indicate an advantage for White, while negative scores indicate
    an advantage for Black.
    """
    piece_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 300,
        chess.BISHOP: 300,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 0  # The king's value is not used in this heuristic
    }

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                score += value + psqt[piece.piece_type - 1][chess.square_mirror(square)]
            else:
                score -= value + psqt[piece.piece_type - 1][square]

    if piece is not None and piece.piece_type == chess.PAWN:
        if piece.color == chess.WHITE and chess.square_rank(square) == 6:
            # Promote white pawn to queen on the 8th rank
            if square // 8 == 7:  # check if on 7th rank
                board.promote(square, chess.QUEEN)
        elif piece.color == chess.BLACK and chess.square_rank(square) == 1:
            # Promote black pawn to queen on the 1st rank
            if square // 8 == 1:  # check if on 2nd rank
                board.promote(square, chess.QUEEN)
    return score


def minimax(board, depth, alpha, beta, maximizing_player):
    if board.is_checkmate() and maximizing_player:
        return -9999
    elif board.is_checkmate() and not maximizing_player:
        return 9999
    if depth == 0:
        return quiesce(alpha, beta, board)
    
    if maximizing_player:
        # If it's the maximizing player's turn
        max_eval = -9999
        for move in board.legal_moves:
            # Apply the move to the board
            board.push(move)
            # Recursively evaluate the position after the move
            eval = -minimax(board, depth - 1, -alpha, -beta, False)
            # Undo the move
            board.pop()
            # Update the maximum evaluation and alpha value
            if eval > max_eval:
                max_eval = eval
            if eval > alpha:
                alpha = eval
            if beta <= alpha:
                # If beta is less than or equal to alpha, prune the rest of the tree
                break
        return max_eval
    else:
        # If it's the minimizing player's turn
        min_eval = 9999
        for move in board.legal_moves:
            # Apply the move to the board
            board.push(move)
            # Recursively evaluate the position after the move
            eval = minimax(board, depth - 1, alpha, beta, True)
            # Undo the move
            board.pop()
            # Update the minimum evaluation and beta value
            if eval < min_eval:
                min_eval = eval
            if eval < beta:
                beta = eval
            if beta <= alpha:
                # If beta is less than or equal to alpha, prune the rest of the tree
                break
        return min_eval

# https://www.chessprogramming.org/Static_Exchange_Evaluation
# TODO: Implement static exchange evaluation
def see(board):
    value = 0
    last_move = board.peek()
    

# https://www.chessprogramming.org/Quiescence_Search
# Use quiescence search to evaluate the position after a capture
def quiesce(alpha, beta, board):
    curr = board_evaluation(board)
    if curr >= beta:
        return curr
    if alpha < curr:
        alpha = curr
    for move in board.legal_moves:
        if board.is_capture(move) or board.is_check():
            board.push(move)
            score = -quiesce(-beta, -alpha, board)
            board.pop()
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
    return alpha
    
def get_best_move(board):
    try:
        move = chess.polyglot.MemoryMappedReader("human.bin").weighted_choice(board).move
        return move
    except:
        best_move = None
        max_eval = -9999
        alpha = -99999
        beta = 99999
        for move in board.legal_moves:
            # Apply the move to the board
            board.push(move)
            # Evaluate the position after the move using the minimax algorithm with alpha-beta pruning
            eval = minimax(board, MAX_DEPTH, alpha, beta, False)
            # Undo the move
            board.pop()
            # Update the best move and maximum evaluation
            if eval > max_eval:
                max_eval = eval
                best_move = move
            if eval > alpha:
                alpha = eval
        return best_move