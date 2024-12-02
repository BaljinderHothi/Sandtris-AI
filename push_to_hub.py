from stable_baselines3 import DQN
from huggingface_hub import HfApi, HfFolder, Repository
import os

def main():
    # Define repository details
    repo_name = "dqn-tetris"
    model_path = "models/dqn_tetris.zip"
    model_dir = "models"

    # Load the trained model
    model = DQN.load(model_path)

    # Initialize Hugging Face API
    api = HfApi()
    user = api.whoami()["name"]

    # Create the repository if it doesn't exist
    try:
        api.create_repo(name=repo_name, repo_type="model", exist_ok=True)
        print(f"Repository '{repo_name}' created.")
    except Exception as e:
        print(f"Repository '{repo_name}' already exists or failed to create: {e}")

    # Clone the repository locally
    repo = Repository(local_dir=repo_name, clone_from=f"{user}/{repo_name}", use_auth_token=True)

    # Copy the model file into the repository directory
    os.makedirs(repo_name, exist_ok=True)
    os.rename(model_path, os.path.join(repo_name, "dqn_tetris.zip"))

    # Add and commit the model
    repo.git_add(auto_lfs_track=True)
    repo.git_commit("Add trained DQN Tetris model")
    repo.git_push()
    print(f"Model pushed to Hugging Face Hub at {user}/{repo_name}")

if __name__ == "__main__":
    main()
