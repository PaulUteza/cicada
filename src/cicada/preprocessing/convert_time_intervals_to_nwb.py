from convert_to_nwb import ConvertToNWB
import hdf5storage
import numpy as np


class ConvertTimeIntervalsToNWB(ConvertToNWB):
    def __init__(self, nwb_file):
        ConvertToNWB.__init__(self, nwb_file)

    def convert(self, **kwargs):
        """Convert the data and add it to the nwb_file

        Args:
            **kwargs: arbitrary arguments
        """
        super().convert(**kwargs)

        if "name" not in kwargs:
            raise Exception(f"'name' argument should be pass to convert "
                            f"function in class {self.__class__.__name__}")

        name = kwargs["name"]

        if "description" not in kwargs:
            raise Exception(f"'description' argument should be pass to convert "
                            f"function in class {self.__class__.__name__}")

        description = kwargs["description"]

        if "intervals_data" not in kwargs:
            raise Exception(f"'intervals_data' argument should be pass to convert "
                            f"function in class {self.__class__.__name__}")

        intervals_data = kwargs["intervals_data"]

        print(f"In ConvertTimeIntervalsToNWB {name} -> {description} -> {intervals_data}")

        # TODO: find a way to get the imaging_rate, to convert the intervals frames to seconds
        #  and get frames_to_add in order to put the correct time
        self.nwb_file.create_time_intervals(name=name, description=description)
