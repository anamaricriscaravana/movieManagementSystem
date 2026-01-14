import os
import shutil

def save_profile_image(source_path, user_id):
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    
    extension = os.path.splitext(source_path)[1]
    dest = os.path.join("uploads", f"profile_{user_id}{extension}")
    
    shutil.copy(source_path, dest)
    return dest