import sys

import pygame
import chess

from chessAI import get_best_move

MAX_DEPTH = 3

# Initialize the Pygame module
pygame.init()

# Set the screen dimensions
screen_width = 600
screen_height = 600

# Create the Pygame screen
screen = pygame.display.set_mode((screen_width, screen_height))

# Set the font and font size for the text
font = pygame.font.SysFont("Arial", 24)

# Create a clock object to limit the frame rate
clock = pygame.time.Clock()
fps = 60




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
