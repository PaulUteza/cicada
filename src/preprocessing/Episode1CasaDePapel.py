import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

from pynwb import NWBHDF5IO


class Episode1CasaDePapel:
    """
    Required data : path_results, time_str, colors, rasterplot, age, sampling_rate, description

    """
    def __init__(self, nwb_file_path):
        # Dictionnaire pour stocker les données trouvées
        self.data_got = {"path_results": "",
                         "time_str": "",
                         "colors": [],
                         "rasterplot": None,
                         "age": None,
                         "sampling_rate": None,
                         "description": None}

        self.nwb_file_path = nwb_file_path

        io = NWBHDF5IO(self.nwb_file_path, 'r')
        self.nwb_file = io.read()

    # Vérifie que les modules nécessaires sont bien présents
    def check_data(self):

        # TODO : renvoie True/False pour indiquer la présence de chaque module
        #   pour savoir si on peut exécuter la fonction à partir des données présentes dans le NWB

        # Test présence du module Ophys
        try:
            mod = self.nwb_file.get_processing_module(name="ophys")
        except Exception as e:
            print(e)
            raise Exception("pas de module ophys")

        # Test présence de Rasterplot
        try:
            mod.get_data_interface(name="Rasterplot")
        except Exception as e:
            print(e)
            print(mod)
            raise Exception("pas de data interface Rasterplot")

    # Obtient toutes les données nécessaires
    def get_all_data_from_nwb(self):

        root_path = os.path.dirname(self.nwb_file_path)

        # TODO : obtenir les metadata proprement !

        path_results_raw = os.path.join(root_path, "transient_duration")

        time_str = datetime.now().strftime("%Y_%m_%d.%H-%M-%S")
        path_results = path_results_raw + f"{time_str}"

        if not os.path.isdir(path_results):
            os.mkdir(path_results)

        self.data_got["path_results"] = path_results
        self.data_got["time_str"] = time_str

        # Voir pour les couleurs ce qui est utile ou non ...
        self.data_got["colors"] = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c', '#fdbf6f',
                                   '#ff7f00', '#cab2d6', '#6a3d9a', '#ffff99', '#b15928']

        mod = self.nwb_file.get_processing_module(name="ophys")
        rasterplot = mod.get_data_interface(name="Rasterplot")

        self.data_got["rasterplot"] = rasterplot.data

        try:
            age = self.nwb_file.subject.age
            print(age)
        except Exception as e:
            print(e)
            age = input("please add 'age' :")

        self.data_got["age"] = age

        self.data_got["sampling_rate"] = 10

        try:
            description = self.nwb_file.session_id
        except Exception as e:
            print(e)
            description = input("please add 'session_id' :")

        self.data_got["description"] = description

    @staticmethod
    def choice_color(choice="qualitative"): # A voir si c'est utile ou non ...
        # from: http://colorbrewer2.org/?type=sequential&scheme=YlGnBu&n=8
        if choice == "defaut":
            colors = ['#ffffd9', '#edf8b1', '#c7e9b4', '#7fcdbb', '#41b6c4', '#1d91c0', '#225ea8', '#0c2c84']
        # orange ones: http://colorbrewer2.org/?type=sequential&scheme=YlGnBu&n=8#type=sequential&scheme=YlOrBr&n=9
        elif choice == "orange":
            colors = ['#ffffe5', '#fff7bc', '#fee391', '#fec44f', '#fe9929', '#ec7014', '#cc4c02', '#993404', '#662506']
        # diverging, 11 colors : http://colorbrewer2.org/?type=diverging&scheme=RdYlBu&n=11
        elif choice == "diverging":
            colors = ['#a50026', '#d73027', '#f46d43', '#fdae61', '#fee090', '#ffffbf', '#e0f3f8', '#abd9e9',
                      '#74add1', '#4575b4', '#313695']
        # qualitative 12 colors : http://colorbrewer2.org/?type=qualitative&scheme=Paired&n=12
        elif choice == "qualitative":
            colors = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c', '#fdbf6f',
                      '#ff7f00', '#cab2d6', '#6a3d9a', '#ffff99', '#b15928']
        else:
            print("color choice not available")
            colors = None

        return colors

    # Fonction principale qui exécute l'analyse voulue
    def main_analysis(self):

        self.check_data() # On vérifie qu'on peut appliquer la fonction
        self.get_all_data_from_nwb() # On récupère les données

        # On met les données sous la forme (ms_to_analyse, param) pour pouvoir réutiliser
        # les fonctions de main_hippocampal ...
        # Par contre ce sont des dictionnaires et non des classes => remplacement des truc.machin par truc["machin"]
        # dans la suite
        ms = {"spike_nums_dur": self.data_got["rasterplot"],
              "age": self.data_got["age"],
              "sampling_rate": self.data_got["sampling_rate"],
              "description": self.data_got["description"]}
        ms_to_analyse = [ms]

        param = {"path_results": self.data_got["path_results"],
                 "time_str": self.data_got["time_str"],
                 "colors": self.data_got["colors"]}

        colors = self.data_got["colors"]

        self.plot_transient_durations(ms_to_analyse, param, colors=colors)

    # Fonction de main_hippocampal_network_emergence
    def plot_transient_durations(self, ms_to_analyse, param, colors=None, save_formats="pdf"):
        path_results = os.path.join(param["path_results"], "transient_duration")
        if not os.path.isdir(path_results):
            os.mkdir(path_results)
        spike_durations_by_age = dict()
        spike_durations_by_age_avg_by_cell = dict()

        for ms in ms_to_analyse:
            if ms["spike_nums_dur"] is None:
                continue
            # print(f"plot_transient_durations: {ms.description}")
            age_str = "p" + str(ms["age"])
            # list of length n_cells, each element being a list of int representing the duration of the transient
            # in frames
            spike_durations = self.get_spikes_duration_from_raster_dur(spike_nums_dur=ms["spike_nums_dur"])
            distribution_avg_by_cell = []
            distribution_all = []
            if age_str not in spike_durations_by_age:
                spike_durations_by_age[age_str] = []
            if age_str not in spike_durations_by_age_avg_by_cell:
                spike_durations_by_age_avg_by_cell[age_str] = []
            for spike_durations_by_cell in spike_durations:
                if len(spike_durations_by_cell) == 0:
                    continue
                spike_durations_by_cell = [d/ms["sampling_rate"] for d in spike_durations_by_cell]
                distribution_all.extend(spike_durations_by_cell)
                spike_durations_by_age[age_str].extend(spike_durations_by_cell)

                distribution_avg_by_cell.append(np.mean(spike_durations_by_cell))
                spike_durations_by_age_avg_by_cell[age_str].append(np.mean(spike_durations_by_cell))

            self.plot_hist_distribution(distribution_data=distribution_all,
                                        description=f"{ms['description']}_hist_rising_time_durations",
                                        param=param,
                                        path_results=path_results,
                                        tight_x_range=True,
                                        twice_more_bins=False,
                                        xlabel="Duration of rising time (s)", save_formats=save_formats)
            self.plot_hist_distribution(distribution_data=distribution_avg_by_cell,
                                        description=f"{ms['description']}_hist_rising_time_duration_avg_by_cell",
                                        param=param,
                                        path_results=path_results,
                                        tight_x_range=True,
                                        twice_more_bins=True,
                                        xlabel="Average duration of rising time for each cell (s)",
                                        save_formats=save_formats)

        self.box_plot_data_by_age(data_dict=spike_durations_by_age, title="", filename="rising_time_duration_by_age",
                                  y_label="Duration of rising time (s)", colors=colors, with_scatters=False,
                                  path_results=path_results,
                                  param=param, save_formats=save_formats)
        self.box_plot_data_by_age(data_dict=spike_durations_by_age_avg_by_cell, title="",
                                  filename="rising_time_durations_by_age_avg_by_cell",
                                  path_results=path_results,
                                  y_label="Average duration of rising time for each cell (s)", colors=colors,
                                  param=param, save_formats=save_formats)

    # A partir de là c'est que des fonctions appelées par plot_transient_duration
    @staticmethod
    def plot_hist_distribution(distribution_data, description, param, values_to_scatter=None,
                               n_bins = None, use_log=False, x_range=None,
                               labels=None, scatter_shapes=None, colors=None, tight_x_range=False,
                               twice_more_bins=False, background_color="black", labels_color="white",
                               xlabel="", ylabel=None, path_results=None, save_formats="pdf",
                               ax_to_use=None, color_to_use=None, legend_str="", density=False):
        """
        Plot a distribution in the form of an histogram, with option for adding some scatter values
        :param distribution_data:
        :param description:
        :param param:
        :param values_to_scatter:
        :param labels:
        :param scatter_shapes:
        :param colors:
        :param tight_x_range:
        :param twice_more_bins:
        :param xlabel:
        :param ylabel:
        :param save_formats:
        :return:
        """
        distribution = np.array(distribution_data)
        if color_to_use is None:
            hist_color = "blue"
        else:
            hist_color = color_to_use

        if x_range is not None:
            min_range = x_range[0]
            max_range = x_range[1]
        elif tight_x_range:
            max_range = np.max(distribution)
            min_range = np.min(distribution)
        else:
            max_range = 100
            min_range = 0
        weights = (np.ones_like(distribution) / (len(distribution))) * 100
        # weights=None

        if ax_to_use is None:
            fig, ax1 = plt.subplots(nrows=1, ncols=1,
                                    gridspec_kw={'height_ratios': [1]},
                                    figsize=(12, 12))
            ax1.set_facecolor(background_color)
            fig.patch.set_facecolor(background_color)
        else:
            ax1 = ax_to_use
        if n_bins is not None:
            bins = n_bins
        else:
            bins = int(np.sqrt(len(distribution)))
            if twice_more_bins:
                bins *= 2

        if bins > 100:
            edge_color = hist_color
        else:
            edge_color = "white"

        hist_plt, edges_plt, patches_plt = ax1.hist(distribution, bins=bins, range=(min_range, max_range),
                                                    facecolor=hist_color, log=use_log,
                                                    edgecolor=edge_color, label=f"{legend_str}",
                                                    weights=weights, density=density)
        if values_to_scatter is not None:
            scatter_bins = np.ones(len(values_to_scatter), dtype="int16")
            scatter_bins *= -1

            for i, edge in enumerate(edges_plt):
                # print(f"i {i}, edge {edge}")
                if i >= len(hist_plt):
                    # means that scatter left are on the edge of the last bin
                    scatter_bins[scatter_bins == -1] = i - 1
                    break

                if len(values_to_scatter[values_to_scatter <= edge]) > 0:
                    if (i + 1) < len(edges_plt):
                        bool_list = values_to_scatter < edge  # edges_plt[i + 1]
                        for i_bool, bool_value in enumerate(bool_list):
                            if bool_value:
                                if scatter_bins[i_bool] == -1:
                                    new_i = max(0, i - 1)
                                    scatter_bins[i_bool] = new_i
                    else:
                        bool_list = values_to_scatter < edge
                        for i_bool, bool_value in enumerate(bool_list):
                            if bool_value:
                                if scatter_bins[i_bool] == -1:
                                    scatter_bins[i_bool] = i

            decay = np.linspace(1.1, 1.15, len(values_to_scatter))
            for i, value_to_scatter in enumerate(values_to_scatter):
                if i < len(labels):
                    ax1.scatter(x=value_to_scatter, y=hist_plt[scatter_bins[i]] * decay[i], marker=scatter_shapes[i],
                                color=colors[i], s=60, zorder=20, label=labels[i])
                else:
                    ax1.scatter(x=value_to_scatter, y=hist_plt[scatter_bins[i]] * decay[i], marker=scatter_shapes[i],
                                color=colors[i], s=60, zorder=20)
        ax1.legend()

        if tight_x_range:
            ax1.set_xlim(min_range, max_range)
        else:
            ax1.set_xlim(0, 100)
            xticks = np.arange(0, 110, 10)

            ax1.set_xticks(xticks)
            # sce clusters labels
            ax1.set_xticklabels(xticks)
        ax1.yaxis.set_tick_params(labelsize=20)
        ax1.xaxis.set_tick_params(labelsize=20)
        ax1.tick_params(axis='y', colors=labels_color)
        ax1.tick_params(axis='x', colors=labels_color)
        # TO remove the ticks but not the labels
        # ax1.xaxis.set_ticks_position('none')

        if ylabel is None:
            ax1.set_ylabel("Distribution (%)", fontsize=20, labelpad=20)
        else:
            ax1.set_ylabel(ylabel, fontsize=20, labelpad=20)
        ax1.set_xlabel(xlabel, fontsize=20, labelpad=20)

        ax1.xaxis.label.set_color(labels_color)
        ax1.yaxis.label.set_color(labels_color)

        if ax_to_use is None:
            # padding between ticks label and  label axis
            # ax1.tick_params(axis='both', which='major', pad=15)
            fig.tight_layout()

            if isinstance(save_formats, str):
                save_formats = [save_formats]
            if path_results is None:
                path_results = param["path_results"]
            for save_format in save_formats:
                save_format = "png"
                fig.savefig(f'{path_results}/{description}'
                            f'_{param["time_str"]}.{save_format}',
                            format=f"{save_format}",
                            facecolor=fig.get_facecolor())

            plt.close()

    @staticmethod
    def box_plot_data_by_age(data_dict, title, filename,
                             y_label, param, colors=None,
                             path_results=None, y_lim=None,
                             x_label=None, with_scatters=True,
                             scatters_with_same_colors=None,
                             scatter_size=20,
                             scatter_alpha=0.5,
                             n_sessions_dict=None,
                             background_color="black",
                             link_medians=True,
                             color_link_medians="red",
                             labels_color="white",
                             with_y_jitter=None,
                             save_formats="pdf"):
        """

        :param data_dict:
        :param n_sessions_dict: should be the same keys as data_dict, value is an int reprenseing the number of sessions
        that gave those data (N), a n will be display representing the number of poins in the boxplots if n != N
        :param title:
        :param filename:
        :param y_label:
        :param y_lim: tuple of int,
        :param scatters_with_same_colors: scatter that have the same index in the data_dict,, will be colors
        with the same colors, using the list of colors given by scatters_with_same_colors
        :param param: Contains a field name colors used to color the boxplot
        :param save_formats:
        :return:
        """
        fig, ax1 = plt.subplots(nrows=1, ncols=1,
                                gridspec_kw={'height_ratios': [1]},
                                figsize=(12, 12))
        colorfull = (colors is not None)

        median_color = background_color if colorfull else labels_color

        ax1.set_facecolor(background_color)

        fig.patch.set_facecolor(background_color)

        labels = []
        data_list = []
        medians_values = []
        for age, data in data_dict.items():
            data_list.append(data)
            medians_values.append(np.median(data))
            label = age
            if n_sessions_dict is None:
                # label += f"\n(n={len(data)})"
                pass
            else:
                n_sessions = n_sessions_dict[age]
                if n_sessions != len(data):
                    label += f"\n(N={n_sessions}, n={len(data)})"
                else:
                    label += f"\n(N={n_sessions})"
            labels.append(label)

        bplot = plt.boxplot(data_list, patch_artist=colorfull,
                            labels=labels, sym='', zorder=30)  # whis=[5, 95], sym='+'
        # color=["b", "cornflowerblue"],
        # fill with colors

        # edge_color="silver"

        for element in ['boxes', 'whiskers', 'fliers', 'caps']:
            plt.setp(bplot[element], color="white")

        for element in ['means', 'medians']:
            plt.setp(bplot[element], color=median_color)

        if colorfull:
            if colors is None:
                colors = param["colors"][:len(data_dict)]
            else:
                while len(colors) < len(data_dict):
                    colors.extend(colors)
                colors = colors[:len(data_dict)]
            for patch, color in zip(bplot['boxes'], colors):
                patch.set_facecolor(color)
                r, g, b, a = patch.get_facecolor()
                # for transparency purpose
                patch.set_facecolor((r, g, b, 0.8))

        if with_scatters:
            for data_index, data in enumerate(data_list):
                # Adding jitter
                x_pos = [1 + data_index + ((np.random.random_sample() - 0.5) * 0.5) for x in np.arange(len(data))]

                if with_y_jitter is not None:
                    y_pos = [value + (((np.random.random_sample() - 0.5) * 2) * with_y_jitter) for value in data]
                else:
                    y_pos = data
                font_size = 3
                colors_scatters = []
                if scatters_with_same_colors is not None:
                    while len(colors_scatters) < len(y_pos):
                        colors_scatters.extend(scatters_with_same_colors)
                else:
                    colors_scatters = [colors[data_index]]
                ax1.scatter(x_pos, y_pos,
                            color=colors_scatters[:len(y_pos)],
                            alpha=scatter_alpha,
                            marker="o",
                            edgecolors=background_color,
                            s=scatter_size, zorder=1)
        if link_medians:
            ax1.plot(np.arange(1, len(medians_values)+1), medians_values,
                     zorder=36, color=color_link_medians, linewidth=2)

        # plt.xlim(0, 100)
        plt.title(title)

        ax1.set_ylabel(f"{y_label}", fontsize=30, labelpad=20)
        if y_lim is not None:
            ax1.set_ylim(y_lim[0], y_lim[1])
        if x_label is not None:
            ax1.set_xlabel(x_label, fontsize=30, labelpad=20)
        ax1.xaxis.label.set_color(labels_color)
        ax1.yaxis.label.set_color(labels_color)

        ax1.yaxis.set_tick_params(labelsize=20)
        ax1.xaxis.set_tick_params(labelsize=5)
        ax1.tick_params(axis='y', colors=labels_color)
        ax1.tick_params(axis='x', colors=labels_color)
        xticks = np.arange(1, len(data_dict) + 1)
        ax1.set_xticks(xticks)
        # removing the ticks but not the labels
        ax1.xaxis.set_ticks_position('none')
        # sce clusters labels
        ax1.set_xticklabels(labels)

        # padding between ticks label and  label axis
        # ax1.tick_params(axis='both', which='major', pad=15)
        fig.tight_layout()
        # adjust the space between axis and the edge of the figure
        # https://matplotlib.org/faq/howto_faq.html#move-the-edge-of-an-axes-to-make-room-for-tick-labels
        # fig.subplots_adjust(left=0.2)

        if isinstance(save_formats, str):
            save_formats = [save_formats]

        plt.rcParams['pdf.fonttype'] = 42
        plt.rcParams['font.family'] = 'Calibri'

        if path_results is None:
            path_results = param["path_results"]
        for save_format in save_formats:
            save_format = "png"
            fig.savefig(f'{path_results}/{filename}'
                        f'_{param["time_str"]}.{save_format}',
                        format=f"{save_format}",
                        facecolor=fig.get_facecolor())

        plt.close()

    @staticmethod
    def get_spikes_duration_from_raster_dur(spike_nums_dur):
        spike_durations = []
        for cell_id, spikes_time in enumerate(spike_nums_dur):
            if len(spikes_time) == 0:
                spike_durations.append([])
                continue
            n_times = len(spikes_time)
            d_times = np.diff(spikes_time)
            # show the +1 and -1 edges
            pos = np.where(d_times == 1)[0] + 1
            neg = np.where(d_times == -1)[0] + 1

            if (pos.size == 0) and (neg.size == 0):
                if len(np.nonzero(spikes_time)[0]) > 0:
                    spike_durations.append([n_times])
                else:
                    spike_durations.append([])
            elif pos.size == 0:
                # i.e., starts on an spike, then stops
                spike_durations.append([neg[0]])
            elif neg.size == 0:
                # starts, then ends on a spike.
                spike_durations.append([n_times - pos[0]])
            else:
                if pos[0] > neg[0]:
                    # we start with a spike
                    pos = np.insert(pos, 0, 0)
                if neg[-1] < pos[-1]:
                    #  we end with aspike
                    neg = np.append(neg, n_times - 1)
                # NOTE: by this time, length(pos)==length(neg), necessarily
                h = np.matrix([pos, neg])
                if np.any(h):
                    goodep = np.array(h[1, :] - h[0, :]).flatten()
                    spike_durations.append(list(goodep))

        return spike_durations
