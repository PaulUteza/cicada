from qtpy.QtWidgets import *
from qtpy.QtCore import QAbstractItemModel, QModelIndex, Qt
# from qtpy import QtCore, QtGui
from cicada.analysis.cicada_cells_test import CicadaCellsTest


class TreeItem(object):
    # TODO: add a function that allows to update all analyses function contained in the tree
    #  given them the new data and data_format, and using check_data deactivate the a given analysis
    def __init__(self, cicada_analysis=None, parent=None):
        self.parent_item = parent
        self.item_analysis = cicada_analysis
        if self.item_analysis is None:
            # then we define the header
            self.item_data = ("Analysis", "Description")
        else:
            self.item_data = (self.item_analysis.name, self.item_analysis.short_description)
        self.child_items = []

    def append_child(self, item):
        self.child_items.append(item)

    def child(self, row):
        return self.child_items[row]

    def child_count(self):
        return len(self.child_items)

    def column_count(self):
        return len(self.item_data)

    def data(self, column):
        try:
            return self.item_data[column]
        except IndexError:
            return None

    def parent(self):
        return self.parent_item

    def row(self):
        if self.parent_item:
            return self.parent_item.child_items.index(self)

        return 0


class QAnalysisTreeView(QTreeView):
    def __init__(self, parent = None):
        QTreeView.__init__(self)


class QAnalysisTreeModel(QAbstractItemModel):
    def __init__(self, tree_item, parent=None):
        super(QAnalysisTreeModel, self).__init__(parent)

        self.rootItem = tree_item

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().column_count()
        else:
            return self.rootItem.column_count()

    def data(self, index, role):
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()

        return item.data(index.column())

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.rootItem.data(section)

        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self.rootItem
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent()

        if parent_item == self.rootItem:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_item = self.rootItem
        else:
            parent_item = parent.internalPointer()

        return parent_item.child_count()

    def setupModelData(self, lines, parent):
        parents = [parent]
        indentations = [0]

        number = 0

        while number < len(lines):
            position = 0
            while position < len(lines[number]):
                if lines[number][position] != ' ':
                    break
                position += 1

            lineData = lines[number][position:].trimmed()

            if lineData:
                # Read the column data from the rest of the line.
                columnData = [s for s in lineData.split('\t') if s]

                if position > indentations[-1]:
                    # The last child of the current parent is now the new
                    # parent unless the current parent has no children.

                    if parents[-1].childCount() > 0:
                        parents.append(parents[-1].child(parents[-1].childCount() - 1))
                        indentations.append(position)

                else:
                    while position < indentations[-1] and len(parents) > 0:
                        parents.pop()
                        indentations.pop()

                # Append a new item to the current parent's list of children.
                parents[-1].appendChild(TreeItem(columnData, parents[-1]))

            number += 1

class AnalysisTreeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'analysis tree test'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 240
        self.dataGroupBox = None
        self.dataView = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.dataGroupBox = QGroupBox("Analysis")
        self.dataView = QAnalysisTreeView()
        # self.dataView.setRootIsDecorated(False)
        self.dataView.setAlternatingRowColors(True)

        dataLayout = QHBoxLayout()
        dataLayout.addWidget(self.dataView)
        self.dataGroupBox.setLayout(dataLayout)

        model = self.create_model(self)
        self.dataView.setModel(model)
        # self.add_analysis(model, "sequences", 'Find sequences')
        # self.add_analysis(model, 'assemblies', 'Find assemblies')
        # self.add_analysis(model, 'ISI', 'Interval spikes interval')

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.dataGroupBox)
        self.setLayout(mainLayout)

        self.dataView.expandAll()
        self.show()

    def create_model(self, parent):
        # TODO: a system that list the Analysis Function available in the pipeline
        #  + a system that either read a yaml file or a dir and load automatically analysis function

        # TODO: build a function that takes a list of instance of analysis, and construct the tree according
        #  to their family name

        # TODO: the tree could contain either analysis instance either the name of the Family
        #  and keep count for each family of the number of analysis available

        cells_analysis = CicadaCellsTest()
        root_tree = TreeItem()
        cells_analysis_tree = TreeItem(cicada_analysis=cells_analysis, parent=root_tree)
        cells_analysis = CicadaCellsTest()
        cells_analysis.name = "test_"
        tree_bis = TreeItem(cicada_analysis=cells_analysis, parent=cells_analysis_tree)
        cells_analysis_tree.append_child(tree_bis)
        root_tree.append_child(cells_analysis_tree)

        model = QAnalysisTreeModel(tree_item=root_tree)
        return model
    #
    # def add_analysis(self, model, analysis, description):
    #     model.insertRow(0)
    #     model.setData(model.index(0, 0), analysis)
    #     model.setData(model.index(0, 1), description)


