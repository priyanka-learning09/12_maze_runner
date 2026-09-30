import pygame
from game.maze import CELL

SPEED = 3
WALL_WIDTH = 3


class Player:
    def __init__(self, r, c):
        self.r = r
        self.c = c

        x = c * CELL + CELL // 2
        y = r * CELL + CELL // 2

        self.rect = pygame.Rect(x - 10, y - 10, 20, 20)
        self.color = (60, 120, 220)

    def move(self, keys, walls, rows, cols):
        dx, dy = 0, 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = SPEED

        # Horizontal movement
        new_rect = self.rect.move(dx, 0)

        if not self._hits_wall(new_rect, walls, rows, cols):
            self.rect = new_rect

        # Vertical movement
        new_rect = self.rect.move(0, dy)

        if not self._hits_wall(new_rect, walls, rows, cols):
            self.rect = new_rect

        # Update current cell
        self.r = max(0, min(rows - 1, self.rect.centery // CELL))
        self.c = max(0, min(cols - 1, self.rect.centerx // CELL))

    def _hits_wall(self, rect, walls, rows, cols):

        # Maze boundaries
        if rect.left < 0 or rect.right > cols * CELL:
            return True

        if rect.top < 0 or rect.bottom > rows * CELL:
            return True

        # Check walls of every cell
        for r in range(rows):
            for c in range(cols):

                x = c * CELL
                y = r * CELL
                cell_walls = walls[r][c]

                # TOP
                if cell_walls[0]:
                    wall_rect = pygame.Rect(
                        x,
                        y - WALL_WIDTH // 2,
                        CELL,
                        WALL_WIDTH
                    )

                    if rect.colliderect(wall_rect):
                        return True

                # BOTTOM
                if cell_walls[1]:
                    wall_rect = pygame.Rect(
                        x,
                        y + CELL - WALL_WIDTH // 2,
                        CELL,
                        WALL_WIDTH
                    )

                    if rect.colliderect(wall_rect):
                        return True

                # RIGHT
                if cell_walls[2]:
                    wall_rect = pygame.Rect(
                        x + CELL - WALL_WIDTH // 2,
                        y,
                        WALL_WIDTH,
                        CELL
                    )

                    if rect.colliderect(wall_rect):
                        return True

                # LEFT
                if cell_walls[3]:
                    wall_rect = pygame.Rect(
                        x - WALL_WIDTH // 2,
                        y,
                        WALL_WIDTH,
                        CELL
                    )

                    if rect.colliderect(wall_rect):
                        return True

        return False

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)