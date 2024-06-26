import view.resources_rc
from PySide6.QtWidgets import QMainWindow, QPushButton, QButtonGroup, QWidget, QDialog, QApplication
from view.utilitaires import group_buttons, load_ui
from view.choose_invoice import ChooseInvoice


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = load_ui("main")
        self.setCentralWidget(self.ui)
        self.setWindowTitle("Les 7 Royaumes")
        self.setup_ui()

    def setup_ui(self):
        # self.stackedWidget:QStackedWidget = self.findChild(QStackedWidget, 'stackedWidget')
        self.ui.stackedWidget.currentChanged.connect(self.page_changed)
        self.ui.stackedWidget.setCurrentIndex(0)
        self.page = self.ui.stackedWidget.widget(0).objectName()

        self.connect_buttons() # connecter les boutons de changement de page (_btn, _back)

        self.maj_btns = QButtonGroup()
        group_buttons(self.maj_btns, self.findChild(QWidget, "fournisseurs").findChildren(QPushButton))

        self.findChild(QPushButton, 'invoiceItem').clicked.connect(self.choose_invoice)

    def connect_buttons(self):
        self.changePageGroupBtns = QButtonGroup()
        changePageBtns = []
        for index in range(1, self.ui.stackedWidget.count()):
            widget = self.ui.stackedWidget.widget(index).objectName()
            changePageBtns.append(self.findChild(QPushButton, f'{widget}_btn'))
            changePageBtns.append(self.findChild(QPushButton, f'{widget}_back'))
        group_buttons(self.changePageGroupBtns, changePageBtns)
        self.changePageGroupBtns.buttonClicked.connect(self.change_page)

    def change_page(self, button:QPushButton):
        if 'back' in button.objectName():
            self.ui.stackedWidget.setCurrentIndex(0)
        else:
            name = button.objectName().replace('_btn', '')
            widget = self.findChild(QWidget, name)
            self.ui.stackedWidget.setCurrentWidget(widget)

    def page_changed(self, index:int):
        self.page = self.ui.stackedWidget.widget(index).objectName()

    def choose_invoice(self):
        invoices = ['invoice1', 'invoice2', 'invoice3']
        dialog = ChooseInvoice(self, invoices)
        dialog.show()
        if dialog.exec() == QDialog.Accepted:
            print("accepted")

    def closeEvent(self, event):
        QApplication.closeAllWindows()
        event.accept()