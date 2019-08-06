from cicada.analysis.cicada_analysis_format_wrapper import CicadaAnalysisFormatWrapper
from pynwb.ophys import ImageSegmentation


class CicadaAnalysisNwbWrapper(CicadaAnalysisFormatWrapper):
    """
    Allows to communicate with the nwb format
    """

    def __init__(self, data_to_analyse=None):
        CicadaAnalysisFormatWrapper.__init__(self, data_to_analyse=data_to_analyse)


    def get_segmentations(self):
        """

        Returns: a dict with key being the id of the cicada_analysis and the
        value is a string representing the segmentation name

        """
        segmentations_dict = dict()

        for nwb_file in self.data_to_analyse:
            mod = nwb_file.modules['ophys']
            segmentation_keys = []
            for key, value in mod.data_interfaces.items():
                # we want to check that the object in Module is an Instance of ImageSegmentation
                if isinstance(value, ImageSegmentation):
                    segmentation_keys.append(key)
            # it could be empty, but if it matters, it should have been check by method check_data in CicadaAnalysis
            segmentations_dict[nwb_file.identifier] = segmentation_keys

        return segmentations_dict