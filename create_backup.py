"""Create backup zip of the project"""
import shutil
import os
from datetime import datetime

backup_name = f'try_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
parent_dir = os.path.dirname(os.path.abspath('.'))
backup_path = os.path.join(parent_dir, backup_name)

shutil.make_archive(backup_path.replace('.zip', ''), 'zip', '.')
print(f'Backup created: {backup_path}')


