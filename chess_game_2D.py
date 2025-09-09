import customtkinter as ctk
import chess
import requests
import tkinter.messagebox as messagebox

# Chess board setup
board = chess.Board()
move_history = []
selected_square = None

# Default font settings
DEFAULT_FONT = "Arial"
DEFAULT_FONT_SIZE = 35
Font = (DEFAULT_FONT, DEFAULT_FONT_SIZE)

# Map chess pieces to Unicode symbols
PIECE_UNICODE_MAP = {
    'p': '♟', 'P': '♙',
    'r': '♜', 'R': '♖',
    'n': '♞', 'N': '♘',
    'b': '♝', 'B': '♗',
    'q': '♛', 'Q': '♕',
    'k': '♚', 'K': '♔',
}

def piece_to_unicode(piece):
    return PIECE_UNICODE_MAP.get(piece.symbol(), '') if piece else ''

def get_best_move_online(fen):
    """Get best move from online Stockfish API."""
    try:
        response = requests.post("https://chess-api.com/v1", json={"fen": fen})
        return response.json().get("move")
    except Exception as e:
        messagebox.showerror("Connection Error", f"Failed to connect to Stockfish API.\n{e}")
        return None

def update_board():
    for row in range(8):
        for col in range(8):
            piece = board.piece_at(chess.square(col, 7 - row))
            color = "white" if (row + col) % 2 == 0 else "gray"
            squares[row][col].configure(text=piece_to_unicode(piece), fg_color=color)

def reset_game():
    global board, move_history, selected_square
    board = chess.Board()
    move_history = []
    selected_square = None
    update_board()
    update_move_history()

def promote_pawn_with_window(move):
    promotion_window = ctk.CTkToplevel(root)
    promotion_window.title("Pawn Promotion")
    promotion_window.geometry("300x305")
    promotion_label = ctk.CTkLabel(promotion_window, text="Choose your promotion:", font=("Arial", 15))
    promotion_label.pack(pady=10)

    def set_promotion(promotion_piece):
        promotion_move = chess.Move(move.from_square, move.to_square, promotion_piece)
        board.push(promotion_move)
        move_history.append(f"Player: {promotion_move}")
        promotion_window.destroy()

        best_move = get_best_move_online(board.fen())
        if best_move:
            board.push(chess.Move.from_uci(best_move))
            move_history.append(f"Opponent: {best_move}")
        update_board()
        update_move_history()
        process_game_status()

    for piece, label in [(chess.QUEEN, "Queen (♛)"), (chess.ROOK, "Rook (♜)"),
                         (chess.BISHOP, "Bishop (♝)"), (chess.KNIGHT, "Knight (♞)")]:
        ctk.CTkButton(promotion_window, text=label, hover_color="black",
                      fg_color="saddle brown", command=lambda p=piece: set_promotion(p)).pack(pady=5)

def move_piece(row, col):
    global selected_square
    if selected_square is None:
        selected_square = (row, col)
    else:
        from_square = chess.square(selected_square[1], 7 - selected_square[0])
        to_square = chess.square(col, 7 - row)
        move = chess.Move(from_square, to_square)
        promotion_move = chess.Move(move.from_square, move.to_square, chess.QUEEN)

        if move in board.legal_moves:
            board.push(move)
            move_history.append(f"Player: {move}")
            process_game_status()

            best_move = get_best_move_online(board.fen())
            if best_move:
                board.push(chess.Move.from_uci(best_move))
                move_history.append(f"Opponent: {best_move}")
                process_game_status()

            update_board()
            update_move_history()
        elif promotion_move in board.legal_moves:
            promote_pawn_with_window(move)
        else:
            messagebox.showerror("Invalid Move", "This move is not allowed.")

        selected_square = None

def process_game_status():
    if board.is_checkmate():
        messagebox.showinfo("Game Status", "Checkmate!")
    elif board.is_stalemate():
        messagebox.showinfo("Game Status", "Draw! (Stalemate)")
    elif board.is_repetition():
        messagebox.showinfo("Game Status", "Draw! (Threefold Repetition)")
    elif board.is_fifty_moves():
        messagebox.showinfo("Game Status", "Draw! (Fifty-Move Rule)")
    elif board.is_insufficient_material():
        messagebox.showinfo("Game Status", "Draw! (Insufficient Material)")
    elif board.is_check():
        messagebox.showinfo("Game Status", "Check!")

def update_move_history():
    history_box.configure(state="normal")
    history_box.delete("1.0", "end")
    for move in move_history:
        history_box.insert("end", f"{move}\n")
    history_box.see("end")
    history_box.configure(state="disabled")

# UI setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
root = ctk.CTk()
root.title("Chess Game")
root.geometry("500x540")

tab_view = ctk.CTkTabview(root, segmented_button_selected_hover_color="#AD6735", segmented_button_selected_color="#8B4513")
tab_view.pack(expand=True, fill="both")
game_tab = tab_view.add("Game")
settings_tab = tab_view.add("Settings")
history_tab = tab_view.add("History")
reset_tab = tab_view.add("Reset")

squares = [[None for _ in range(8)] for _ in range(8)]
for row in range(8):
    for col in range(8):
        color = "white" if (row + col) % 2 == 0 else "gray"
        squares[row][col] = ctk.CTkButton(
            game_tab,
            text='',
            width=60,
            height=60,
            fg_color=color,
            corner_radius=3,
            hover_color="#191970",
            text_color="saddle brown",
            font=Font,
            command=lambda r=row, c=col: move_piece(r, c)
        )
        squares[row][col].grid(row=row, column=col)

update_board()

history_label = ctk.CTkLabel(history_tab, text="Move History:", font=("Arial", 15))
history_label.pack(pady=10)
history_box = ctk.CTkTextbox(history_tab, width=700, height=500)
history_box.configure(state="disabled")
history_box.pack(pady=10)

def apply_settings():
    global DEFAULT_FONT, Font
    font_options = {"Minimal": "Arial", "Classic": "Quivira", "Modern": "Pecita"}
    DEFAULT_FONT = font_options[font_var.get()]
    Font = (DEFAULT_FONT, DEFAULT_FONT_SIZE)

    for row in range(8):
        for col in range(8):
            squares[row][col].configure(font=Font)

    update_board()

reset_button = ctk.CTkButton(reset_tab, text="Reset Game", command=reset_game, hover_color="black", fg_color="saddle brown")
reset_button.pack(pady=20)

font_label = ctk.CTkLabel(settings_tab, text="Font:")
font_label.pack(pady=10)
font_var = ctk.StringVar(value="Minimal")
font_dropdown = ctk.CTkOptionMenu(settings_tab, variable=font_var, values=["Minimal", "Classic", "Modern"], fg_color="saddle brown", button_color="#793301", button_hover_color="#000000")
font_dropdown.pack()

apply_button = ctk.CTkButton(settings_tab, text="Apply", hover_color="black", fg_color="saddle brown", command=apply_settings)
apply_button.pack(pady=20)

root.mainloop()
