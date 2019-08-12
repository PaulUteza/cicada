from cicada.analysis.cicada_analysis import CicadaAnalysis
from tqdm import tqdm
import sys
from time import sleep

class CicadaPsthAnalysis(CicadaAnalysis):
    def __init__(self):
        """
        A list of
        :param data_to_analyse: list of data_structure
        :param family_id: family_id indicated to which family of analysis this class belongs. If None, then
        the analysis is a family in its own.
        :param data_format: indicate the type of data structure. for NWB, NIX
        """
        CicadaAnalysis.__init__(self, name="PSTH",
                         short_description="Build PSTH")

    def check_data(self):
        """
        Check the data given one initiating the class and return True if the data given allows the analysis
        implemented, False otherwise.
        :return: a boolean
        """
        if self._data_format != "nwb":

            # non NWB format compatibility not yet implemented
            return False

        for data in self._data_to_analyse:
            # check is there is at least one processing module
            if len(data.processing) == 0:
                return False

            # in our case, we will use 'ophys' module
            if "ophys" not in data.processing:
                return False
        return True

    def set_arguments_for_gui(self):
        """

        Returns:

        """
        CicadaAnalysis.set_arguments_for_gui(self)

        range_arg = {"arg_name": "psth_range", "value_type": "int", "min_value": 50, "max_value": 2000,
                     "default_value": 500, "description": "Range of the PSTH (ms)"}
        self.add_argument_for_gui(**range_arg)

        stim_arg = {"arg_name": "stimulus name", "value_type": "str",
                     "default_value": "stim", "description": "Name of the stimulus"}
        self.add_argument_for_gui(**stim_arg)

        plot_arg = {"arg_name": "plot_options", "choices": ["lines", "bars"],
                    "default_value": "bars", "description": "Options to display the PSTH"}
        self.add_argument_for_gui(**plot_arg)

        avg_arg = {"arg_name": "average_fig", "value_type": "bool",
                   "default_value": True, "description": "Add a figure that average all sessions"}

        self.add_argument_for_gui(**avg_arg)

        format_arg = {"arg_name": "save_formats", "choices": ["pdf", "png"],
                    "default_value": "pdf", "description": "Formats in which to save the figures",
                    "multiple_choices": True}

        self.add_argument_for_gui(**format_arg)

        # not mandatory, because one of the element will be selected by the GUI
        segmentation_arg = {"arg_name": "segmentation", "choices": self.analysis_formats_wrapper.get_segmentations(),
                            "description": "Segmentation to use", "mandatory": False,
                            "multiple_choices": False}

        self.add_argument_for_gui(**segmentation_arg)

    def update_original_data(self):
        """
        To be called if the data to analyse should be updated after the analysis has been run.
        :return: boolean: return True if the data has been modified
        """
        pass

    def run_analysis(self, **kwargs):
        """
        test
        :param kwargs:
        :return:
        """
        for data in tqdm(self._data_to_analyse, file=sys.stdout, ncols=100, desc=self.name, ascii=False):
            print(f"PSTH ----- {data.identifier} on range {kwargs['psth_range']} with {kwargs['plot_options']} "
                  f"plot using {kwargs['segmentation']} "
                  f"with formats {kwargs['save_formats']} ")
        # for i in tqdm(range(10),file=sys.stdout, ncols=100, ascii=False):
        #     sleep(1)
