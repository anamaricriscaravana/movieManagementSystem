import os
import shutil

def save_profile_image(source_path, user_id):
    # Save a user's profile image to the local 'uploads' folder.
    # Ensure the 'uploads' directory exists
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    # Get the file extension from the source file (e.g., .jpg, .png)
    extension = os.path.splitext(source_path)[1]

    # Construct destination path using user_id for uniqueness
    dest = os.path.join("uploads", f"profile_{user_id}{extension}")
    
    # Copy the file to the destination
    shutil.copy(source_path, dest)
    return dest