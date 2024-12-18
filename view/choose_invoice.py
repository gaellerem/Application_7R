from PySide6.QtWidgets import QDialog, QCheckBox, QLabel, QWidget, QHBoxLayout
from PySide6.QtCore import Qt
from utilitaires.ui import load_ui


class ChooseInvoice(QDialog):
    def __init__(self, parent, invoices):
        super().__init__()
        self.ui = load_ui("choose_invoice", parent)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.ui)
        self.setWindowTitle("Factures non reçues")
        self.checkboxes = []
        self.setup_ui(invoices)
        self.ui.confirm.clicked.connect(self.accept)

    def setup_ui(self, invoices):
        self.contentWidget = self.findChild(QWidget, "content")
        for invoice in reversed(invoices):
            layout = QHBoxLayout()
            label = QLabel(invoice)
            checkbox = QCheckBox()
            layout.addWidget(label)
            layout.addWidget(checkbox, alignment=Qt.AlignCenter)
            self.contentWidget.layout().addLayout(layout)
            self.checkboxes.append((invoice, checkbox))

    def get_checked_invoices(self):
        checked_invoices = [invoice for invoice,
                            checkbox in self.checkboxes if checkbox.isChecked()]
        return checked_invoices
