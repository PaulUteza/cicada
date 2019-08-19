from cicada.preprocessing.convert_to_nwb import ConvertToNWB
from pynwb.ophys import ImageSegmentation, Fluorescence
import numpy as np
from PIL import ImageSequence
import PIL
import PIL.Image as pil_image
import os
from cicada.preprocessing.convert_ci_movie_to_nwb import ConvertCiMovieToNWB


class ConvertSuite2pRoisToNWB(ConvertToNWB):
    """Class to convert ROIs data from Suite2P to NWB
       if raw_traces from Suite2p are available they are loaded.
       Otherwise if the movie is available, build the raw_traces.
       create_roi_response_series
    """

    def __init__(self, nwb_file):
        super().__init__(nwb_file)

    def convert(self, **kwargs):
        """Convert the data and add to the nwb_file

        Args:
            **kwargs: arbitrary arguments
        """

        super().convert(**kwargs)
        if "suite2p_dir" not in kwargs:
            raise Exception(f"'suite2p_dir' argument should be pass to convert "
                            f"function in class {self.__class__.__name__}")
        suite2p_dir = kwargs["suite2p_dir"]

        # looking for the motion_corrected_ci_movie, return None if it doesn't exists
        # TODO: take in consideration the movie is not available
        #  then don't construct image mask and don't build raw-traces, use F.npy is available
        image_series = self.nwb_file.acquisition.get("motion_corrected_ci_movie")

        mod = self.nwb_file.create_processing_module('ophys', 'contains optical physiology processed data')
        img_seg = ImageSegmentation(name="segmentation_suite2p")
        mod.add_data_interface(img_seg)
        imaging_plane = self.nwb_file.get_imaging_plane("my_imgpln")
        # description, imaging_plane, name=None
        ps = img_seg.create_plane_segmentation(description='output from segmenting',
                                               imaging_plane=imaging_plane, name='my_plane_seg',
                                               reference_images=image_series)

        stat = np.load(os.path.join(suite2p_dir, "stat.npy"),
                       allow_pickle=True)
        is_cell = np.load(os.path.join(suite2p_dir, "iscell.npy"),
                          allow_pickle=True)
        # TODO: load f.npy for raw_traces if available

        if image_series.format == "tiff":
            dim_y, dim_x = image_series.data.shape[1:]
            n_frames = image_series.data.shape[0]
            print(f"dim_y, dim_x: {image_series.data.shape[1:]}")
        elif image_series.format == "external":
            im = PIL.Image.open(image_series.external_file[0])
            n_frames = len(list(ImageSequence.Iterator(im)))
            dim_y, dim_x = np.array(im).shape
            print(f"dim_y, dim_x: {np.array(im).shape}")
        else:
            raise Exception(f"Format of calcium movie imaging {image_series.format} not yet implemented")

        n_cells = 0
        # Add rois
        for cell in np.arange(len(stat)):
            if is_cell[cell][0] == 0:
                continue
            n_cells += 1
            pix_mask = [(y, x, 1) for x, y in zip(stat[cell]["xpix"], stat[cell]["ypix"])]
            image_mask = np.zeros((dim_y, dim_x))
            for pix in pix_mask:
                image_mask[pix[0], pix[1]] = pix[2]
            # we can id to identify the cell (int) otherwise it will be incremented at each step
            ps.add_roi(pixel_mask=pix_mask, image_mask=image_mask)

        fl = Fluorescence(name="fluorescence_suite2p")
        mod.add_data_interface(fl)

        rt_region = ps.create_roi_table_region('all cells', region=list(np.arange(n_cells)))
        if format == "external":
            if image_series.external_file[0].endswith(".tiff") or \
                    image_series.external_file[0].endswith(".tif"):
                # TODO: fix this bug, so far external loading, taking in consideration frames_to_add is not possible
                #  either copy the code from ConvertCiMovieToNWB reconstructing frames_to_add from intervals
                #  or find another solution. Another solution would be to put on the yaml as argument
                #  frames_to_add but using the attribute from the ConvertMovie instance. s
                ci_movie = ConvertCiMovieToNWB.load_tiff_movie_in_memory(image_series.external_file[0])
            else:
                raise Exception(f"Calcium imaging format not supported yet {image_series.external_file[0]}")
        else:
            ci_movie = image_series.data
        # TODO: if movie is external, see to load it
        if ci_movie:
            raw_traces = np.zeros((n_cells, ci_movie.shape[0]))
            for cell in np.arange(n_cells):
                img_mask = ps['image_mask'][cell]
                img_mask = img_mask.astype(bool)
                raw_traces[cell, :] = np.mean(ci_movie[:, img_mask], axis=1)
            rrs = fl.create_roi_response_series(name='raw_traces', data=raw_traces, unit='lumens',
                                                rois=rt_region, timestamps=np.arange(n_frames),
                                                description="raw traces")