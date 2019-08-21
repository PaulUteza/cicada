import argparse
import sys
import io
import os
from cicada.analysis.cicada_psth_analysis import CicadaPsthAnalysis
from pynwb import NWBHDF5IO
from cicada.preprocessing.utils import get_subfiles


class AnalysisNotExisting(Exception):
    pass

parser = argparse.ArgumentParser()

parser.add_argument('-d', '--data', nargs='+', help="Data to analyse, can be a directory containing data"
                                                    " or a file or both")

parser.add_argument('-p', '--path', help="Path to the folder where results will be saved")

# D'une liste en dur ? Le nom de la classe ?
parser.add_argument('-a', '--analysis', help="Desired analysis name")

parser.add_argument('-q', '--quiet', help="Silence output", action='store_true')


args = parser.parse_args()
create_result_dir = ''
data_to_analyse = []

if args.quiet:
    text_trap = io.StringIO()
    sys.stdout = text_trap


if not args.path:
    raise NotADirectoryError("Result folder not given")

result_path = os.path.realpath(args.path)
if not os.path.isdir(os.path.realpath(args.path)):
    print('Directory not found')
    while create_result_dir != 'n' and create_result_dir != 'y':
        create_result_dir = input('Do you want to create it ? [y/n] (Default : No) ')
        if create_result_dir == 'n' or create_result_dir == '':
            exit('No result folder, exiting')
        elif create_result_dir == 'y':
            print('Result folder created at : ' + str(os.path.realpath(args.path)))
            os.mkdir(args.path)


for data in args.data:
    if os.path.isdir(os.path.realpath(data)):
        files_in_dir = get_subfiles(os.path.realpath(data))
        for file in files_in_dir:
            if not file.endswith('nwb'):
                print('File with unsupported format found at : ' + str(os.path.realpath(os.path.join(data, file)) +
                                                                                        '\nThis file will be ignored'))
            else:
                args.data.append((os.path.join(data, file)))
        # args.data.remove(data)
    else:
        if data is not None:
            if not data.endswith('nwb'):
                print('data with unsupported format found at : ' + str(os.path.realpath(data) +
                                                                       '\nThis file will be ignored'))
            elif not os.path.isfile(os.path.realpath(data)):
                print(str(os.path.realpath(data) +' not found\nThis file will be ignored'))
            else:
                io = NWBHDF5IO(os.path.realpath(data), 'r')
                nwb_file = io.read()
                if nwb_file.identifier not in [data.identifier for data in data_to_analyse]:
                    data_to_analyse.append(nwb_file)


if not args.analysis:
    raise AnalysisNotExisting("No Analysis given")
else:
    print('The following files will be analysed : ' + str([data.identifier for data in data_to_analyse]))
    if args.analysis.lower() == 'psth':
        analysis = CicadaPsthAnalysis()
        analysis.gui = False
        analysis.set_data(data_to_analyse=data_to_analyse)
        analysis.run_analysis(results_path=args.path)
    else:
        raise AnalysisNotExisting("Analysis not found")