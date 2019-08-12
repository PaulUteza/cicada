from abc import ABC, abstractmethod, abstractproperty
from cicada.analysis.cicada_analysis_arguments_handler import AnalysisArgumentsHandler
from cicada.analysis.cicada_analysis_nwb_wrapper import CicadaAnalysisNwbWrapper
from cicada.preprocessing.utils import class_name_to_file_name
import importlib
from copy import copy, deepcopy

class CicadaAnalysis(ABC):
    """
    An abstract class that should be inherit in order to create a specific analyse

    """
    def __init__(self, name, short_description, family_id=None, long_description=None,
                 data_to_analyse=None, data_format=None,):
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
        self.current_order_index = 0
        self._data_to_analyse = data_to_analyse
        self._data_format = data_format
        self.analysis_arguments_handler = AnalysisArgumentsHandler(cicada_analysis=self)

        # dict containing instances of CicadaAnalysisFormatWrapper, for each format supported
        self.analysis_formats_wrapper = None
        self.initiate_analysis_formats_wrapper(data_format=data_format)
        if self._data_to_analyse:
            self.set_arguments_for_gui()

    # @abstractproperty
    # def data_to_analyse(self):
    #     pass
    #
    # @abstractproperty
    # def data_format(self):
    #     pass


    def copy(self):

        module_name = 'cicada.analysis.' + class_name_to_file_name(self.__class__.__name__)
        module = importlib.import_module(module_name)
        new_class = getattr(module, self.__class__.__name__)
        new_object = new_class()
        new_object.name = self.name
        new_object.short_description = self.short_description
        new_object.family_id = self.family_id
        new_object.long_description = self.long_description
        new_object.set_data(self._data_to_analyse, self._data_format)
        return new_object

    def initiate_analysis_formats_wrapper(self, data_format):
        if data_format == "nwb":
            self.analysis_formats_wrapper = CicadaAnalysisNwbWrapper(self._data_to_analyse)


    def set_data(self, data_to_analyse, data_format="nwb"):
        """
                A list of
                :param data_to_analyse: list of data_structure
                :param data_format: indicate the type of data structure. for NWB, NIX
        """
        self.initiate_analysis_formats_wrapper(data_format=data_format)
        if not isinstance(data_to_analyse, list):
            data_to_analyse = [data_to_analyse]
        self.analysis_formats_wrapper.set_data(data_to_analyse)
        self._data_to_analyse = data_to_analyse
        self._data_format = data_format
        self.set_arguments_for_gui()

    @abstractmethod
    def check_data(self):
        """
        Check the data given one initiating the class and return True if the data given allows the analysis
        implemented, False otherwise.
        :return: a boolean
        """
        pass

    def add_argument_for_gui(self, with_incremental_order=True, **kwargs):
        """

        Args:
            **kwargs:
            with_incremental_order: boolean, if True means the order of the argument will be the same as when added

        Returns:

        """
        if with_incremental_order:
            kwargs.update({"order_index": self.current_order_index})
            self.current_order_index += 1

        self.analysis_arguments_handler.add_argument(**kwargs)

    def set_arguments_for_gui(self):
        """
        Need to be implemented in order to be used through the graphical interface.
        :return: None
        """
        # creating a new AnalysisArgumentsHandler instance
        self.analysis_arguments_handler = AnalysisArgumentsHandler(cicada_analysis=self)
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
