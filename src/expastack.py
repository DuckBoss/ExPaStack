import sys
from .parameters import UserParameters

class PrimaryRunner:
    def __init__(self):
        print("ExPaStack Initialized.")
        if len(sys.argv) > 1:
            print("Additional command-line parameters detected.")
            params = UserParameters()
            for i, arg in enumerate(sys.argv):
                if arg in params.parameters:
                    print(f"Command-line parameter detected - {arg[2:]}")

