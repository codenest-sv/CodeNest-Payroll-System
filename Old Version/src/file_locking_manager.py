# file_locking_manager.py
import shutil
import os
from datetime import datetime

class FileLockingManager:
    BACKUP_FOLDER = os.path.join("data", "backups")

    def __init__(self):
        os.makedirs(self.BACKUP_FOLDER, exist_ok=True)

    def create_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.BACKUP_FOLDER, f"backup_{timestamp}.zip")
        shutil.make_archive(backup_file.replace('.zip', ''), 'zip', "data")
        print(f"🗂️ Backup created: {backup_file}")
