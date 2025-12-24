import os
import shutil

def flatten_directory(root_dir):
    """
    Move all files from subfolders into root_dir, then delete empty folders.
    """

    root_dir = os.path.abspath(root_dir)

    for current_path, folders, files in os.walk(root_dir, topdown=False):
        # Skip the root folder itself
        if current_path == root_dir:
            continue

        for file in files:
            src = os.path.join(current_path, file)
            dst = os.path.join(root_dir, file)

            # If filename already exists, create a unique name
            if os.path.exists(dst):
                base, ext = os.path.splitext(file)
                counter = 1
                while True:
                    new_name = f"{base}_{counter}{ext}"
                    dst = os.path.join(root_dir, new_name)
                    if not os.path.exists(dst):
                        break
                    counter += 1

            # Move file
            shutil.move(src, dst)

        # After moving files, remove empty folder
        try:
            os.rmdir(current_path)
        except OSError:
            pass  # Directory not empty or can't delete

    print("✔ All files moved and folders cleaned up.")

if __name__ == "__main__":
    target_directory = r"E:\experiment_1"
    flatten_directory(target_directory)