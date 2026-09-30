import pygame
import time
import json
import os
from collections import deque

from game.maze import generate_maze, CELL
from game.player import Player


FPS = 60

BG = (240, 235, 220)
WALL_COLOR = (40, 40, 60)
EXIT_COLOR = (80, 200, 80)

# Difficulty settings
DIFFICULTIES = {
    "Easy": (10, 8),
    "Medium": (15, 13),
    "Hard": (20, 18)
}

DEFAULT_DIFFICULTY = "Medium"

LEADERBOARD_FILE = "leaderboard.json"


class GameEngine:

    def __init__(self):

        pygame.init()

        self.difficulty_names = list(DIFFICULTIES.keys())
        self.difficulty_index = self.difficulty_names.index(
            DEFAULT_DIFFICULTY
        )

        self.font = pygame.font.SysFont("monospace", 20)
        self.big_font = pygame.font.SysFont(
            "monospace",
            36,
            bold=True
        )

        self.clock = pygame.time.Clock()

        self.screen = None

        self.load_leaderboard()

        self.reset()

    # ---------------------------------------------------------
    # Difficulty
    # ---------------------------------------------------------

    @property
    def difficulty(self):
        return self.difficulty_names[self.difficulty_index]

    @property
    def cols(self):
        return DIFFICULTIES[self.difficulty][0]

    @property
    def rows(self):
        return DIFFICULTIES[self.difficulty][1]

    def create_window(self):

        width = self.cols * CELL
        height = self.rows * CELL + 80

        self.screen = pygame.display.set_mode(
            (width, height)
        )

        pygame.display.set_caption(
            f"Maze Runner - {self.difficulty}"
        )

    # ---------------------------------------------------------
    # Reset / New Maze
    # ---------------------------------------------------------

    def reset(self):

        self.create_window()

        self.walls = generate_maze(
            self.cols,
            self.rows
        )

        self.player = Player(0, 0)

        self.exit_rect = pygame.Rect(
            (self.cols - 1) * CELL + 5,
            (self.rows - 1) * CELL + 5,
            CELL - 10,
            CELL - 10
        )

        self.start_time = time.time()

        self.elapsed = 0

        self.won = False

        # Shortest path hint
        self.show_hint = False
        self.shortest_path = []

        # Leaderboard screen
        self.show_leaderboard = False

    # ---------------------------------------------------------
    # Leaderboard
    # ---------------------------------------------------------

    def load_leaderboard(self):

        if os.path.exists(LEADERBOARD_FILE):

            try:
                with open(
                    LEADERBOARD_FILE,
                    "r"
                ) as file:

                    self.leaderboard = json.load(file)

            except (json.JSONDecodeError, OSError):

                self.leaderboard = {}

        else:
            self.leaderboard = {}

    def save_leaderboard(self):

        with open(
            LEADERBOARD_FILE,
            "w"
        ) as file:

            json.dump(
                self.leaderboard,
                file,
                indent=4
            )

    def add_score(self):

        difficulty = self.difficulty

        if difficulty not in self.leaderboard:
            self.leaderboard[difficulty] = []

        self.leaderboard[difficulty].append(
            round(self.elapsed, 2)
        )

        # Sort fastest first
        self.leaderboard[difficulty].sort()

        # Keep only top 5
        self.leaderboard[difficulty] = (
            self.leaderboard[difficulty][:5]
        )

        self.save_leaderboard()

    # ---------------------------------------------------------
    # Shortest Path - BFS
    # ---------------------------------------------------------

    def get_shortest_path(self):

        start = (
            self.player.r,
            self.player.c
        )

        target = (
            self.rows - 1,
            self.cols - 1
        )

        queue = deque([start])

        parent = {
            start: None
        }

        while queue:

            current = queue.popleft()

            if current == target:
                break

            r, c = current

            # N, S, E, W
            directions = [
                (-1, 0, 0, 1),  # North
                (1, 0, 1, 0),   # South
                (0, 1, 2, 3),   # East
                (0, -1, 3, 2)   # West
            ]

            for dr, dc, wall_dir, opposite in directions:

                nr = r + dr
                nc = c + dc

                if not (
                    0 <= nr < self.rows
                    and
                    0 <= nc < self.cols
                ):
                    continue

                # There is a wall between cells
                if self.walls[r][c][wall_dir]:
                    continue

                neighbor = (nr, nc)

                if neighbor not in parent:

                    parent[neighbor] = current

                    queue.append(neighbor)

        # No path found
        if target not in parent:
            return []

        # Reconstruct path
        path = []

        current = target

        while current is not None:

            path.append(current)

            current = parent[current]

        path.reverse()

        return path

    # ---------------------------------------------------------
    # Event Handling
    # ---------------------------------------------------------

    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:

                # New maze
                if event.key == pygame.K_r:

                    self.reset()

                # Shortest path hint
                elif event.key == pygame.K_h:

                    self.show_hint = not self.show_hint

                    if self.show_hint:

                        self.shortest_path = (
                            self.get_shortest_path()
                        )

                # Change difficulty
                elif event.key == pygame.K_1:

                    self.difficulty_index = 0
                    self.reset()

                elif event.key == pygame.K_2:

                    self.difficulty_index = 1
                    self.reset()

                elif event.key == pygame.K_3:

                    self.difficulty_index = 2
                    self.reset()

        return True

    # ---------------------------------------------------------
    # Update
    # ---------------------------------------------------------

    def update(self):

        if self.won:
            return

        keys = pygame.key.get_pressed()

        self.player.move(
            keys,
            self.walls,
            self.rows,
            self.cols
        )

        self.elapsed = (
            time.time() - self.start_time
        )

        if self.player.rect.colliderect(
            self.exit_rect
        ):

            self.won = True

            self.add_score()

            self.show_leaderboard = True

    # ---------------------------------------------------------
    # Draw Maze
    # ---------------------------------------------------------

    def draw_maze(self):

        wall_w = 3

        for r in range(self.rows):

            for c in range(self.cols):

                x = c * CELL
                y = r * CELL

                w = self.walls[r][c]

                # TOP
                if w[0]:

                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y),
                        (x + CELL, y),
                        wall_w
                    )

                # BOTTOM
                if w[1]:

                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y + CELL),
                        (x + CELL, y + CELL),
                        wall_w
                    )

                # RIGHT
                if w[2]:

                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x + CELL, y),
                        (x + CELL, y + CELL),
                        wall_w
                    )

                # LEFT
                if w[3]:

                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y),
                        (x, y + CELL),
                        wall_w
                    )

    # ---------------------------------------------------------
    # Fog of War
    # ---------------------------------------------------------

    def draw_fog(self):

        # Radius = 3 cells
        radius = 3

        player_r = self.player.r
        player_c = self.player.c

        fog = pygame.Surface(
            (
                self.cols * CELL,
                self.rows * CELL
            ),
            pygame.SRCALPHA
        )

        # Entire maze is dark
        fog.fill((0, 0, 0, 190))

        for r in range(self.rows):

            for c in range(self.cols):

                distance = max(
                    abs(r - player_r),
                    abs(c - player_c)
                )

                if distance <= radius:

                    visible_rect = pygame.Rect(
                        c * CELL,
                        r * CELL,
                        CELL,
                        CELL
                    )

                    fog.fill(
                        (0, 0, 0, 0),
                        visible_rect
                    )

        self.screen.blit(fog, (0, 0))

    # ---------------------------------------------------------
    # Draw Shortest Path
    # ---------------------------------------------------------

    def draw_shortest_path(self):

        if not self.show_hint:
            return

        if not self.shortest_path:
            return

        for r, c in self.shortest_path:

            center_x = c * CELL + CELL // 2
            center_y = r * CELL + CELL // 2

            pygame.draw.circle(
                self.screen,
                (255, 180, 40),
                (center_x, center_y),
                5
            )

    # ---------------------------------------------------------
    # Draw Leaderboard
    # ---------------------------------------------------------

    def draw_leaderboard(self):

        if not self.show_leaderboard:
            return

        width = self.cols * CELL
        height = self.rows * CELL

        overlay = pygame.Surface(
            (width, height),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 210)
        )

        self.screen.blit(
            overlay,
            (0, 0)
        )

        title = self.big_font.render(
            "LEADERBOARD",
            True,
            (255, 220, 80)
        )

        self.screen.blit(
            title,
            (
                width // 2 - title.get_width() // 2,
                40
            )
        )

        scores = self.leaderboard.get(
            self.difficulty,
            []
        )

        difficulty_text = self.font.render(
            self.difficulty,
            True,
            (220, 220, 220)
        )

        self.screen.blit(
            difficulty_text,
            (
                width // 2 -
                difficulty_text.get_width() // 2,
                90
            )
        )

        for i, score in enumerate(scores):

            text = self.font.render(
                f"{i + 1}. {score:.2f}s",
                True,
                (240, 240, 240)
            )

            self.screen.blit(
                text,
                (
                    width // 2 -
                    text.get_width() // 2,
                    130 + i * 30
                )
            )

        hint = self.font.render(
            "Press R for a new maze",
            True,
            (180, 180, 180)
        )

        self.screen.blit(
            hint,
            (
                width // 2 -
                hint.get_width() // 2,
                height - 45
            )
        )

    # ---------------------------------------------------------
    # Draw Everything
    # ---------------------------------------------------------

    def draw(self):

        self.screen.fill(BG)

        # Maze
        self.draw_maze()

        # Shortest path
        self.draw_shortest_path()

        # Exit
        pygame.draw.rect(
            self.screen,
            EXIT_COLOR,
            self.exit_rect,
            border_radius=4
        )

        ex_label = self.font.render(
            "EXIT",
            True,
            (20, 80, 20)
        )

        self.screen.blit(
            ex_label,
            (
                self.exit_rect.x + 2,
                self.exit_rect.y + 4
            )
        )

        # Player
        self.player.draw(self.screen)

        # Fog of War
        self.draw_fog()

        # HUD
        hud = pygame.Rect(
            0,
            self.rows * CELL,
            self.cols * CELL,
            80
        )

        pygame.draw.rect(
            self.screen,
            (30, 30, 50),
            hud
        )

        time_text = self.font.render(
            f"Time: {self.elapsed:.1f}s",
            True,
            (220, 220, 220)
        )

        self.screen.blit(
            time_text,
            (10, self.rows * CELL + 10)
        )

        controls = self.font.render(
            "H: Hint   R: New Maze   1/2/3: Difficulty",
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            controls,
            (10, self.rows * CELL + 38)
        )

        difficulty_text = self.font.render(
            f"Difficulty: {self.difficulty}",
            True,
            (255, 220, 100)
        )

        self.screen.blit(
            difficulty_text,
            (
                self.cols * CELL -
                difficulty_text.get_width() - 10,
                self.rows * CELL + 10
            )
        )

        # Win message
        if self.won and not self.show_leaderboard:

            msg = self.big_font.render(
                f"Solved in {self.elapsed:.1f}s!",
                True,
                (80, 240, 80)
            )

            self.screen.blit(
                msg,
                (
                    self.cols * CELL // 2 -
                    msg.get_width() // 2,
                    self.rows * CELL // 2 - 30
                )
            )

        # Leaderboard
        if self.show_leaderboard:
            self.draw_leaderboard()

        pygame.display.flip()

    # ---------------------------------------------------------
    # Main Loop
    # ---------------------------------------------------------

    def run(self):

        running = True

        while running:

            running = self.handle_events()

            self.update()

            self.draw()

            self.clock.tick(FPS)

        pygame.quit()