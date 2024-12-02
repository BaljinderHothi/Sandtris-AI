import os
from stable_baselines3.common.callbacks import BaseCallback
import imageio
import numpy as np

class SaveFramesCallback(BaseCallback):
    """
    Callback for saving frames during training.
    """
    def __init__(self, save_freq, save_path, verbose=0):
        super(SaveFramesCallback, self).__init__(verbose)
        self.save_freq = save_freq
        self.save_path = save_path
        self.frames = []
        os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        if self.num_timesteps % self.save_freq == 0:
            # Render the environment and get the RGB array
            frame = self.training_env.render(mode='rgb_array')
            self.frames.append(frame)
            if self.verbose > 0:
                print(f"Saved frame at timestep {self.num_timesteps}")
        return True

    def _on_training_end(self) -> None:
        # Save the frames as a GIF
        if self.frames:
            gif_path = os.path.join(self.save_path, "training.gif")
            imageio.mimsave(gif_path, self.frames, fps=10)
            if self.verbose > 0:
                print(f"Saved training GIF to {gif_path}")
