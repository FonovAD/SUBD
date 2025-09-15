import sys
import psycopg2
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidgetItem,
                             QHeaderView, QMessageBox, QDialog, QVBoxLayout,
                             QLabel, QLineEdit, QDialogButtonBox)
from PyQt6.QtCore import Qt
from MainForm3 import Ui_MainWindow
from config import DB_CONFIG

class DatabaseManager:
    def __init__(self):
        # Подключение к базе данных
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            print("Успешное подключение к базе данных!")
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            raise

    def get_table_data(self, table_name):
        """Получить данные из конкретной таблицы"""
        cursor = self.connection.cursor()
        columns = self.get_columns_names(table_name)
        cursor.execute(f'SELECT * FROM "{table_name}" ORDER BY {columns[0]}')
        data = cursor.fetchall()
        cursor.close()
        return data

    def get_columns_names(self, table_name):
        """Получить названия столбцов таблицы"""
        cursor = self.connection.cursor()
        cursor.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        """)
        columns = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return columns

    def insert_record(self, table_name, data):
        """Добавить новую запись в таблицу"""
        cursor = self.connection.cursor()
        columns = self.get_columns_names(table_name)

        # Формируем SQL запрос
        placeholders = ', '.join(['%s'] * len(data)) # Создание строки с плейсхолдерами (метка для динамической вставки данных) для параметров
        columns_str = ', '.join(columns)

        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    def update_record(self, table_name, record_id, data):
        """Обновить запись в таблице"""
        cursor = self.connection.cursor()
        columns = self.get_columns_names(table_name)

        # Формируем SQL запрос
        set_clause = ', '.join([f"{col} = %s" for col in columns[1:]]) #Пропускаем первый столбец (ID), column1 = %s, column2 = %s...
        query = f"UPDATE {table_name} SET {set_clause} WHERE {columns[0]} = %s"

        # Добавляем ID в конец данных для условия WHERE
        data_with_id = data + [record_id]

        cursor.execute(query, data_with_id)
        self.connection.commit()
        cursor.close()

    def delete_record(self, table_name, record_id):
        """Удалить запись из таблицы"""
        cursor = self.connection.cursor()
        columns = self.get_columns_names(table_name)

        query = f"DELETE FROM {table_name} WHERE {columns[0]} = %s"

        cursor.execute(query, (record_id,))
        self.connection.commit()
        cursor.close()


class EditDialog(QDialog):
    """Диалоговое окно для добавления/редактирования записей"""

    def __init__(self, table_name, columns, data=None, parent=None): # создаем новый экземпляр класса
        super().__init__(parent) # Вызов конструктора родительского класса QDialog
        self.table_name = table_name
        self.columns = columns
        self.data = data # Сохранение данных для редактирования
        self.setup_ui() # Вызов метода создания интерфейса

    def setup_ui(self):
        self.setWindowTitle(f"Редактирование: {self.table_name}")
        self.layout = QVBoxLayout() # Создание вертикального компоновщика

        self.fields = {} # Словарь для хранения полей ввода (ключ - имя столбца, значение - поле ввода)
        for i, column in enumerate(self.columns):
            label = QLabel(column) # Создание метки с именем столбца
            self.layout.addWidget(label) # Добавление метки в компоновщик

            field = QLineEdit() # Создание поля ввода
            if self.data and i < len(self.data):
                field.setText(str(self.data[i])) # Установка текста в поле ввода из переданных данных
            self.fields[column] = field
            self.layout.addWidget(field)

        # Создание кнопок OK и Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept) # Подключение сигнала нажатия к методу
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

        self.setLayout(self.layout) # Установка компоновщика для диалогового окна

    def get_data(self):
        """Получить данные из полей ввода"""
        return [field.text() for field in self.fields.values()]


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Настройка интерфейса
        self.setWindowTitle("Управление экспертизой проектов")
        self.setMinimumSize(800, 600)

        # Настройка таблицы
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch) # Установка режима растягивания столбцов по ширине таблицы

        # Подключение к базе данных
        try:
            self.db = DatabaseManager()
            self.connect_menu_actions()
            self.connect_button_actions()  # Подключаем действия кнопок
            self.statusbar.showMessage("Подключение к базе данных успешно")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться к базе данных: {str(e)}")
            self.close()

        # Текущая таблица
        self.current_table = None

    def connect_menu_actions(self):
        """Связываем пункты меню с соответствующими таблицами"""
        # Связываем действие "Эксперты" с таблицей expert
        self.actionExperts.triggered.connect(lambda: self.show_table("expert"))

        # Связываем действие "ГРНТИ" с таблицей grnti_classifier
        self.actionGRNTI.triggered.connect(lambda: self.show_table("grnti_classifier"))

        # Связываем действие "Регионы" с таблицей reg_obl_city
        self.actionRegions.triggered.connect(lambda: self.show_table("reg_obl_city"))

    def connect_button_actions(self):
        """Связываем кнопки с функциями"""
        self.addButton.clicked.connect(self.add_record)
        self.editButton.clicked.connect(self.edit_record)
        self.deleteButton.clicked.connect(self.delete_record)

    def show_table(self, table_name):
        """Отображение содержимого таблицы"""
        try:
            # Сохраняем текущую таблицу
            self.current_table = table_name

            # Получаем данные и заголовки столбцов
            data = self.db.get_table_data(table_name)
            columns = self.db.get_columns_names(table_name)

            # Очищаем таблицу перед загрузкой новых данных
            self.table_widget.clear()

            # Настраиваем таблицу
            self.table_widget.setColumnCount(len(columns))
            self.table_widget.setHorizontalHeaderLabels(columns)
            self.table_widget.setRowCount(len(data))

            # Заполняем таблицу данными
            for row_num, row_data in enumerate(data):
                for col_num, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    self.table_widget.setItem(row_num, col_num, item)

            self.statusbar.showMessage(f"Загружена таблица: {table_name}. Записей: {len(data)}")

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить таблицу: {str(e)}")

    def add_record(self):
        """Добавить новую запись"""
        if not self.current_table:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите таблицу")
            return

        columns = self.db.get_columns_names(self.current_table)
        dialog = EditDialog(self.current_table, columns)

        if dialog.exec(): # Если нажали OK в диалоговом окне
            data = dialog.get_data()
            try:
                self.db.insert_record(self.current_table, data)
                self.show_table(self.current_table)  # Обновляем таблицу
                self.statusbar.showMessage("Запись успешно добавлена")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось добавить запись: {str(e)}")

    def edit_record(self):
        """Редактировать выбранную запись"""
        if not self.current_table:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите таблицу")
            return

        selected_row = self.table_widget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования")
            return

        # Получаем данные выбранной строки
        row_data = []
        for col in range(self.table_widget.columnCount()):
            item = self.table_widget.item(selected_row, col)
            row_data.append(item.text() if item else "")

        columns = self.db.get_columns_names(self.current_table)
        dialog = EditDialog(self.current_table, columns, row_data)

        if dialog.exec():
            data = dialog.get_data()
            try:
                record_id = row_data[0]  # ID записи (первый столбец)
                self.db.update_record(self.current_table, record_id, data[1:])
                self.show_table(self.current_table)  # Обновляем таблицу
                self.statusbar.showMessage("Запись успешно обновлена")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось обновить запись: {str(e)}")

    def delete_record(self):
        """Удалить выбранную запись"""
        if not self.current_table:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите таблицу")
            return

        selected_row = self.table_widget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления")
            return

        # Получаем ID выбранной записи (первый столбец)
        record_id = self.table_widget.item(selected_row, 0).text()

        # Подтверждение удаления
        reply = QMessageBox.question(self, "Подтверждение",
                                     "Вы уверены, что хотите удалить эту запись?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_record(self.current_table, record_id)
                self.show_table(self.current_table) 
                self.statusbar.showMessage("Запись успешно удалена")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить запись: {str(e)}")

    def closeEvent(self, event):
        """Закрытие соединения с базой данных при выходе"""
        if hasattr(self, 'db'):
            self.db.connection.close()
            print("Соединение с базой данных закрыто")
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())