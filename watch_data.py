from PySide6.QtCore import QFileSystemWatcher
from PySide6.QtCore import QCoreApplication
import sys

def directory_changed(path):
    print('Directory Changed: %s' % path)

def file_changed(path):
    print('File Changed: %s' % path)

app = QCoreApplication(sys.argv)

paths = [
    '../../Jay/run_data/run_005591'
    ]

fs_watcher = QFileSystemWatcher(paths)
fs_watcher.directoryChanged.connect(directory_changed)
fs_watcher.fileChanged.connect(file_changed)

sys.exit(app.exec_())