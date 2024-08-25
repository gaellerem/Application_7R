from PySide6.QtCore import QAbstractTableModel, Qt

class DataFrameModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.column_number_to_letter(section)
            elif orientation == Qt.Vertical:
                return str(self._data.index[section])
        return None

    @staticmethod
    def column_number_to_letter(n):
        """Convert column number to Excel-style letters."""
        result = ''
        while n >= 0:
            result = chr(n % 26 + ord('A')) + result
            n = n // 26 - 1
        return result