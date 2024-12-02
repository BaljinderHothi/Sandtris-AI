import gym
from stable_baselines3 import DQN
from tetris_env import TetrisEnv
import pygame
import time

def main():
    # Create the environment
    env = TetrisEnv()

    # Load the trained model
    model = DQN.load("models/dqn_tetris")

    # Number of evaluation episodes
    episodes = 5

    for ep in range(1, episodes + 1):
        obs = env.reset()
        done = False
        total_reward = 0
        while not done:
            # Render the game (optional)
            env.render(mode='human')

            # Predict the action using the trained model
            action, _states = model.predict(obs, deterministic=True)

            # Take the action in the environment
            obs, reward, done, info = env.step(action)

            total_reward += reward

            # Control the rendering speed
            pygame.time.wait(100)  # Wait 100 ms between steps

        print(f"Episode {ep}: Total Reward = {total_reward}")

    env.close()

if __name__ == "__main__":
    main()
