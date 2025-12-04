# backup_manager.py
import os
import zipfile
from datetime import datetime

class BackupManager:
    BACKUP_DIR = os.path.join("data", "backups")

    def create_backup(self):
        os.makedirs(self.BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"backup_{timestamp}.zip"
        zip_path = os.path.join(self.BACKUP_DIR, zip_name)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for folder, _, files in os.walk("data"):
                for file in files:
                    file_path = os.path.join(folder, file)
                    zipf.write(file_path, os.path.relpath(file_path, "data"))

        print(f"💾 Backup saved as: {zip_path}")
