from abc import ABC, abstractmethod, abstractproperty


class CicadaAnalysis(ABC):
    """
    An abstract class that should be inherit in order to create a specific analyse

    """
    def __init__(self, name, short_description, family_id=None, long_description=None,
                 data_to_analyse=None, data_format=None):
        """
        A list of
        :param name:
        :param short_description: short string that describe what the analysis is about
        used to be displayed in the GUI among other things
        :param family_id: family_id indicated to which family of analysis this class belongs. If None, then
        the analysis is a family in its own.
        :param long_description: string
        """
        super().__init__()
        # TODO: when the exploratory GUI will be built, think about passing in argument some sort of connector
        #  to the GUI in order to communicate with it and get the results displayed if needed
        self.short_description = short_description
        self.long_description = long_description
        self.family_id = family_id
        self.name = name
        self._data_to_analyse = data_to_analyse
        self._data_format = data_format

    # @abstractproperty
    # def data_to_analyse(self):
    #     pass
    #
    # @abstractproperty
    # def data_format(self):
    #     pass

    def set_data(self, data_to_analyse, data_format="nwb"):
        """
                A list of
                :param data_to_analyse: list of data_structure
                :param data_format: indicate the type of data structure. for NWB, NIX
        """
        if not isinstance(data_to_analyse, list):
            data_to_analyse = [data_to_analyse]
        self._data_to_analyse = data_to_analyse
        self._data_format = data_format

    @abstractmethod
    def check_data(self):
        """
        Check the data given one initiating the class and return True if the data given allows the analysis
        implemented, False otherwise.
        :return: a boolean
        """
        pass

    def get_params_for_gui(self):
        """
        Need to be implemented in order to be used through the graphical interface.
        :return: a list of dict
        """
        return None

    @property
    def data_to_analyse(self):
        """

        :return: a list of the data to analyse
        """
        return self._data_to_analyse

    def update_original_data(self):
        """
        To be called if the data to analyse should be updated after the analysis has been run.
        :return: boolean: return True if the data has been modified
        """
        pass

    @abstractmethod
    def run_analysis(self, **kwargs):
        """
        Run the analysis
        :param kwargs:
        :return:
        """
        pass

    # TODO: do a function that return a structure (home-made class ?) that will be used by the GUI to know
    #  which argument to pass to run_analysis, their types, if mandatory and their range among other things
