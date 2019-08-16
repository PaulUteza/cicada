class ConfigHandler:
    """
    Class used for handling the configuration for the GUI.
    At term, it should also open a config GUI to set the parameters.
    All GUI parameters should be available there.
    """
    def __init__(self):
        # Path of the directory where to save new results
        # usually a new directory specific to the analysis done will be created in this directory
        self._default_results_path = None

    @property
    def default_results_path(self):
        return self._default_results_path

    @default_results_path.setter
    def default_results_path(self, value):
        self._default_results_path = value

