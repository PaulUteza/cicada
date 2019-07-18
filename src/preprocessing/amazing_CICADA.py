from datetime import datetime
from dateutil.tz import tzlocal
from shapely.geometry import MultiPoint, LineString

import numpy as np

from pynwb import NWBFile
from pynwb.ophys import TwoPhotonSeries, OpticalChannel, ImageSegmentation, Fluorescence
from pynwb.device import Device
from pynwb import NWBHDF5IO


class Preprocessing:

    def __init__(self, *args):
        self.nwbfile = NWBFile("essai", "ID", datetime.now(tzlocal()), args)
        self.mod = self.nwbfile.create_processing_module('ophys', 'contains optical physiology processed data')
        self.optical_channel = OpticalChannel('my_optchan', 'description', 500.)

        self.device = Device('imaging_device_1')
        self.nwbfile.add_device(self.device)


    def cicada_create_imaging_plane(self):

        """ class pynwb.ophys.ImagingPlane(name, optical_channel, description, device, excitation_lambda,
            imaging_rate, indicator, location,
            manifold=None, conversion=None, unit=None, reference_frame=None, parent=None)
        """

        # Nom du module où récupérer les infos de métadonnée
        name_module = "image_plane_"

        # Récupération des données

        optical_channel = self.optical_channel
        device = self.device

        self.imaging_plane = self.nwbfile.create_imaging_plane(name=data.get(name_module + "name"),
                                                               optical_channel=optical_channel,
                                                               description=data.get(name_module + "description"),
                                                               device=device,
                                                               excitation_lambda=data.get("excitation_lambda"),
                                                               imaging_rate=data.get("imaging_rate"),
                                                               indicator=data.get("indicator"),
                                                               location=data.get(name_module + "location"),
                                                               manifold=data.get("manifold"),
                                                               conversion=data.get(name_module + "conversion"),
                                                               unit=data.get(name_module + "unit"),
                                                               reference_frame=data.get(name_module + "reference_frame"))

        self.nwbfile.add_imaging_plane(imaging_plane)

    def cicada_create_two_photon_series(self):

        """ class pynwb.ophys.TwoPhotonSeries(name, imaging_plane,
            data=None, unit=None, format=None, field_of_view=None, pmt_gain=None, scan_line_rate=None,
            external_file=None, starting_frame=None, bits_per_pixel=None, dimension=[nan], resolution=0.0,
            conversion=1.0, timestamps=None, starting_time=None, rate=None, comments='no comments',
            description='no description', control=None, control_description=None, parent=None)
        """

        # Nom du module où récupérer les infos de métadonnée
        name_module = "two_photon_"

        # Récupération des données

        name_imaging_plane = "imaging_plane"
        imaging_plane = self.nwbfile.get_imaging_plane(name_imaging_plane)

        two_photon_data = None

        self.movie_two_photon = TwoPhotonSeries(name=data.get(name_module + "name"),
                                                imaging_plane=imaging_plane,
                                                data=two_photon_data,
                                                unit=data.get(name_module + "unit"),
                                                format=data.get(name_module + "format"),
                                                field_of_view=data.get(name_module + "field_of_view"),
                                                pmt_gain=data.get(name_module + "pmt_gain"),
                                                scan_line_rate=data.get(name_module + "scan_line_rate"),
                                                external_file=data.get(name_module + "external_file"),
                                                starting_frame=data.get(name_module + "starting_frame"),
                                                bits_per_pixel=data.get(name_module + "bits_per_pixel"),
                                                dimension=data.get(name_module + "dimension"),
                                                resolution=data.get(name_module + "resolution"),
                                                conversion=data.get(name_module + "conversion"),
                                                timestamps=data.get(name_module + "timestamps"),
                                                starting_time=data.get(name_module + "starting_time"),
                                                rate=data.get(name_module + "rate"),
                                                comments=data.get(name_module + "comments"),
                                                description=data.get(name_module + "description"),
                                                control=data.get(name_module + "control"),
                                                control_description=data.get(name_module + "control_description"),
                                                parent=data.get(name_module + "parent"))

        self.nwbfile.add_acquisition(movie_two_photon)


    def cicada_add_plane_segmentation(self):

        """ class pynwb.ophys.PlaneSegmentation(description, imaging_plane,
            name=None, reference_images=None, id=None, columns=None, colnames=None)
        """

        # Image segmentation où stocker la plane segmentation

        image_segmentation = self.image_segmentation

        # Nom du module où récupérer les infos de métadonnée
        name_module = "plane_segmentation_"

        # Récupération des données

        imaging_plane = self.nwbfile.get_imaging_plane(name_imaging_plane)

        self.plane_segmentation = PlaneSegmentation(description=data.get(name_module + "description")),
                                               imaging_plane=imaging_plane,
                                               name=data.get(name_module + "name")),
                                               reference_images=data.get(name_module + "reference_image")),
                                               id=data.get(name_module + "id")),
                                               columns=data.get(name_module + "columns")),
                                               colnames=data.get(name_module + "colnames")))

        self.image_segmentation.add_plane_segmentation(self.plane_segmentation)

    def cicada_add_roi_in_plane_segmentation(self):
        ########################################################## PAS FINI !!!!!!!!!! ############################
        """add_roi(pixel_mask=None, voxel_mask=None, image_mask=None, id=None)"""

        # Plane segmentation où stocker la plane segmentation

        image_segmentation = self.image_segmentation

        # Nom du module où récupérer les infos de métadonnée
        name_module = "plane_segmentation_"

        # Récupération des données

        imaging_plane = self.nwbfile.get_imaging_plane(name_imaging_plane)

        self.plane_segmentation = PlaneSegmentation(description=data.get(name_module + "description")),
        imaging_plane = imaging_plane,
        name = data.get(name_module + "name")),
        reference_images = data.get(name_module + "reference_image")),
        id = data.get(name_module + "id")),
        columns = data.get(name_module + "columns")),
        colnames = data.get(name_module + "colnames")))

        self.image_segmentation.add_plane_segmentation(self.plane_segmentation)


    def find_ROI(self):

        # Chemin du dossier suite2p
        data_path = "C:/Users/François/Documents/dossier François/Stage INMED/Programmes/Godly Ultimate Interface/NWB/exp2nwb-master/src/suite2p"
        self.suite2p_data = dict()

        # Ouverture des fichiers stat et is_cell
        f = np.load(data_path + "/F.npy", allow_pickle=True)
        self.suite2p_data["F"] = f
        f_neu = np.load(data_path + "/Fneu.npy", allow_pickle=True)
        self.suite2p_data["Fneu"] = f_neu
        spks = np.load(data_path + "/spks.npy", allow_pickle=True)
        self.suite2p_data["spks"] = spks
        stat = np.load(data_path + "/stat.npy", allow_pickle=True)
        self.suite2p_data["stat"] = stat
        is_cell = np.load(data_path + "/iscell.npy", allow_pickle=True)
        self.suite2p_data["is_cell"] = is_cell

        # Trouve les coordonnées de chaque ROI (cellule ici)
        coord = []
        for cell in np.arange(len(stat)):
            if is_cell[cell][0] == 0:
                continue
            print(is_cell[cell][0])
            list_points_coord = [(x, y, 1) for x, y in zip(stat[cell]["xpix"], stat[cell]["ypix"])]
            #coord.append(np.array(list_points_coord).transpose())

            # La suite permet d'avoir uniquement les contours (sans les pixels intérieurs)

            # ATTENTION ! Il faut : from shapely.geometry import MultiPoint, LineString
            convex_hull = MultiPoint(list_points_coord).convex_hull
            if isinstance(convex_hull, LineString):
                coord_shapely = MultiPoint(list_points_coord).convex_hull.coords
            else:
                coord_shapely = MultiPoint(list_points_coord).convex_hull.exterior.coords
            coord.append(np.array(coord_shapely).transpose())


        self.suite2p_data["coord"] = coord  # Contient la liste des pixels inclus dans chaque ROI