import sys, os

def resource_path(filename):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS,"trigger_master_resources", filename)
    else:
        return filename