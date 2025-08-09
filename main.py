import os
import sys
import math
import pygame
import chess
import chess.engine
from typing import Optional, Tuple, List

############################
# ====== SETTINGS =========
############################
STOCKFISH_PATH = r"path_to_your_stockfish.exe"

FPS = 60
SQUARE_SIZE = 80
BOARD_MARGIN = 20
EVAL_BAR_WIDTH = 24
RIGHT_PANEL_WIDTH = 180
BUTTON_HEIGHT = 40
BUTTON_GAP = 12

LIGHT_COLOR = (240, 217, 181)
DARK_COLOR  = (181, 136, 99)
HINT_COLOR  = (106, 170, 228)
MOVE_FROM_COLOR = (246, 246, 105)
MOVE_TO_COLOR   = (186, 202, 68)
CHECK_COLOR     = (255, 90, 90)

FONT_NAME = "arial"

# Engine analysis settings
ANALYSIS_TIME_SEC = 0.15   # per frame when idle
HINT_TIME_SEC     = 0.5
ENGINE_MOVE_TIME  = 0.3

############################
# ====== INIT PYGAME ======
############################
pygame.init()
font_small = pygame.font.SysFont(FONT_NAME, 18)
font_medium = pygame.font.SysFont(FONT_NAME, 22)
font_large = pygame.font.SysFont(FONT_NAME, 28)

# Compute sizes
BOARD_SIZE_PX = SQUARE_SIZE * 8
WINDOW_WIDTH  = BOARD_MARGIN*2 + EVAL_BAR_WIDTH + BOARD_SIZE_PX + RIGHT_PANEL_WIDTH
WINDOW_HEIGHT = BOARD_MARGIN*2 + BOARD_SIZE_PX + BUTTON_GAP + BUTTON_HEIGHT

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Chess - Pygame + Stockfish")
clock = pygame.time.Clock()

############################
# ====== CHESS LOGIC ======
############################
board = chess.Board()
flip_board = False

# Undo/Redo stacks
undo_stack: List[chess.Move] = []
redo_stack: List[chess.Move] = []

# Engine
engine: Optional[chess.engine.SimpleEngine] = None
engine_ok = False
engine_err = None
try:
    if not os.path.isfile(STOCKFISH_PATH):
        raise FileNotFoundError(f"Stockfish not found at: {STOCKFISH_PATH}")
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    engine.configure({"Threads": max(1, os.cpu_count() // 2)})
    engine_ok = True
except Exception as e:
    engine_err = str(e)

# Drag & drop state
dragging = False
drag_from_sq: Optional[int] = None
drag_piece_surf: Optional[pygame.Surface] = None
drag_offset = (0, 0)

# Hint move
hint_move: Optional[chess.Move] = None

# Last move highlight
last_move: Optional[chess.Move] = None

############################
# ====== ASSETS (PIECES) ==
############################
# Simple vector-like rendering using unicode; for crisp look, you could replace with images.
UNICODE_PIECES = {
    chess.PAWN:   ("♙", "♟"),
    chess.KNIGHT: ("♘", "♞"),
    chess.BISHOP: ("♗", "♝"),
    chess.ROOK:   ("♖", "♜"),
    chess.QUEEN:  ("♕", "♛"),
    chess.KING:   ("♔", "♚"),
}

FONT_PATH = r"C:\Windows\Fonts\seguisym.ttf"  # Segoe UI Symbol
piece_font = pygame.font.Font(FONT_PATH, 64)

def piece_to_surface(piece: chess.Piece) -> pygame.Surface:
    text = UNICODE_PIECES[piece.piece_type][0 if piece.color == chess.WHITE else 1]
    surf = piece_font.render(text, True, (0, 0, 0))
    # Add subtle outline by blitting multiple times
    outline = piece_font.render(text, True, (255,255,255))
    base = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
    rect = surf.get_rect(center=(SQUARE_SIZE//2, SQUARE_SIZE//2))
    orect = outline.get_rect(center=(SQUARE_SIZE//2, SQUARE_SIZE//2))
    base.blit(outline, orect.move(1,1))
    base.blit(surf, rect)
    return base

############################
# ====== HELPERS ==========
############################
def square_to_coords(sq: int) -> Tuple[int,int]:
    # Returns file (x:0..7), rank (y:0..7) from white's perspective
    file = chess.square_file(sq)
    rank = chess.square_rank(sq)
    return file, rank

def coords_to_square(file: int, rank: int) -> int:
    return chess.square(file, rank)

def board_to_screen(file: int, rank: int) -> Tuple[int,int]:
    # Apply flipping
    draw_file = 7 - file if flip_board else file
    draw_rank = rank if flip_board else 7 - rank
    x = BOARD_MARGIN + EVAL_BAR_WIDTH + draw_file * SQUARE_SIZE
    y = BOARD_MARGIN + draw_rank * SQUARE_SIZE
    return x, y

def screen_to_board(px: int, py: int) -> Optional[int]:
    bx = px - (BOARD_MARGIN + EVAL_BAR_WIDTH)
    by = py - BOARD_MARGIN
    if bx < 0 or by < 0: return None
    file = bx // SQUARE_SIZE
    rank = by // SQUARE_SIZE
    if not (0 <= file <= 7 and 0 <= rank <= 7): return None
    # invert flip mapping
    real_file = 7 - file if flip_board else file
    real_rank = rank if flip_board else 7 - rank
    return coords_to_square(real_file, real_rank)

def legal_targets_from(sq: int) -> List[int]:
    return [m.to_square for m in board.legal_moves if m.from_square == sq]

def draw_board():
    # Squares
    for file in range(8):
        for rank in range(8):
            x, y = board_to_screen(file, rank)
            color = DARK_COLOR if (file + rank) % 2 == 0 else LIGHT_COLOR
            pygame.draw.rect(screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

    # Last move highlight
    if last_move:
        for sq, col in [(last_move.from_square, MOVE_FROM_COLOR), (last_move.to_square, MOVE_TO_COLOR)]:
            f, r = square_to_coords(sq)
            x, y = board_to_screen(f, r)
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s.fill((*col, 120))
            screen.blit(s, (x, y))

    # Check highlight
    if board.is_check():
        king_sq = board.king(board.turn)
        if king_sq is not None:
            f, r = square_to_coords(king_sq)
            x, y = board_to_screen(f, r)
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s.fill((*CHECK_COLOR, 90))
            screen.blit(s, (x, y))

    # Pieces
    for sq, piece in board.piece_map().items():
        if dragging and sq == drag_from_sq:
            continue
        f, r = square_to_coords(sq)
        x, y = board_to_screen(f, r)
        surf = piece_to_surface(piece)
        screen.blit(surf, (x + (SQUARE_SIZE - surf.get_width())//2,
                           y + (SQUARE_SIZE - surf.get_height())//2))

    # Legal move hints (circles) when dragging
    if dragging and drag_from_sq is not None:
        for to_sq in legal_targets_from(drag_from_sq):
            f, r = square_to_coords(to_sq)
            x, y = board_to_screen(f, r)
            center = (x + SQUARE_SIZE//2, y + SQUARE_SIZE//2)
            pygame.draw.circle(screen, HINT_COLOR, center, 10)

def draw_dragged_piece(mouse_pos):
    if dragging and drag_piece_surf is not None:
        mx, my = mouse_pos
        screen.blit(drag_piece_surf, (mx - drag_offset[0], my - drag_offset[1]))

def draw_eval_bar(score_cp: Optional[int], mate_in: Optional[int]):
    # Background
    x = BOARD_MARGIN
    y = BOARD_MARGIN
    w = EVAL_BAR_WIDTH
    h = BOARD_SIZE_PX
    pygame.draw.rect(screen, (50,50,50), (x, y, w, h))
    # Map score to 0..1 (white advantage ↑)
    if mate_in is not None:
        # clamp mate visualization: high confidence
        v = 1.0 if mate_in > 0 else 0.0
    elif score_cp is None:
        v = 0.5
    else:
        # logistic-ish mapping
        v = 1 / (1 + math.exp(-score_cp / 200.0))
    fill_h = int(v * h)
    pygame.draw.rect(screen, (230,230,230), (x, y, w, fill_h))
    pygame.draw.rect(screen, (20,20,20), (x, y + fill_h, w, h - fill_h))
    # Tick + text
    txt = " M#" + str(abs(mate_in)) if mate_in is not None else f" {score_cp/100:.1f}"
    label = font_small.render(txt, True, (255,255,255))
    screen.blit(label, (x - 2, y + h + 4))

def analyze_position(time_sec=ANALYSIS_TIME_SEC) -> Tuple[Optional[int], Optional[int], Optional[chess.Move]]:
    if not engine_ok or engine is None or board.is_game_over():
        return None, None, None
    try:
        limit = chess.engine.Limit(time=time_sec)
        info = engine.analyse(board, limit)
        score = info["score"].pov(chess.WHITE)
        mate = score.mate()
        cp = None if mate is not None else score.score()
        pv = info.get("pv", [])
        best = pv[0] if pv else None
        return cp, mate, best
    except Exception:
        return None, None, None

def uci_play(time_sec=ENGINE_MOVE_TIME) -> Optional[chess.Move]:
    if not engine_ok or engine is None or board.is_game_over():
        return None
    try:
        result = engine.play(board, chess.engine.Limit(time=time_sec))
        return result.move
    except Exception:
        return None

############################
# ====== UI BUTTONS =======
############################
def button_rects():
    left = BOARD_MARGIN + EVAL_BAR_WIDTH + BOARD_SIZE_PX + 20
    top = BOARD_MARGIN
    rects = []
    labels = ["Hint", "Engine Move", "Undo", "Redo", "Flip"]
    for i, name in enumerate(labels):
        y = top + i * (BUTTON_HEIGHT + BUTTON_GAP)
        rects.append((name, pygame.Rect(left, y, RIGHT_PANEL_WIDTH - 40, BUTTON_HEIGHT)))
    return rects

def draw_buttons():
    for name, rect in button_rects():
        pygame.draw.rect(screen, (60,60,60), rect, border_radius=8)
        pygame.draw.rect(screen, (110,110,110), rect, width=2, border_radius=8)
        label = font_medium.render(name, True, (255,255,255))
        screen.blit(label, (rect.centerx - label.get_width()//2,
                            rect.centery - label.get_height()//2))

def handle_button_click(pos):
    global hint_move, last_move, flip_board
    for name, rect in button_rects():
        if rect.collidepoint(pos):
            if name == "Hint":
                _, _, best = analyze_position(HINT_TIME_SEC)
                hint_move = best
            elif name == "Engine Move":
                mv = uci_play(ENGINE_MOVE_TIME)
                if mv:
                    push_move(mv)
                    hint_move = None
            elif name == "Undo":
                undo()
            elif name == "Redo":
                redo()
            elif name == "Flip":
                flip_board = not flip_board

############################
# ====== MOVE HELPERS =====
############################
def push_move(move: chess.Move):
    global last_move
    undo_stack.append(move)
    board.push(move)
    last_move = move
    redo_stack.clear()

def undo():
    global last_move
    if board.move_stack:
        mv = board.pop()
        redo_stack.append(mv)
        last_move = board.peek() if board.move_stack else None

def redo():
    global last_move
    if redo_stack:
        mv = redo_stack.pop()
        board.push(mv)
        undo_stack.append(mv)
        last_move = mv

############################
# ====== MAIN LOOP ========
############################
def main():
    global dragging, drag_from_sq, drag_piece_surf, drag_offset, hint_move

    if not engine_ok:
        print("Engine error:", engine_err, file=sys.stderr)

    running = True
    eval_cp, eval_mate, _ = analyze_position(0.01)

    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Buttons first
                for _, rect in button_rects():
                    if rect.collidepoint(event.pos):
                        handle_button_click(event.pos)
                        break
                else:
                    # Board drag start
                    sq = screen_to_board(*event.pos)
                    if sq is not None and board.piece_at(sq) and board.piece_at(sq).color == board.turn:
                        dragging = True
                        drag_from_sq = sq
                        drag_piece_surf = piece_to_surface(board.piece_at(sq))
                        mx, my = event.pos
                        # center grip
                        drag_offset = (SQUARE_SIZE//2, SQUARE_SIZE//2)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging and drag_from_sq is not None:
                    target_sq = screen_to_board(*event.pos)
                    legal_targets = legal_targets_from(drag_from_sq)
                    if target_sq is not None and target_sq in legal_targets:
                        promo = None
                        # Promotion auto-queen for simplicity (hold Shift to underpromote to knight)
                        if chess.square_rank(target_sq) in (0, 7) and board.piece_at(drag_from_sq).piece_type == chess.PAWN:
                            promo = chess.KNIGHT if pygame.key.get_mods() & pygame.KMOD_SHIFT else chess.QUEEN
                        move = chess.Move(drag_from_sq, target_sq, promotion=promo)
                        if move in board.legal_moves:
                            push_move(move)
                            hint_move = None
                    # reset drag
                dragging = False
                drag_from_sq = None
                drag_piece_surf = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    undo()
                elif event.key == pygame.K_r:
                    redo()

        # Passive evaluation when idle
        if engine_ok and not dragging and not board.is_game_over():
            # light background analysis
            cp, mate, best = analyze_position(ANALYSIS_TIME_SEC)
            if cp is not None or mate is not None:
                eval_cp, eval_mate = cp, mate
            # keep last hint if any
        else:
            cp, mate = None, None

        # DRAW
        screen.fill((25, 25, 28))
        draw_board()

        # Draw hint arrow
        if hint_move:
            f1, r1 = square_to_coords(hint_move.from_square)
            f2, r2 = square_to_coords(hint_move.to_square)
            x1, y1 = board_to_screen(f1, r1)
            x2, y2 = board_to_screen(f2, r2)
            start = (x1 + SQUARE_SIZE//2, y1 + SQUARE_SIZE//2)
            end   = (x2 + SQUARE_SIZE//2, y2 + SQUARE_SIZE//2)
            pygame.draw.line(screen, (70, 170, 255), start, end, 6)
            # arrow head
            ang = math.atan2(end[1]-start[1], end[0]-start[0])
            ah  = 14
            left = (end[0] - ah*math.cos(ang - math.pi/6), end[1] - ah*math.sin(ang - math.pi/6))
            right= (end[0] - ah*math.cos(ang + math.pi/6), end[1] - ah*math.sin(ang + math.pi/6))
            pygame.draw.polygon(screen, (70,170,255), [end, left, right])

        draw_dragged_piece(mouse_pos)
        draw_eval_bar(eval_cp, eval_mate)
        draw_buttons()

        # Status text
        status = "White to move" if board.turn == chess.WHITE else "Black to move"
        if board.is_game_over():
            if board.is_checkmate():
                status = "Checkmate"
            elif board.is_stalemate():
                status = "Stalemate"
            else:
                status = "Game over"
        status_text = font_large.render(status, True, (255,255,255))
        screen.blit(status_text, (BOARD_MARGIN + EVAL_BAR_WIDTH, BOARD_MARGIN + BOARD_SIZE_PX + 8))

        # Engine status
        eng = "Engine: OK" if engine_ok else f"Engine error: {engine_err}"
        eng_text = font_small.render(eng, True, (200,200,200))
        screen.blit(eng_text, (BOARD_MARGIN + EVAL_BAR_WIDTH, BOARD_MARGIN + BOARD_SIZE_PX + 8 + status_text.get_height()))

        pygame.display.flip()

    if engine:
        try:
            engine.quit()
        except Exception:
            pass
    pygame.quit()

if __name__ == "__main__":
    main()
