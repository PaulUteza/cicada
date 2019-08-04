from abc import ABC


class ConvertToNWB(ABC):
    """NWB file object class"""
    def __init__(self, nwb_file):
        """
        Args:
            nwb_file (NWB.file): NWB file object
        """
        self.nwb_file = nwb_file

    def convert(self, **kwargs):
        """Convert the data and add to the nwb_file

        Args:
            **kwargs: arbitrary arguments
        """
        pass
