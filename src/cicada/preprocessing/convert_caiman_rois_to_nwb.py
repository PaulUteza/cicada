from converttonwb import ConvertToNWB


class ConvertCaimanRoisToNWB(ConvertToNWB):

    """Class to convert ROIs data from Caiman to NWB"""

    def __init__(self, nwb_file):
        ConvertToNWB.__init__(self, nwb_file)