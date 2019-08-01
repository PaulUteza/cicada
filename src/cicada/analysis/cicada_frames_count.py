from cicada.analysis.cicada_analysis import CicadaAnalysis


class CicadaFramesCount(CicadaAnalysis):
    def __init__(self):
        """
        A list of
        :param data_to_analyse: list of data_structure
        :param family_id: family_id indicated to which family of analysis this class belongs. If None, then
        the analysis is a family in its own.
        :param data_format: indicate the type of data structure. for NWB, NIX
        """
        super().__init__(name="count frames", family_id="counter",
                         short_description="Count the number of frames")

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

    def update_original_data(self):
        """
        To be called if the data to analyse should be updated after the analysis has been run.
        :return: boolean: return True if the data has been modified
        """
        pass

    def run_analysis(self, **kwargs):
        """
        Run the analysis: just printing the number of cells in each session
        :param kwargs:
        :return:
        """
        n_frames_dict = {}
        for data in self._data_to_analyse:
            mod = data.modules['ophys']
            rrs = mod['Fluorescence'].get_roi_response_series()

            # get the data...
            rrs_data = rrs.data
            n_frames_dict[data.identifier] = rrs.data.shape[1]
            # rrs_timestamps = rrs.timestamps
            # rrs_rois = rrs.rois
        print(f"N frames by session: {n_frames_dict}")
