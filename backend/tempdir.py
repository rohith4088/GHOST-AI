import os
from git import Repo # type: ignore

def clone_github_repo(repo_url, folder_name="temp_repo"):
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    try:
        # Clone the repository into the specified folder
        print(f"Cloning into directory: {folder_name}")
        Repo.clone_from(repo_url, folder_name)
        print("Repository files:")
        for root, dirs, files in os.walk(folder_name):
            for file in files:
                print(os.path.join(root, file))

        # Return the folder name for further processing
        return folder_name

    except Exception as e:
        print(f"Error cloning repository: {e}")
        return None


if __name__ == "__main__":
    repo_url = input("Enter the GitHub repository URL: ")
    clone_github_repo(repo_url, folder_name="temp_repo")