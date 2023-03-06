import sys

import pygame
import chess
import chess.engine

MAX_DEPTH = 5

# Initialize the Pygame module
pygame.init()

# Set the screen dimensions
screen_width = 600
screen_height = 600

# Create the Pygame screen
screen = pygame.display.set_mode((screen_width, screen_height))

# Set the font and font size for the text
font = pygame.font.SysFont("Arial", 24)

# Initialize the Stockfish engine
engine = chess.engine.SimpleEngine.popen_uci(
    r"res/Chess/stockfish-windows-2022-x86-64-avx2.exe")

# Create a clock object to limit the frame rate
clock = pygame.time.Clock()
fps = 60


def board_evaluation(board):
    """
    Evaluate the given chess board and return a score for the current player.
    Positive scores indicate an advantage for White, while negative scores indicate
    an advantage for Black.
    """
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0  # The king's value is not used in this heuristic
    }

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value

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
    if depth == 0 or board.is_game_over():
        # If we've reached the maximum depth or the game is over, return the static evaluation
        return board_evaluation(board)

    if maximizing_player:
        # If it's the maximizing player's turn
        max_eval = float('-inf')
        for move in board.legal_moves:
            # Apply the move to the board
            board.push(move)
            # Recursively evaluate the position after the move
            eval = minimax(board, depth - 1, alpha, beta, False)
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
        min_eval = float('inf')
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


def get_best_move(board):
    best_move = None
    max_eval = float('-inf')
    alpha = float('-inf')
    beta = float('inf')
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


def draw_board(board, selected_square=None):
    # Define the colors for the chessboard and highlighting
    light_color = (255, 206, 158)
    dark_color = (209, 139, 71)
    highlight_color = (0, 255, 0, 50)  # Make the highlighting semi-transparent
    highlight_color2 = (173, 255, 47)

    # Define the dimensions for the squares
    square_size = screen_width // 8

    # Draw the chessboard
    for row in range(8):
        for col in range(8):
            x = col * square_size
            y = row * square_size
            color = light_color if (row + col) % 2 == 0 else dark_color
            if selected_square is not None and chess.square(col, 7 - row) == selected_square:
                color = highlight_color
            pygame.draw.rect(screen, color, pygame.Rect(x, y, square_size, square_size))

            # Highlight the legal moves for the selected piece
            if selected_square is not None:
                moves = board.legal_moves
                legal_squares = set(move.to_square for move in moves if move.from_square == selected_square)
                if chess.square(col, 7 - row) in legal_squares:
                    pygame.draw.rect(screen, highlight_color2, pygame.Rect(x, y, square_size, square_size))

    # Draw the chess pieces
    for row in range(8):
        for col in range(8):
            square = chess.square(col, 7 - row)
            piece = board.piece_at(square)
            if piece is not None:
                filename = f"res/pieces/{piece.color}/{piece.symbol()}.png"
                image = pygame.image.load(filename)
                image = pygame.transform.scale(image, (square_size, square_size))
                rect = image.get_rect()
                rect.x = col * square_size
                rect.y = row * square_size
                screen.blit(image, rect)


# Create a new chess board
board = chess.Board()

# Initialize the selected square variable
selected_square = None


def get_selected_square():
    # Get the position of the mouse click
    mouse_pos = pygame.mouse.get_pos()

    # Convert the mouse position to a chess square
    col = mouse_pos[0] // (screen_width // 8)
    row = 7 - mouse_pos[1] // (screen_height // 8)
    return chess.square(col, row)


# Play the game until it's over
if not board.is_game_over():
    while 1:
        # Draw the board to the Pygame screen
        draw_board(board, selected_square)

        # Draw the text for the player's turn
        turn_text = "White's turn" if board.turn == chess.WHITE else "Black's turn"
        text = font.render(turn_text, True, (255, 255, 255))
        screen.blit(text, (10, 10))

        # Update the Pygame screen
        pygame.display.flip()

        clock.tick(fps)

        # If it's the player's turn (white)
        if board.turn == chess.WHITE:
            # Handle Pygame events
            for event in pygame.event.get():
                # If the user closes the window, exit the program
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # If the user clicks on the board
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    square = get_selected_square()
                    # If the user has not yet selected a square
                    if selected_square is None:
                        # If the selected square has a piece and it belongs to the player whose turn it is
                        if board.piece_at(square) is not None and board.piece_at(square).color == board.turn:
                            selected_square = square
                    # If the user has already selected a square
                    else:
                        # If the selected square is a valid move for the piece
                        move = chess.Move(selected_square, square)
                        if move in board.legal_moves:
                            # Make the move
                            board.push(move)
                        # Deselect the square
                        selected_square = None

        # If it's the computer's turn (black)
        elif board.turn == chess.BLACK:
            # Get the best move from the Stockfish engine
            best_move = get_best_move(board)

            # Make the move
            board.push(best_move)
elif board.is_game_over():
    if board.result() == '1-0':
        message = "White wins!"
    elif board.result() == '0-1':
        message = "Black wins!"
    else:
        message = "Draw!"

# Draw board one last time to show the end state
draw_board(board)
