import shutil
import os

# check that folder exists
os.makedirs("destination", exist_ok=True)

# Move file
shutil.move("sample.txt", "destination/sample.txt")

print("File moved.")