import gym
from gym import spaces
import numpy as np
import pygame
import random
from sandtris import Tetris  

class TetrisEnv(gym.Env):
    """
    Custom Environment for Tetris game compatible with OpenAI Gym
    """
    metadata = {'render.modes': ['human']}
    
    def __init__(self):
        super(TetrisEnv, self).__init__()
        
        # Define action space: 0=left, 1=right, 2=rotate, 3=drop, 4=noop
        self.action_space = spaces.Discrete(5)
        
        # Observation space: 2D grid representing the game board
        # Assuming colors are integers from 0 (empty) to 6 (filled)
        self.height = 20
        self.width = 10
        self.observation_space = spaces.Box(low=0, high=6, 
                                            shape=(self.height, self.width), dtype=np.int32)
        
     
        self.game = Tetris(self.height, self.width)
        
    def reset(self):
        """
        
        """
        self.game = Tetris(self.height, self.width)
        self.game.new_figure()
        return self._get_obs()
    
    def step(self, action):
        """
      
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
            pass  
        
       
        self.game.go_down()
        
        # Calculate reward
        reward += self.game.score  
        
        if self.game.state == "gameover":
            done = True
            reward -= 10  
        
        return self._get_obs(), reward, done, {}
    
    def _get_obs(self):
        """
        
        """
        return np.array(self.game.field)
    
    def render(self, mode='human'):
        """
   
        """
       
        if not pygame.get_init():
            pygame.init()
            self.game.x = 100
            self.game.y = 60
            self.game.zoom = 20
            size = (400, 500)
            self.screen = pygame.display.set_mode(size)
            pygame.display.set_caption("Tetris RL")
        
       
        self.screen.fill((173, 216, 230))  # WHITE
        
        
        for i in range(self.game.height):
            for j in range(self.game.width):
                pygame.draw.rect(self.screen, (128, 128, 128), 
                                 [self.game.x + self.game.zoom * j, 
                                  self.game.y + self.game.zoom * i, 
                                  self.game.zoom, self.game.zoom], 1)
                if self.game.field[i][j] > 0:
                    pygame.draw.rect(self.screen, 
                                     colors[self.game.field[i][j]],
                                     [self.game.x + self.game.zoom * j + 1,
                                      self.game.y + self.game.zoom * i + 1,
                                      self.game.zoom - 2, self.game.zoom - 1])
        
        
        if self.game.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in self.game.figure.image():
                        pygame.draw.rect(self.screen, colors[self.game.figure.color],
                                         [self.game.x + self.game.zoom * (j + self.game.figure.x) + 1,
                                          self.game.y + self.game.zoom * (i + self.game.figure.y) + 1,
                                          self.game.zoom - 2, self.game.zoom - 2])
        
     
        pygame.display.flip()
    
    def close(self):
        """
       
        """
        pygame.quit()

# redefining here but can import
colors = [
    (0, 0, 0),
    (120, 37, 179),
    (100, 179, 179),
    (80, 34, 22),
    (80, 134, 22),
    (180, 34, 22),
    (180, 34, 122),
]
