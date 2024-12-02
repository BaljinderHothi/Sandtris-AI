import gym
from stable_baselines3 import DQN
from stable_baselines3.common.evaluation import evaluate_policy
from tetris_env import TetrisEnv
from callbacks import SaveFramesCallback
import os

def main():
    # Create the environment
    env = TetrisEnv()

    # Initialize the RL model (DQN)
    model = DQN('MlpPolicy', env, verbose=1, 
                learning_rate=1e-3, 
                buffer_size=50000, 
                learning_starts=1000, 
                batch_size=32, 
                gamma=0.99, 
                target_update_interval=1000, 
                exploration_fraction=0.1, 
                exploration_final_eps=0.02)

    # Define the number of training timesteps
    TIMESTEPS = 100000  # Adjust as needed

    # Initialize the callback
    callback = SaveFramesCallback(save_freq=5000, save_path="models/frames", verbose=1)

    # Train the model with the callback
    model.learn(total_timesteps=TIMESTEPS, callback=callback)

    # Save the model
    os.makedirs("models", exist_ok=True)
    model.save("models/dqn_tetris")
    print("Model saved to models/dqn_tetris.zip")

    # Evaluate the trained agent
    mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=10)
    print(f"Mean Reward: {mean_reward} +/- {std_reward}")

if __name__ == "__main__":
    main()
