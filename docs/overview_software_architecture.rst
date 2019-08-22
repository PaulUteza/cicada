---------------------
Software architecture
---------------------

Analysis
--------
 Each analysis is represented by a class that inherits CicadaAnalysis (in the module `cicada.analysis <https://cicada-cossart.readthedocs.io/en/latest/analysis.html#module-cicada.analysis.cicada_analysis>`_).

Each CicadaAnalysis instance instanciate an ArgumentAnalysisHandler that communicates with the GUI and handle the arguments that will be passed to the analysis. 

Each CicadaAnalaysis instance allows to check the compatibility of the data to analyze though the method check_data().

The method run_analysis() will be called to start the analysis. 

The abstract class CicadaAnalysisFormatWrapper allows,through inheritance, to write a wrapper for a given data format, such as nwb. 
It allows to get the content from specific data format, and adding a new format consists in creating a new instance of CicadaAnalysisFormatWrapper, without any change in the CicadaAnalysis instances.


Graphical User Interface
------------------------

The GUI uses QT through QtPy which wrapps PyQt5 and PySide. 

The GUI is composed of 3 main modules. (screenshot to add)
1. A list that displays the loaded recorded sessions to analyse (`SessionsWidget <https://cicada-cossart.readthedocs.io/en/latest/gui.html#module-cicada.gui.session_show_filter_group>`_).

2. A tree that displays the available analyses, updated depending on the data to analyse. (`AnalysisTreeApp <https://cicada-cossart.readthedocs.io/en/latest/gui.html#module-cicada.gui.cicada_analysis_tree_guianalysis>`_) 

3. A panel that allows to set arguments for the given analysis and to follow the status of the analysis. (`AnalysisParametersApp <https://cicada-cossart.readthedocs.io/en/latest/gui.html#module-cicada.gui.cicada_analysis_parameters_gui>`_>
