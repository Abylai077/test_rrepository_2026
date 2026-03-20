import os

# Create directory
os.mkdir("test_dir")

# Create nested directories
os.makedirs("parent_dir/child_dir", exist_ok=True)

# Current directory
print("Current directory:", os.getcwd())

# List files and folders
print("Directory contents:", os.listdir())