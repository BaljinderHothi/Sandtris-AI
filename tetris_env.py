import gym
from gym import spaces
import numpy as np
import pygame
import random
from sandtris import Tetris  # Ensure sandtris.py is in the same directory
import os

colors = [
    (0, 0, 0),
    (120, 37, 179),
    (100, 179, 179),
    (80, 34, 22),
    (80, 134, 22),
    (180, 34, 22),
    (180, 34, 122),
]

class TetrisEnv(gym.Env):
    """
    Custom Environment for Tetris game compatible with OpenAI Gym
    """
    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self):
        super(TetrisEnv, self).__init__()

        # Define action space: 0=left, 1=right, 2=rotate, 3=drop, 4=noop
        self.action_space = spaces.Discrete(5)

        # Observation space: 2D grid representing the game board
        self.height = 20
        self.width = 10
        self.observation_space = spaces.Box(low=0, high=6, 
                                            shape=(self.height, self.width), dtype=np.int32)

        # Initialize the game
        self.game = Tetris(self.height, self.width)

        # Setup for rendering
        self.screen = None
        self.zoom = 20
        self.x = 100
        self.y = 60

    def reset(self):
        """
        Reset the game to initial state
        """
        self.game = Tetris(self.height, self.width)
        self.game.new_figure()
        return self._get_obs()

    def step(self, action):
        """
        Execute one time step within the environment
        """
        done = False
        reward = 0

        # Apply action
        if action == 0:
            self.game.go_side(-1)  # Move left
        elif action == 1:
            self.game.go_side(1)   # Move right
        elif action == 2:
            self.game.rotate()     # Rotate
        elif action == 3:
            self.game.go_space()   # Drop
        elif action == 4:
            pass  # No operation

        # Move the piece down automatically
        self.game.go_down()

        # Calculate reward
        lines_cleared = self.game.score  # Assuming score increments with lines cleared
        reward += lines_cleared * 10

        # Additional reward shaping
        aggregate_height = self.calculate_aggregate_height()
        holes = self.calculate_holes()
        bumpiness = self.calculate_bumpiness()

        reward -= (aggregate_height * 0.5 + holes * 0.7 + bumpiness * 0.3)

        if self.game.state == "gameover":
            done = True
            reward -= 10  # Penalty for losing

        return self._get_obs(), reward, done, {}

    def _get_obs(self):
        """
        Get the current state of the game as an observation
        """
        return np.array(self.game.field)

    def render(self, mode='human'):
        """
        Render the game state as an RGB array or display it
        """
        if mode == 'rgb_array':
            if self.screen is None:
                pygame.init()
                size = (self.x * 2 + self.zoom * self.width, self.y * 2 + self.zoom * self.height)
                self.screen = pygame.Surface(size)

            self.screen.fill((173, 216, 230))  # WHITE background

            # Draw the game field
            for i in range(self.game.height):
                for j in range(self.game.width):
                    rect = pygame.Rect(self.x + self.zoom * j, self.y + self.zoom * i, self.zoom, self.zoom)
                    pygame.draw.rect(self.screen, (128, 128, 128), rect, 1)  # Grid lines
                    if self.game.field[i][j] > 0:
                        pygame.draw.rect(self.screen, 
                                         colors[self.game.field[i][j]],
                                         rect.inflate(-2, -2))

            # Draw the current figure
            if self.game.figure is not None:
                for i in range(4):
                    for j in range(4):
                        p = i * 4 + j
                        if p in self.game.figure.image():
                            rect = pygame.Rect(self.x + self.zoom * (j + self.game.figure.x),
                                               self.y + self.zoom * (i + self.game.figure.y),
                                               self.zoom, self.zoom)
                            pygame.draw.rect(self.screen, 
                                             colors[self.game.figure.color],
                                             rect.inflate(-2, -2))

            # Convert Pygame surface to RGB array
            return pygame.surfarray.array3d(self.screen)

        elif mode == 'human':
            if self.screen is None:
                pygame.init()
                size = (self.x * 2 + self.zoom * self.width, self.y * 2 + self.zoom * self.height)
                self.screen = pygame.display.set_mode(size)
                pygame.display.set_caption("Tetris RL")

            self.screen.fill((173, 216, 230))  # WHITE background

            # Draw the game field
            for i in range(self.game.height):
                for j in range(self.game.width):
                    rect = pygame.Rect(self.x + self.zoom * j, self.y + self.zoom * i, self.zoom, self.zoom)
                    pygame.draw.rect(self.screen, (128, 128, 128), rect, 1)  # Grid lines
                    if self.game.field[i][j] > 0:
                        pygame.draw.rect(self.screen, 
                                         colors[self.game.field[i][j]],
                                         rect.inflate(-2, -2))

            # Draw the current figure
            if self.game.figure is not None:
                for i in range(4):
                    for j in range(4):
                        p = i * 4 + j
                        if p in self.game.figure.image():
                            rect = pygame.Rect(self.x + self.zoom * (j + self.game.figure.x),
                                               self.y + self.zoom * (i + self.game.figure.y),
                                               self.zoom, self.zoom)
                            pygame.draw.rect(self.screen, 
                                             colors[self.game.figure.color],
                                             rect.inflate(-2, -2))

            pygame.display.flip()

    def close(self):
        """
        Clean up resources
        """
        if self.screen is not None:
            pygame.display.quit()
        pygame.quit()

    # Reward shaping helper functions
    def calculate_aggregate_height(self):
        heights = [0 for _ in range(self.width)]
        for j in range(self.width):
            for i in range(self.height):
                if self.game.field[i][j] != 0:
                    heights[j] = self.height - i
                    break
        return sum(heights)

    def calculate_holes(self):
        holes = 0
        for j in range(self.width):
            block_found = False
            for i in range(self.height):
                if self.game.field[i][j] != 0:
                    block_found = True
                elif block_found and self.game.field[i][j] == 0:
                    holes += 1
        return holes

    def calculate_bumpiness(self):
        heights = [0 for _ in range(self.width)]
        for j in range(self.width):
            for i in range(self.height):
                if self.game.field[i][j] != 0:
                    heights[j] = self.height - i
                    break
        bumpiness = 0
        for j in range(self.width - 1):
            bumpiness += abs(heights[j] - heights[j + 1])
        return bumpiness
