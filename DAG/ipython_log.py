# IPython log file
from picklemanager import PickleManager
pm = PickleManager()
class dummy:
    def __init__(self, id = None):
        if id is None:
            self.id = 1
        self.id = id

pm.load_variables_to_workspace(gdict = globals())
