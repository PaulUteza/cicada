from qtpy.QtWidgets import *
from qtpy.QtCore import Qt
from cicada.gui.cicada_analysis_parameters_gui import *


class AnalysisArgument:

    def __init__(self, **kwargs):
        """

        Args:
            **kwargs:
                - arg_name
                - order_index
                - default_value
                - range_values
                - max_value
                - min_value
                - value_type
        """
        for attribute_name, value in kwargs.items():
            setattr(self, attribute_name, value)

        self.widget = None

    def get_gui_widget(self):
        if self.widget:
            return self.widget

        if getattr(self, "value_type", None) == "int":
            if hasattr(self, "min_value") and hasattr(self, "max_value"):
                self.widget = SliderWidget(analysis_arg=self)
                return self.widget

    # TODO: implement __eq__ etc.. in order to sort AnalysisArgument, mandatory first... and then use order_index

class AnalysisArgumentsHandler:

    def __init__(self):
        self.args_dict = dict()
        self.order_index = 0

    def add_argument(self, **kwargs):
        arg_analysis = AnalysisArgument(**kwargs, order_index=self.order_index)
        self.order_index += 1
        self.args_dict[arg_analysis.arg_name] = arg_analysis

    def get_argument(self, arg_name):
        self.args_dict.get(arg_name)

    def get_analysis_arguments(self):
        return list(self.args_dict.values())

    def set_argument_value(self, arg_name, **kwargs):
        """
        Set an argument values, will be use to run analysis
        Args:
            arg_name:
            **kwargs:

        Returns:

        """
        pass

    def check_arguments_validity(self):
        """
        Check if all mandatory arguments have been filled
        Returns:

        """
        pass

