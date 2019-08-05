from qtpy.QtWidgets import *
from qtpy.QtCore import Qt
# to import the Widgets for the GUI
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
                - mandatory
                - description
                - ...
        """
        for attribute_name, value in kwargs.items():
            setattr(self, attribute_name, value)

        self.widget = None

        self.final_value = None

    def get_gui_widget(self):
        if self.widget:
            return self.widget

        if getattr(self, "value_type", None) == "int":
            if hasattr(self, "min_value") and hasattr(self, "max_value"):
                self.widget = SliderWidget(analysis_arg=self)
                return self.widget
        elif getattr(self, "value_type", None) == "str":
            if hasattr(self, "choices"):
                self.widget = ComboBoxWidget(analysis_arg=self)
                return self.widget
        elif getattr(self, "value_type", None) == "bool":
            self.widget = CheckBoxWidget(analysis_arg=self)
            return self.widget
        else:
            self.widget = LineEditWidget(analysis_arg=self)
            return self.widget

    def set_argument_value(self, value):
        self.final_value = value

    def is_mandatory(self):
        return getattr(self, "mandatory", False)

    # TODO: implement __eq__ etc.. in order to sort AnalysisArgument, mandatory first... and then use order_index
    #  to sort among mandatory and among non-mandatory arguments

    def get_default_value(self):
        return getattr(self, "default_value", None)

    def get_description(self):
        return getattr(self, "description", None)

    def get_argument_value(self):
        if self.widget is None:
            return None
        return self.widget.get_value()


class AnalysisArgumentsHandler:
    """
    Handle the AnalysisArgument instances for a given CicadaAnalysis instance.
    Allows to create the widgets and get the values to pass to run_analysis() of the CicadaAnalysis instance.
    """

    def __init__(self, cicada_analysis):
        self.args_dict = dict()
        self.order_index = 0
        self.cicada_analysis = cicada_analysis

    def add_argument(self, **kwargs):
        arg_analysis = AnalysisArgument(**kwargs, order_index=self.order_index)
        self.order_index += 1
        self.args_dict[arg_analysis.arg_name] = arg_analysis

    def get_analysis_argument(self, arg_name):
        self.args_dict.get(arg_name)

    def get_analysis_arguments(self, ordered=False):
        # TODO: implement sorting of the args
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

    def get_gui_widgets(self):
        """
        Get the list of widgets necessary to fill the arguments for the cicada analysis associated
        Returns:

        """
        gui_widgets = []
        analysis_arguments = self.get_analysis_arguments()
        for analysis_argument in analysis_arguments:
            widget = analysis_argument.get_gui_widget()
            if widget:
                gui_widgets.append(widget)
        return gui_widgets

    def check_arguments_validity(self):
        """
        Check if all mandatory arguments have been filled
        Returns:

        """
        pass

    def run_analysis(self):
        kwargs = {}
        for arg_name, analysis_argument in self.args_dict.items():
            kwargs[arg_name] = analysis_argument.get_argument_value()
        self.cicada_analysis.run_analysis(**kwargs)
