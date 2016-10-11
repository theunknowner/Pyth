import sys

PROJECT_PATH = "/home/jason/git/Pyth/Pyth/"
THRESHOLDS_PATH = "/home/jason/git/Thresholds/Thresholds/"

RESOURCE_PATHS = [PROJECT_PATH,
                  THRESHOLDS_PATH
                  ]



def import_paths():
    for path in RESOURCE_PATHS:
        if not path in sys.path:
            sys.path.append(path)


#auto run when module is imported
import_paths()