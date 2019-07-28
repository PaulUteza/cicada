class CicadaAnalysis:
    """
    A generic class that should be inherit in order to create a specific analyse

    """
    def __init__(self, data_to_analyse, family_id=None, data_format="NWB"):
        """
        A list of
        :param data_to_analyse: list of data_structure
        :param family_id: family_id indicated to which family of analysis this class belongs. If None, then
        the analysis is a family in its own.
        :param data_format: indicate the type of data structure. for NWB, NIX
        """
        # TODO: when the exploratory GUI will be built, think about passing in argument some sort of connector
        #  to the GUI in order to communicate with it and get the results displayed if needed
        if not isinstance(data_to_analyse, list):
            data_to_analyse = [data_to_analyse]
        self.data_to_analyse = data_to_analyse
        self.data_format = data_format
        self.family_id = family_id

    def check_data(self):
        """
        Check the data given one initiating the class and return True if the data given allows the analysis
        implemented, False otherwise.
        :return: a boolean
        """
        pass

    @property
    def data_to_analyse(self):
        """

        :return: a list of the data to analyse
        """
        return self.data_to_analyse

    def update_original_data(self):
        """
        To be called if the data to analyse should be updated after the analysis has been run.
        :return: boolean: return True if the data has been modified
        """
        pass

    def run_analysis(self, **kwargs):
        """
        Run the analysis
        :param kwargs:
        :return:
        """
        pass

    # TODO: do a function that return a structure (home-made class ?) that will be used by the GUI to know
    #  which argument to pass to run_analysis, their types, if mandatory and their range among other things
