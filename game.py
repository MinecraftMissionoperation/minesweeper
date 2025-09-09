import pygame, sys, random

pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 16, 16
MINES_COUNT = 40  # Default: Medium level; can change per difficulty

TILE_SIZE = WIDTH // COLS

# Colors
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
DARK_GRAY = (50, 50, 50)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
NUM_COLORS = [None, BLUE, GREEN, RED, (0,0,128), (128,0,0), (0,128,128), (0,0,0), (128,128,128)]

screen = pygame.display.set_mode((WIDTH, HEIGHT + 50))
pygame.display.set_caption("Minesweeper")

font = pygame.font.SysFont("arial", 18)
large_font = pygame.font.SysFont("arial", 28)

# Tile states
HIDDEN = 0
REVEALED = 1
FLAGGED = 2

def create_board(rows, cols, mines_count):
    board = [[0 for _ in range(cols)] for _ in range(rows)]
    mines = set()
    while len(mines) < mines_count:
        r, c = random.randint(0, rows-1), random.randint(0, cols-1)
        mines.add((r, c))
    for (r, c) in mines:
        board[r][c] = -1
    # Calculate adjacent counts
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == -1:
                continue
            count = 0
            for rr in range(max(0, r-1), min(rows, r+2)):
                for cc in range(max(0, c-1), min(cols, c+2)):
                    if board[rr][cc] == -1:
                        count += 1
            board[r][c] = count
    return board

def draw_board(board, state):
    for r in range(len(board)):
        for c in range(len(board[0])):
            x, y = c*TILE_SIZE, r*TILE_SIZE
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            if state[r][c] == REVEALED:
                pygame.draw.rect(screen, GRAY, rect)
                if board[r][c] == -1:
                    pygame.draw.circle(screen, BLACK, rect.center, TILE_SIZE // 3)
                elif board[r][c] > 0:
                    text = font.render(str(board[r][c]), True, NUM_COLORS[board[r][c]])
                    text_rect = text.get_rect(center=rect.center)
                    screen.blit(text, text_rect)
            elif state[r][c] == FLAGGED:
                pygame.draw.rect(screen, DARK_GRAY, rect)
                pygame.draw.polygon(screen, RED, [
                    (x+TILE_SIZE//4, y+TILE_SIZE//4*3),
                    (x+TILE_SIZE//2, y+TILE_SIZE//4),
                    (x+TILE_SIZE//2, y+TILE_SIZE//4*3)
                ])
            else:
                pygame.draw.rect(screen, DARK_GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

def adjacent_reveal(board, state, r, c):
    if not (0 <= r < len(board) and 0 <= c < len(board[0])):
        return
    if state[r][c] == REVEALED or state[r][c] == FLAGGED:
        return
    state[r][c] = REVEALED
    if board[r][c] == 0:
        for rr in range(max(0, r-1), min(len(board), r+2)):
            for cc in range(max(0, c-1), min(len(board[0]), c+2)):
                if rr == r and cc == c:
                    continue
                adjacent_reveal(board, state, rr, cc)

def check_win(board, state):
    for r in range(len(board)):
        for c in range(len(board[0])):
            if board[r][c] != -1 and state[r][c] != REVEALED:
                return False
    return True

def draw_text_center(text, y, color=BLACK):
    render = large_font.render(text, True, color)
    rect = render.get_rect(center=(WIDTH//2, y))
    screen.blit(render, rect)

def main():
    running = True
    board = None
    state = None
    game_over = False
    win = False

    def reset(level):
        nonlocal board, state, game_over, win, ROWS, COLS, MINES_COUNT, TILE_SIZE
        if level == "easy":
            ROWS, COLS, MINES_COUNT = 9, 9, 10
        elif level == "medium":
            ROWS, COLS, MINES_COUNT = 16, 16, 40
        else:
            ROWS, COLS, MINES_COUNT = 24, 24, 99
        TILE_SIZE = WIDTH // COLS
        board = create_board(ROWS, COLS, MINES_COUNT)
        state = [[HIDDEN for _ in range(COLS)] for _ in range(ROWS)]
        game_over = False
        win = False

    level = "medium"
    reset(level)

    # Level menu
    while True:
        screen.fill(WHITE)
        draw_text_center("Select Difficulty", HEIGHT//2-50)
        easy_text = font.render("1. Easy (9x9, 10 mines)", True, BLACK)
        medium_text = font.render("2. Medium (16x16, 40 mines)", True, BLACK)
        hard_text = font.render("3. Hard (24x24, 99 mines)", True, BLACK)
        screen.blit(easy_text, (WIDTH//2 - easy_text.get_width()//2, HEIGHT//2))
        screen.blit(medium_text, (WIDTH//2 - medium_text.get_width()//2, HEIGHT//2 + 30))
        screen.blit(hard_text, (WIDTH//2 - hard_text.get_width()//2, HEIGHT//2 + 60))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    level = "easy"
                    reset(level)
                    goto_game = True
                    break
                elif event.key == pygame.K_2:
                    level = "medium"
                    reset(level)
                    goto_game = True
                    break
                elif event.key == pygame.K_3:
                    level = "hard"
                    reset(level)
                    goto_game = True
                    break
        else:
            continue
        break

    # Game loop
    while running:
        screen.fill(WHITE)
        draw_board(board, state)
        # Display mine count left as flags
        flagged_count = sum(row.count(FLAGGED) for row in state)
        mines_left = MINES_COUNT - flagged_count
        flag_text = font.render(f"Mines Left: {mines_left}", True, BLACK)
        screen.blit(flag_text, (10, HEIGHT + 10))

        if game_over:
            draw_text_center("Game Over! Press R to Restart", HEIGHT + 25, RED)
        elif win:
            draw_text_center("You Win! Press R to Restart", HEIGHT + 25, GREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_over or win:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    reset(level)
                    game_over = False
                    win = False
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if y >= HEIGHT:  # Ignore clicks outside board
                    continue
                c = x // TILE_SIZE
                r = y // TILE_SIZE

                if event.button == 1:  # Left-click to reveal
                    if state[r][c] == HIDDEN:
                        if board[r][c] == -1:
                            # Reveal all mines
                            for rr in range(ROWS):
                                for cc in range(COLS):
                                    if board[rr][cc] == -1:
                                        state[rr][cc] = REVEALED
                            game_over = True
                        else:
                            adjacent_reveal(board, state, r, c)
                            if check_win(board, state):
                                win = True

                elif event.button == 3:  # Right-click to flag/unflag
                    if state[r][c] == HIDDEN:
                        state[r][c] = FLAGGED
                    elif state[r][c] == FLAGGED:
                        state[r][c] = HIDDEN

        pygame.display.flip()
        pygame.time.Clock().tick(30)

    pygame.quit()

main()
