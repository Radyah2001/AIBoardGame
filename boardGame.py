import chess
import chess.engine
from IPython.display import SVG, display
import chess.svg

# Initialize the Stockfish engine
engine = chess.engine.SimpleEngine.popen_uci(
    r"C:\Users\Haydars-PC\Desktop\Chess\stockfish-windows-2022-x86-64-avx2.exe")


def print_board(board):
    display(SVG(chess.svg.board(board=board)))


def save_board(board, filename):
    svg = chess.svg.board(board=board)
    with open(filename, 'w') as f:
        f.write(svg)




# Create a new chess board
board = chess.Board()

# Play the game until it's over
while not board.is_game_over():
    # Print the board to the console
    print_board(board)
    save_board(board, 'board.svg')

    # If it's the player's turn (white)
    if board.turn == chess.WHITE:
        # Prompt the player for their move
        move = input("Enter your move (in algebraic notation): ")
        try:
            board.push_san(move)
        except ValueError:
            print("Invalid move. Try again.")
    # If it's the AI's turn (black)
    else:
        # Use the Stockfish engine to choose the AI's move
        result = engine.play(board, chess.engine.Limit(time=1.0))
        board.push(result.move)

# Print the final board to the console
print_board(board)

# Determine the result of the game and print the outcome
result = board.result()
if result == "1-0":
    print("White wins!")
elif result == "0-1":
    print("Black wins!")
else:
    print("Draw!")

# Clean up the Stockfish engine
engine.quit()
