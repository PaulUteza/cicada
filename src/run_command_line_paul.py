import argparse
import sys
import io
import os
import ast
from pynwb import NWBHDF5IO
from cicada.preprocessing.utils import get_subfiles, path_leaf
import importlib
import importlib.util


class AnalysisNotExisting(Exception):
    pass

class Logging:
    def __init__(self, path, quiet):
        self.path = path
        self.quiet = quiet
        self.terminal = sys.stdout

    def write(self, text):
        file = open(os.path.join(self.path, "log.out"), "a+")
        file.write(text)
        file.close()
        if not self.quiet:
            self.terminal.write(text)

    def flush(self):
        pass


class ErrLogging:
    def __init__(self, path):
        self.path = path
        self.terminal = sys.stderr

    def write(self, text):

        file = open(os.path.join(self.path, "log.err"), "a+")
        file.write(text)
        file.close()
        self.terminal.write(text)

    def flush(self):
        pass

parser = argparse.ArgumentParser()

parser.add_argument('-d', '--data', nargs='+', help="Data to analyse, can be a directory containing data"
                                                    " or a file or both")
parser.add_argument('--parameters', nargs='+', help='Parameter of the analysis (i.e : save_formats="png")')

parser.add_argument('--parameters_file', help='YAML file containing parameters')

parser.add_argument('--analysis_list', help="Display a list of all existing analysises", action="store_true")

parser.add_argument('-p', '--path', help="Path to the folder where results will be saved")

parser.add_argument('-a', '--analysis', help="Desired analysis name or absolute path to analysis file")

parser.add_argument('--no_logging', help="Don't create log files", action='store_true')
parser.add_argument('-q', '--quiet', help="Silence output", action='store_true')


args = parser.parse_args()
create_result_dir = ''
data_to_analyse = []
analysis_dict = {}


analysis_files = get_subfiles('cicada/analysis')
for analysis in analysis_files:
    with open(os.path.realpath(os.path.join('cicada/analysis', analysis))) as file:
        node = ast.parse(file.read())
        for n in node.body:
            if isinstance(n, ast.ClassDef):
                analysis_dict.update({n.name: 'cicada.analysis.' + os.path.splitext(path_leaf(file.name))[0]})

analysis_list = [''.join(x) for x in analysis_dict.keys()]
while '' in analysis_list:
    analysis_list.remove('')


if args.analysis_list:
    print("Existing analysises are : ")
    for analysis in analysis_list:
        print(analysis)
    exit()

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
    else:
        if data is not None:
            if '.' not in data:
                print('Dir not found : ' + str(os.path.realpath(data) + '\nIt will be ignored'))
            elif not data.endswith('nwb'):
                print('data with unsupported format found at : ' + str(os.path.realpath(data) +
                                                                       '\nThis file will be ignored'))
            elif not os.path.isfile(os.path.realpath(data)):
                print(str(os.path.realpath(data) + ' not found\nThis file will be ignored'))
            else:
                io = NWBHDF5IO(os.path.realpath(data), 'r')
                nwb_file = io.read()
                if nwb_file.identifier not in [data.identifier for data in data_to_analyse]:
                    data_to_analyse.append(nwb_file)


if not args.analysis:
    raise AnalysisNotExisting("No Analysis given")
else:
    print('The following files will be analysed : ' + str([data.identifier for data in data_to_analyse]))
    if os.path.isfile(args.analysis):
        module = importlib.util.spec_from_file_location(os.path.basename(path_leaf(args.analysis)), args.analysis)
        foo = importlib.util.module_from_spec(module)
        module.loader.exec_module(foo)
        with open(args.analysis) as file:
            node = ast.parse(file.read())
            for n in node.body:
                if isinstance(n, ast.ClassDef):
                    class_name = n.name
        analysis = eval('foo.' + class_name + '()')
        analysis.gui = False
        analysis.set_data(data_to_analyse=data_to_analyse)
        analysis.run_analysis(results_path=args.path)
    else:
        if args.analysis in analysis_list:
            module = importlib.import_module(analysis_dict[args.analysis])
            class_ = getattr(module, args.analysis)
            analysis = class_()
            analysis.gui = False
            analysis.set_data(data_to_analyse=data_to_analyse)
            if not args.no_logging:
                sys.stdout = Logging(args.path, quiet=args.quiet)
                sys.stderr = ErrLogging(args.path)
            analysis.run_analysis(results_path=args.path)
            if not args.no_logging:
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
                try:
                    os.rename(os.path.join(args.path, 'log.out'), os.path.join(analysis.get_results_path(), 'log.out'))
                    os.rename(os.path.join(args.path, 'log.err'), os.path.join(analysis.get_results_path(), 'log.err'))
                except FileNotFoundError:
                    pass

        else:
            raise AnalysisNotExisting("Analysis not found")

if args.quiet:
    sys.stdout = sys.__stdout__
