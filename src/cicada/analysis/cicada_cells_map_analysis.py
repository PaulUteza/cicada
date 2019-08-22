from cicada.analysis.cicada_analysis import CicadaAnalysis
from cicada.utils.display.cells_map_utils import CellsCoord
import sys
from time import sleep, time
import numpy as np
from shapely.geometry import MultiPoint, LineString

class CicadaCellsMapAnalysis(CicadaAnalysis):
    def __init__(self):
        """
        """
        CicadaAnalysis.__init__(self, name="cells_map", family_id="display",
                                short_description="Plot map of the cells")

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

            segmentations = self.analysis_formats_wrapper.get_segmentations()

            # we need at least one segmentation
            if (segmentations is None) or len(segmentations) == 0:
                return False
        return True

    def set_arguments_for_gui(self):
        """

        Returns:

        """
        CicadaAnalysis.set_arguments_for_gui(self)

        # range_arg = {"arg_name": "psth_range", "value_type": "int", "min_value": 50, "max_value": 2000,
        #              "default_value": 500, "description": "Range of the PSTH (ms)"}
        # self.add_argument_for_gui(**range_arg)
        #
        # stim_arg = {"arg_name": "stimulus name", "value_type": "str",
        #              "default_value": "stim", "description": "Name of the stimulus"}
        # self.add_argument_for_gui(**stim_arg)
        #
        # plot_arg = {"arg_name": "plot_options", "choices": ["lines", "bars"],
        #             "default_value": "bars", "description": "Options to display the PSTH"}
        # self.add_argument_for_gui(**plot_arg)
        #
        # avg_arg = {"arg_name": "average_fig", "value_type": "bool",
        #            "default_value": True, "description": "Add a figure that average all sessions"}
        #
        # self.add_argument_for_gui(**avg_arg)
        #
        # format_arg = {"arg_name": "save_formats", "choices": ["pdf", "png"],
        #             "default_value": "pdf", "description": "Formats in which to save the figures",
        #             "multiple_choices": True}
        #
        # self.add_argument_for_gui(**format_arg)

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
        CicadaAnalysis.run_analysis(self, **kwargs)

        if self._data_format != "nwb":
            print(f"Format others than nwb not supported yet")
            return

        self.run_nwb_format_analysis(**kwargs)

    def run_nwb_format_analysis(self, **kwargs):
        start_time = time()
        n_sessions = len(self._data_to_analyse)

        segmentation_dict = kwargs['segmentation']

        for session_index, session_data in enumerate(self._data_to_analyse):
            session_identifier = session_data.identifier
            mod = session_data.modules['ophys']
            plane_seg = mod[segmentation_dict[session_identifier]].get_plane_segmentation('my_plane_seg')

            if 'pixel_mask' not in plane_seg:
                print(f"pixel_mask not available in for {session_data.identifier} "
                      f"in {segmentation_dict[session_identifier]}")
                self.update_progressbar(start_time, 100 / n_sessions)
                continue

            # TODO: use pixel_mask instead of using the coord of the contour of the cell
            #  means changing the way coord_cell works
            coord_list = []
            for cell in np.arange(len(plane_seg['pixel_mask'])):
                pixels_coord = plane_seg['pixel_mask'][cell]
                list_points_coord = [(pix[0], pix[1]) for pix in pixels_coord]
                convex_hull = MultiPoint(list_points_coord).convex_hull
                if isinstance(convex_hull, LineString):
                    coord_shapely = MultiPoint(list_points_coord).convex_hull.coords
                else:
                    coord_shapely = MultiPoint(list_points_coord).convex_hull.exterior.coords
                coord_list.append(np.array(coord_shapely).transpose())

            cells_coord = CellsCoord(coord_list, nb_col=200, nb_lines=200, from_suite_2p=True)

            cells_coord.plot_cells_map(path_results=self.get_results_path(),
                                          data_id=session_identifier, show_polygons=False,
                                          fill_polygons=False,
                                          title_option="all_cells", connections_dict=None,
                                          cells_groups=None,
                                          img_on_background=None,
                                          cells_groups_colors=None,
                                          cells_groups_edge_colors=None,
                                          with_edge=True, cells_groups_alpha=None,
                                          dont_fill_cells_not_in_groups=False,
                                          with_cell_numbers=True, save_formats=["png", "pdf"],
                                          save_plot=True, return_fig=False)

            self.update_progressbar(start_time, 100 / n_sessions)