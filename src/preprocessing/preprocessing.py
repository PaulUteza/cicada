
from datetime import datetime
from dateutil.tz import tzlocal
from shapely.geometry import MultiPoint, LineString

import numpy as np

from pynwb import NWBFile
from pynwb.ophys import TwoPhotonSeries, OpticalChannel, ImageSegmentation, PlaneSegmentation, Fluorescence, \
                        DfOverF, RoiResponseSeries, MotionCorrection, CorrectedImageStack
from pynwb.device import Device
from pynwb import NWBHDF5IO

import yaml
import os

from pynwb import NWBHDF5IO
from pynwb import NWBFile
from pynwb.ophys import TwoPhotonSeries, OpticalChannel, ImageSegmentation, Fluorescence
from pynwb.device import Device
from pynwb.file import Subject


class Preprocessing(object):

    def load_yaml(self):
        # Open YAML file with metadata if existing then dump all data in a dict
        if os.path.isfile("data.yaml"):
            with open("data.yaml", 'r') as stream:
                self.data = yaml.safe_load(stream)
        # Same but with .yml extension
        elif os.path.isfile("data.yml"):
            with open("data.yml", 'r') as stream:
                self.data = yaml.safe_load(stream)
        else:
            self.data = dict()
        if self.data is None:
            self.data = dict()
        self.subject_metadata_acquisition()
        self.ophys_metadata_acquisition()
        # Dump the dict in the YAML file to save what the user inputted for future use
        with open('data.yaml', 'w') as outfile:
            yaml.dump(self.data, outfile, default_flow_style=False, allow_unicode=True)

    def add_required_metadata(self, data, key, metadata_type):
        # Prompt user to give required metadata
        # Need to be wary of the type (put " " for string and datetime.datetime(%Y, %m, %d) for datetime)
        print("Missing required " + metadata_type + " metadata : " + key + "\n")
        metadata_value = input("Type the value (with respect of the type) : ")
        data[key] = eval(metadata_value)
        return data

    def add_optional_metadata(self,data):
        # Allow user to add as much metadata as he wants with the key he wants
        # Need to refer to documentation if he wants to fill existing attributes but he can create new ones and use
        # them in his own code
        keyboard_input = False
        while not keyboard_input:
            # Prompt user to give optional metadata
            # Need to be wary of the type (put " " for string and datetime.datetime(%Y, %m, %d) for datetime)
            metadata_key = input("Type the name of the metadata you want to add ? ")
            metadata_key.replace(" ","").lower().replace("", "_")
            metadata_value = input("Type the value (with respect of the type) : ")
            data[metadata_key] = eval(metadata_value)
            go = input("Continue ? (yes/no)")
            # Prevent errors if other input than yes/np
            while go.replace(" ","").lower() != "no" and go.replace(" ","").lower() != "yes":
                go = input("Continue ? (yes/no)")
            if go.replace(" ","").lower() == "no":
                keyboard_input = True
        return data

    def ophys_metadata_acquisition(self):

        # TODO: Peut être faire un dictionnaire de sous-dictionnaires correspondant à chaque classe à remplir
        #         Points positifs : Plus grand lisibilité dans le YAML, gestion simple des ambiguités de nom
        #         tout en gardant la notation de NWB.
        #         Points négatifs : Plus dur à rentrer en input pour l'utilisateur (il faut lui demander à quelle classe
        #         correspond sa valeur).

        # List of the required metadata

        # TODO : maybe better implementation is possible ?

        required_metadata = ["session_description", "identifier", "session_start_time"]

        if self.data.get('ophys_metadata') is None:
            self.data['ophys_metadata'] = dict()
            for i in required_metadata:
                self.data["ophys_metadata"] = self.add_required_metadata(self.data["ophys_metadata"], i, "ophys")
        else:
            # Check if YAML file doesn't have all the required attributes and ask them the missing ones
            metadata_to_add = list(set(required_metadata) - set(list(self.data['ophys_metadata'].keys())))
            for i in metadata_to_add:
                self.data["ophys_metadata"] = self.add_required_metadata(self.data["ophys_metadata"], i, "ophys")

        print("Found ophys metadata : " + str(list(self.data['ophys_metadata'].keys())))
        add_metadata = input("Do you want to add more ophys metadata ? (yes/no) ")
        # Prevent errors if other input than yes/np
        while add_metadata.replace(" ", "").lower() != "no" and add_metadata.replace(" ", "").lower() != "yes":
            add_metadata = input("Do you want to add more ophys metadata ? (yes/no) ")
        if add_metadata.replace(" ", "").lower() == "yes":
            self.data["ophys_metadata"] = self.add_optional_metadata(self.data["ophys_metadata"])

        # Create new NWB file with all known attributes
        self.nwbfile = NWBFile(session_description=self.data['ophys_metadata'].get("session_description"),
                               identifier=self.data['ophys_metadata'].get("identifier"),
                               session_start_time=self.data['ophys_metadata'].get("session_start_time"),
                               file_create_date=self.data['ophys_metadata'].get("file_create_date"),
                               timestamps_reference_time=self.data['ophys_metadata'].get("timestamps_reference_time"),
                               experimenter=self.data['ophys_metadata'].get("experimenter"),
                               experiment_description=self.data['ophys_metadata'].get("experiment_description"),
                               session_id=self.data['ophys_metadata'].get("session_id"),
                               institution=self.data['ophys_metadata'].get("institution"),
                               keywords=self.data['ophys_metadata'].get("keywords"),
                               notes=self.data['ophys_metadata'].get("notes"),
                               pharmacology=self.data['ophys_metadata'].get("pharmacology"),
                               protocol=self.data['ophys_metadata'].get("protocol"),
                               related_publications=self.data['ophys_metadata'].get("related_publications"),
                               slices=self.data['ophys_metadata'].get("slices"),
                               source_script=self.data['ophys_metadata'].get("source_script"),
                               source_script_file_name=self.data['ophys_metadata'].get("source_script_file_name"),
                               data_collection=self.data['ophys_metadata'].get("self.data['ophys_metadata']_collection"),
                               surgery=self.data['ophys_metadata'].get("surgery"),
                               virus=self.data['ophys_metadata'].get("virus"),
                               stimulus_notes = self.data['ophys_metadata'].get("stimulus_notes"),
                               lab=self.data['ophys_metadata'].get("lab"),subject=self.subject)


    def subject_metadata_acquisition(self):
        # Check if metadata about the subject exists and prompt the user if he wants to add some
        if self.data.get('subject_metadata') is None:
            print("No subject metadata found \n ")
            self.data['subject_metadata'] = dict()
        elif len(self.data['subject_metadata']) == 0:
            print("No subject metadata found \n ")
        else:
            print("Found subject metadata : " + str(list(self.data['subject_metadata'].keys())))
        add_metadata = input("Do you want to add more subject metadata ? (yes/no) ")
        # Prevent errors if other input than yes/np
        while add_metadata.replace(" ", "").lower() != "no" and add_metadata.replace(" ", "").lower() != "yes":
            add_metadata = input("Do you want to add more subject metadata ? (yes/no) ")
        if add_metadata.replace(" ", "").lower() == "yes":
            self.data['subject_metadata'] = self.add_optional_metadata(self.data['subject_metadata'])

        self.subject = Subject(age=self.data['subject_metadata'].get("age"),
                               description=self.data['subject_metadata'].get("description"),
                               genotype=self.data['subject_metadata'].get("genotype"),
                               sex=self.data['subject_metadata'].get("sex"),
                               species=self.data['subject_metadata'].get("species"),
                               subject_id=self.data['subject_metadata'].get("subject_id"),
                               weight=self.data['subject_metadata'].get("weight"),
                               date_of_birth=self.data['subject_metadata'].get("date_of_birth"))

    def cicada_create_device(self):
        """
        class pynwb.ophys.OpticalChannel(name, description, emission_lambda, parent=None)
        """
        required_metadata = ["device"]

        metadata_to_add = list(set(required_metadata) - set(list(self.data['ophys_metadata'].keys())))
        for i in metadata_to_add:
            self.data["ophys_metadata"] = self.add_required_metadata(self.data["ophys_metadata"], i, "ophys")

        device = Device(name=self.data['ophys_metadata'].get("device"))

        self.nwbfile.add_device(device)

    def cicada_create_optical_channel(self):
        required_metadata = ["optical_channel_name", "optical_channel_description", "emission_lambda"]


        metadata_to_add = list(set(required_metadata) - set(list(self.data['ophys_metadata'].keys())))
        for i in metadata_to_add:
            self.data["ophys_metadata"] = self.add_required_metadata(self.data["ophys_metadata"], i, "ophys")

        self.optical_channel = OpticalChannel(name=self.data['ophys_metadata'].get("optical_channel_name"),
                                              description=self.data['ophys_metadata'].get(
                                                  "optical_channel_description"),
                                              emission_lambda=self.data['ophys_metadata'].get("emission_lambda"))

    def cicada_create_module(self):

        required_metadata = ["processing_module_name","processing_module_description"]

        metadata_to_add = list(set(required_metadata) - set(list(self.data['ophys_metadata'].keys())))
        for i in metadata_to_add:
            self.data["ophys_metadata"] = self.add_required_metadata(self.data["ophys_metadata"], i, "ophys")

        self.mod = self.nwbfile.create_processing_module(name=self.data['ophys_metadata'].get("processing_module_name"),
                                                         description=self.data['ophys_metadata'].get(
                                                             "processing_module_description"))

    def cicada_create_imaging_plane(self):

        """ class pynwb.ophys.ImagingPlane(name, optical_channel, description, device, excitation_lambda,
            imaging_rate, indicator, location,
            manifold=None, conversion=None, unit=None, reference_frame=None, parent=None)
        """

        required_metadata = ["imaging_plane_name", "imaging_plane_description", "excitation_lambda",
                             "imaging_rate", "indicator", "imaging_plane_location"]
        metadata_to_add = list(set(required_metadata) - set(list(self.data['ophys_metadata'].keys())))
        for i in metadata_to_add:
            self.data["ophys_metadata"] = self.add_required_metadata(self.data["ophys_metadata"], i, "ophys")
        # Nom du module où récupérer les infos de métadonnée
        name_module = "image_plane_"

        self.imaging_plane = self.nwbfile.create_imaging_plane(name=self.data['ophys_metadata'].get(name_module + "name"),
                                                               optical_channel=self.optical_channel,
                                                               description=self.data['ophys_metadata'].get(name_module + "description"),
                                                               device=self.device,
                                                               excitation_lambda=self.data['ophys_metadata'].get("excitation_lambda"),
                                                               imaging_rate=self.data['ophys_metadata'].get("imaging_rate"),
                                                               indicator=self.data['ophys_metadata'].get("indicator"),
                                                               location=self.data['ophys_metadata'].get(name_module + "location"),
                                                               manifold=self.data['ophys_metadata'].get("manifold"),
                                                               conversion=self.data['ophys_metadata'].get(name_module + "conversion"),
                                                               unit=self.data['ophys_metadata'].get(name_module + "unit"),
                                                               reference_frame=self.data['ophys_metadata'].get(name_module + "reference_frame"))

        self.nwbfile.add_imaging_plane(self.imaging_plane)

    def cicada_create_imaging_plane(self):

        """ class pynwb.ophys.ImagingPlane(name, optical_channel, description, device, excitation_lambda,
            imaging_rate, indicator, location,
            manifold=None, conversion=None, unit=None, reference_frame=None, parent=None)
        """

        required_metadata = ["imaging_plane_name", "imaging_plane_description", "excitation_lambda",
                             "imaging_rate", "indicator", "imaging_plane_location"]
        metadata_to_add = list(set(required_metadata) - set(list(self.data['ophys_metadata'].keys())))
        for i in metadata_to_add:
            self.data["ophys_metadata"] = self.add_required_metadata(self.data["ophys_metadata"], i, "ophys")
        # Nom du module où récupérer les infos de métadonnée
        name_module = "image_plane_"

        self.imaging_plane = self.nwbfile.create_imaging_plane(name=self.data['ophys_metadata'].get(name_module + "name"),
                                                               optical_channel=self.optical_channel,
                                                               description=self.data['ophys_metadata'].get(name_module + "description"),
                                                               device=self.device,
                                                               excitation_lambda=self.data['ophys_metadata'].get("excitation_lambda"),
                                                               imaging_rate=self.data['ophys_metadata'].get("imaging_rate"),
                                                               indicator=self.data['ophys_metadata'].get("indicator"),
                                                               location=self.data['ophys_metadata'].get(name_module + "location"),
                                                               manifold=self.data['ophys_metadata'].get("manifold"),
                                                               conversion=self.data['ophys_metadata'].get(name_module + "conversion"),
                                                               unit=self.data['ophys_metadata'].get(name_module + "unit"),
                                                               reference_frame=self.data['ophys_metadata'].get(name_module + "reference_frame"))

        self.nwbfile.add_imaging_plane(self.imaging_plane)

    def cicada_create_two_photon_series(self):

        """ class pynwb.ophys.TwoPhotonSeries(name, imaging_plane,
            data=None, unit=None, format=None, field_of_view=None, pmt_gain=None, scan_line_rate=None,
            external_file=None, starting_frame=None, bits_per_pixel=None, dimension=[nan], resolution=0.0,
            conversion=1.0, timestamps=None, starting_time=None, rate=None, comments='no comments',
            description='no description', control=None, control_description=None, parent=None)
        """

        required_metadata = ["two_photons_name"]
        metadata_to_add = list(set(required_metadata) - set(list(self.data['ophys_metadata'].keys())))
        for i in metadata_to_add:
            self.data["ophys_metadata"] = self.add_required_metadata(self.data["ophys_metadata"], i, "ophys")
        # Nom du module où récupérer les infos de métadonnée
        name_module = "two_photon_"


        data_to_store = None

        self.movie_two_photon = TwoPhotonSeries(name=self.data['ophys_metadata'].get(name_module + "name"),
                                                imaging_plane=self.imaging_plane,
                                                data=data_to_store,
                                                unit=self.data['ophys_metadata'].get(name_module + "unit"),
                                                format=self.data['ophys_metadata'].get(name_module + "format"),
                                                field_of_view=self.data['ophys_metadata'].get(name_module + "field_of_view"),
                                                pmt_gain=self.data['ophys_metadata'].get(name_module + "pmt_gain"),
                                                scan_line_rate=self.data['ophys_metadata'].get(name_module + "scan_line_rate"),
                                                external_file=self.data['ophys_metadata'].get(name_module + "external_file"),
                                                starting_frame=self.data['ophys_metadata'].get(name_module + "starting_frame"),
                                                bits_per_pixel=self.data['ophys_metadata'].get(name_module + "bits_per_pixel"),
                                                dimension=self.data['ophys_metadata'].get(name_module + "dimension"),
                                                resolution=self.data['ophys_metadata'].get(name_module + "resolution"),
                                                conversion=self.data['ophys_metadata'].get(name_module + "conversion"),
                                                timestamps=self.data['ophys_metadata'].get(name_module + "timestamps"),
                                                starting_time=self.data['ophys_metadata'].get(name_module + "starting_time"),
                                                rate=self.data['ophys_metadata'].get(name_module + "rate"),
                                                comments=self.data['ophys_metadata'].get(name_module + "comments"),
                                                description=self.data['ophys_metadata'].get(name_module + "description"),
                                                control=self.data['ophys_metadata'].get(name_module + "control"),
                                                control_description=self.data['ophys_metadata'].get(name_module + "control_description"),
                                                parent=self.data['ophys_metadata'].get(name_module + "parent"))

        self.nwbfile.add_acquisition(self.movie_two_photon)

    def cicada_create_motion_correction(self):

        """  class pynwb.ophys.MotionCorrection(corrected_images_stacks={}, name='MotionCorrection')
        """


        # Nom du module où récupérer les infos de métadonnée
        name_module = "motion_correction_"

        # Récupération des données

        corrected_images_stacks = {}

        self.motion_correction = MotionCorrection(corrected_images_stacks=corrected_images_stacks,
                                                  name=self.data['ophys_metadata'].get(name_module + "name"))

        self.mod.add_data_interface(self.motion_correction)

    def cicada_add_corrected_image_stack(self):

        """ class pynwb.ophys.CorrectedImageStack(corrected, original, xy_translation, name='CorrectedImageStack')
        """

        # Nom du module où récupérer les infos de métadonnée
        name_module = "corrected_image_stack_"

        # Récupération des données

        corrected = None
        original = None
        xy_translation = None

        self.corrected_image_stack = CorrectedImageStack(corrected,
                                                         original,
                                                         xy_translation,
                                                         name=self.data['ophys_metadata'].get(name_module + "name"))

        self.motion_correction.add_corrected_image_stack(self.corrected_image_stack)

    def cicada_add_plane_segmentation(self):

        """ class pynwb.ophys.PlaneSegmentation(description, imaging_plane,
            name=None, reference_images=None, id=None, columns=None, colnames=None)
        """

        required_metadata = ["plane_segmentation_description"]
        metadata_to_add = list(set(required_metadata) - set(list(self.data['ophys_metadata'].keys())))
        for i in metadata_to_add:
            self.data["ophys_metadata"] = self.add_required_metadata(self.data["ophys_metadata"], i, "ophys")


        # Nom du module où récupérer les infos de métadonnée
        name_module = "plane_segmentation_"

        # Récupération des données

        self.plane_segmentation = PlaneSegmentation(description=self.data['ophys_metadata'].get(name_module + "description"),
                                                    imaging_plane=self.imaging_plane,
                                                    name=self.data['ophys_metadata'].get(name_module + "name"),
                                                    reference_images=self.data['ophys_metadata'].get(name_module + "reference_image"),
                                                    id=self.data['ophys_metadata'].get(name_module + "id"),
                                                    columns=self.data['ophys_metadata'].get(name_module + "columns"),
                                                    colnames=self.data['ophys_metadata'].get(name_module + "colnames"))

        self.image_segmentation.add_plane_segmentation(self.plane_segmentation)

    def cicada_add_roi_in_plane_segmentation(self):
        """add_roi(pixel_mask=None, voxel_mask=None, image_mask=None, id=None)
        """


        # Nom du module où récupérer les infos de métadonnée
        name_module = "ROI_n1_"

        # Récupération des données
        # Rien pour l'instant

        self.plane_segmentation.add_roi(pixel_mask=self.data['ophys_metadata'].get(name_module + "pixel_mask"),
                                        voxel_mask=self.data['ophys_metadata'].get(name_module + "voxel_mask"),
                                        image_mask=self.data['ophys_metadata'].get(name_module + "image_mask"),
                                        id=self.data['ophys_metadata'].get(name_module + "id"))

    def cicada_create_roi_table_region_in_plane_segmentation(self):
        """create_roi_table_region(description, region=slice(None, None, None), name='rois')"""

        required_metadata = ["roi_table_description"]
        metadata_to_add = list(set(required_metadata) - set(list(self.data['ophys_metadata'].keys())))
        for i in metadata_to_add:
            self.data["ophys_metadata"] = self.add_required_metadata(self.data["ophys_metadata"], i, "ophys")


        # Nom du module où récupérer les infos de métadonnée
        name_module = "roi_table_region_"

        # Récupération des données
        # Rien pour l'instant

        self.plane_segmentation.create_roi_table_region(description=self.data['ophys_metadata'].get(name_module + "description"),
                                                        region=self.data['ophys_metadata'].get(name_module + "region"),
                                                        name=self.data['ophys_metadata'].get(name_module + "name"))

    def cicada_create_image_segmentation(self):

        """  class pynwb.ophys.ImageSegmentation(plane_segmentations={}, name='ImageSegmentation')
        """


        # Nom du module où récupérer les infos de métadonnée
        name_module = "image_segmentation_"

        # Récupération des données

        plane_segmentations={}

        self.image_segmentation = ImageSegmentation(plane_segmentations=plane_segmentations,
                                                    name=self.data['ophys_metadata'].get(name_module + "name"))

        self.mod.add_data_interface(self.image_segmentation)

    def cicada_create_fluorescence(self):

        """   class pynwb.ophys.Fluorescence(roi_response_series={}, name='Fluorescence')
        """


        # Nom du module où récupérer les infos de métadonnée
        name_module = "fluorescence_"

        # Récupération des données

        roi_response_series = {}

        self.fluorescence = Fluorescence(roi_response_series=roi_response_series,
                                         name=self.data['ophys_metadata'].get(name_module + "name"))

        self.mod.add_data_interface(self.fluorescence)

    def cicada_create_DfOverF(self):

        """   class pynwb.ophys.DfOverF(roi_response_series={}, name='DfOverF')
        """


        # Nom du module où récupérer les infos de métadonnée
        name_module = "DfOverF_"

        # Récupération des données

        roi_response_series = {}

        self.DfOverF = DfOverF(roi_response_series=roi_response_series,
                               name=self.data['ophys_metadata'].get(name_module + "name"))

        self.mod.add_data_interface(self.DfOverF)

    def cicada_add_roi_response_series(self,module):

        """  class pynwb.ophys.RoiResponseSeries(name, data, unit, rois,
             resolution=0.0, conversion=1.0, timestamps=None, starting_time=None, rate=None, comments='no comments',
             description='no description', control=None, control_description=None, parent=None)
        """

        required_metadata = ["roi_response_name", "roi_response_unit"]
        metadata_to_add = list(set(required_metadata) - set(list(self.data['ophys_metadata'].keys())))
        for i in metadata_to_add:
            self.data["ophys_metadata"] = self.add_required_metadata(self.data["ophys_metadata"], i, "ophys")

        # Nom du module où récupérer les infos de métadonnée
        name_module = "roi_response_series_"

        # Récupération des données

        data_to_store = None
        rois = None

        roi_response_series = RoiResponseSeries(name=self.data['ophys_metadata'].get(name_module + "name"),
                                                data=data_to_store,
                                                unit=self.data['ophys_metadata'].get(name_module + "unit"),
                                                rois=rois,
                                                resolution=self.data['ophys_metadata'].get(name_module + "resolution"),
                                                conversion=self.data['ophys_metadata'].get(name_module + "conversion"),
                                                timestamps=self.data['ophys_metadata'].get(name_module + "timestamp"),
                                                starting_time=self.data['ophys_metadata'].get(name_module + "starting_time"),
                                                rate=self.data['ophys_metadata'].get(name_module + "rate"),
                                                comments=self.data['ophys_metadata'].get(name_module + "comments"),
                                                description=self.data['ophys_metadata'].get(name_module + "description"),
                                                control=self.data['ophys_metadata'].get(name_module + "control"),
                                                control_description=self.data['ophys_metadata'].get(name_module + "control_description"),
                                                parent=self.data['ophys_metadata'].get(name_module + "parent"))

        module.add_roi_response_series(roi_response_series)

    def find_roi(self):

        # Chemin du dossier suite2p
        data_path = "C:/Users/François/Documents/dossier François/Stage INMED/" \
                    "Programmes/Godly Ultimate Interface/NWB/exp2nwb-master/src/suite2p"
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
            # coord.append(np.array(list_points_coord).transpose())

            # La suite permet d'avoir uniquement les contours (sans les pixels intérieurs)

            # ATTENTION ! Il faut : from shapely.geometry import MultiPoint, LineString
            convex_hull = MultiPoint(list_points_coord).convex_hull
            if isinstance(convex_hull, LineString):
                coord_shapely = MultiPoint(list_points_coord).convex_hull.coords
            else:
                coord_shapely = MultiPoint(list_points_coord).convex_hull.exterior.coords
            coord.append(np.array(coord_shapely).transpose())

        self.suite2p_data["coord"] = coord  # Contient la liste des pixels inclus dans chaque ROI




if __name__ == '__main__':
    new = Preprocessing()
    Preprocessing.load_yaml(new)
    with NWBHDF5IO('ophys_example.nwb', 'w') as io:
        io.write(new.nwbfile)
