from abc import ABC, abstractmethod, abstractproperty


class CicadaAnalysisFormatWrapper(ABC):
    """
    An abstract class that should be inherit in order to create a specific format wrapper

    """

    def __init__(self, data_to_analyse):
        super().__init__()
        self.data_to_analyse = data_to_analyse

    def set_data(self, data_to_analyse):
        self.data_to_analyse = data_to_analyse

    @abstractmethod
    def get_segmentations(self):
        """

        Returns: a dict with key being the id of the cicada_analysis and the
        value is a string representing the segmentation name

        """
        pass