from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QDialog, QMessageBox, QDateEdit
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QDate
from sqlalchemy import or_
from db import Session, Company, JobName, Document, Address, Employee

class AddEmployeeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Имя")

        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Фамилия")

        self.middle_name_input = QLineEdit()
        self.middle_name_input.setPlaceholderText("Отчество")

        self.series_input = QLineEdit()
        self.series_input.setPlaceholderText("Серия паспорта")

        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("Номер паспорта")

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Адрес проживания")

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Телефон")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")

        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())

        self.company_input = QComboBox()
        self.jobname_input = QComboBox()

        session = Session()
        self.companies = session.query(Company).all()
        self.jobs = session.query(JobName).all()
        for c in self.companies:
            self.company_input.addItem(c.name, c.id)
        for j in self.jobs:
            self.jobname_input.addItem(j.name, j.id)

        inputs = [
            self.last_name_input, self.name_input, self.middle_name_input,
            self.series_input, self.number_input, self.address_input,
            self.phone_input, self.email_input, self.start_date_input,
            self.company_input, self.jobname_input
        ]

        for widget in inputs:
            layout.addWidget(widget)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_employee)
        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.reject)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.back_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def save_employee(self):
        try:
            session = Session()
            doc = Document(series=self.series_input.text(), number=self.number_input.text())
            session.add(doc)
            session.commit()

            addr = Address(address=self.address_input.text())
            session.add(addr)
            session.commit()

            emp = Employee(
                name=self.name_input.text(),
                last_name=self.last_name_input.text(),
                middlename=self.middle_name_input.text(),
                document_id=doc.id,
                address_id=addr.id,
                company_id=self.company_input.currentData(),
                jobname_id=self.jobname_input.currentData(),
                phone=self.phone_input.text(),
                email=self.email_input.text(),
                start_date=self.start_date_input.date().toPython()
            )
            session.add(emp)
            session.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {e}")


class EditEmployeeDialog(AddEmployeeDialog):
    def __init__(self, employee_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование сотрудника")
        self.setWindowIcon(QIcon("./logo.png"))
        self.employee_id = employee_id
        self.load_employee_data()

    def load_employee_data(self):
        session = Session()
        emp = session.query(Employee).get(self.employee_id)

        self.name_input.setText(emp.name)
        self.last_name_input.setText(emp.last_name)
        self.middle_name_input.setText(emp.middlename)
        self.series_input.setText(emp.document.series)
        self.number_input.setText(emp.document.number)
        self.address_input.setText(emp.address.address)
        self.phone_input.setText(emp.phone)
        self.email_input.setText(emp.email)
        self.start_date_input.setDate(emp.start_date)

        self.company_input.setCurrentIndex(self.company_input.findData(emp.company_id))
        self.jobname_input.setCurrentIndex(self.jobname_input.findData(emp.jobname_id))

    def save_employee(self):
        try:
            session = Session()
            emp = session.query(Employee).get(self.employee_id)

            emp.name = self.name_input.text()
            emp.last_name = self.last_name_input.text()
            emp.middlename = self.middle_name_input.text()
            emp.phone = self.phone_input.text()
            emp.email = self.email_input.text()
            emp.start_date = self.start_date_input.date().toPython()
            emp.company_id = self.company_input.currentData()
            emp.jobname_id = self.jobname_input.currentData()

            emp.document.series = self.series_input.text()
            emp.document.number = self.number_input.text()

            emp.address.address = self.address_input.text()

            session.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении: {e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Сотрудники организации")
        self.setWindowIcon(QIcon("icon.png"))
        self.resize(1100, 600)

        layout = QVBoxLayout()
        control_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по имени...")
        self.search_input.textChanged.connect(self.update_table)

        self.jobname_filter = QComboBox()
        self.jobname_filter.addItem("Все должности", None)
        self.jobname_filter.currentIndexChanged.connect(self.update_table)

 #       self.add_button = QPushButton("Добавить")
 #       self.add_button.clicked.connect(self.open_add_dialog)

        self.edit_button = QPushButton("Редактировать")
        self.edit_button.clicked.connect(self.edit_selected)

        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_selected)

        control_layout.addWidget(self.search_input)
        control_layout.addWidget(self.jobname_filter)
#        control_layout.addWidget(self.add_button)
        control_layout.addWidget(self.edit_button)
        control_layout.addWidget(self.delete_button)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["Фамилия", "Имя", "Отчество", "Серия", "Номер", "Адрес", "Компания", "Должность", "Дата начала работы"])

        layout.addLayout(control_layout)
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_jobname()
        self.update_table()

    def load_jobname(self):
        session = Session()
        jobname = session.query(JobName).all()
        for j in jobname:
            self.jobname_filter.addItem(j.name, j.id)

    def update_table(self):
        session = Session()
        search = self.search_input.text().lower()
        company_id = self.jobname_filter.currentData()

        query = session.query(Employee)
        if search:
            query = query.filter(or_(
                Employee.name.ilike(f"%{search}%"),
                Employee.last_name.ilike(f"%{search}%"),
                Employee.middlename.ilike(f"%{search}%")
            ))
        if company_id:
            query = query.filter(Employee.company_id == company_id)

        employees = query.all()
        self.table.setRowCount(len(employees))

        for row, emp in enumerate(employees):
            self.table.setItem(row, 0, QTableWidgetItem(emp.last_name))
            self.table.setItem(row, 1, QTableWidgetItem(emp.name))
            self.table.setItem(row, 2, QTableWidgetItem(emp.middlename))
            self.table.setItem(row, 3, QTableWidgetItem(emp.document.series))
            self.table.setItem(row, 4, QTableWidgetItem(emp.document.number))
            self.table.setItem(row, 5, QTableWidgetItem(emp.address.address))
            self.table.setItem(row, 6, QTableWidgetItem(emp.company.name))
            self.table.setItem(row, 7, QTableWidgetItem(emp.jobname.name))
            self.table.setItem(row, 8, QTableWidgetItem(str(emp.start_date)))

            self.table.setVerticalHeaderItem(row, QTableWidgetItem(str(emp.id)))

    def get_selected_employee_id(self):
        selected = self.table.currentRow()
        if selected < 0:
            return None
        header_item = self.table.verticalHeaderItem(selected)
        if header_item:
            return int(header_item.text())
        return None

    # def open_add_dialog(self):
    #     dialog = addEmployeeDialog(self)
    #     if dialog.exec():
    #         self.update_table()

    def edit_selected(self):
        employee_id = self.get_selected_employee_id()
        if employee_id is None:
            QMessageBox.warning(self, "Редактирование", "Выберите сотрудника для редактирования")
            return

        dialog = EditEmployeeDialog(employee_id, self)
        if dialog.exec():
            self.update_table()

    def delete_selected(self):
        employee_id = self.get_selected_employee_id()
        if employee_id is None:
            QMessageBox.warning(self, "Удаление", "Выберите сотрудника для удаления")
            return

        confirm = QMessageBox.question(
            self, "Подтверждение", "Удалить выбранного сотрудника?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            session = Session()
            employee = session.query(Employee).get(employee_id)
            if employee:
                session.delete(employee)
                session.commit()
                self.update_table()
            else:
                QMessageBox.critical(self, "Ошибка", "Сотрудник не найден в базе данных")

