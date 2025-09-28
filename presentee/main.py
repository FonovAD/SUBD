import sys
import psycopg2
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidgetItem,
                             QHeaderView, QMessageBox, QDialog, QVBoxLayout,
                             QLabel, QLineEdit, QDialogButtonBox)
from PySide6.QtCore import Qt
# from MainForm3 import Ui_MainWindow
from config import DB_CONFIG
from datetime import datetime
from MainFormlayout import Ui_MainWindow

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

    def __init__(self, table_name, columns, data=None, parent=None, display_names=None, date_columns=None):
        super().__init__(parent)
        self.table_name = table_name
        self.columns = columns
        self.data = data
        self.display_names = display_names or {}
        self.date_columns = date_columns or []  # Список колонок с датами
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(f"Редактирование: {self.table_name}")
        self.layout = QVBoxLayout()

        self.fields = {}
        for i, column in enumerate(self.columns):
            # Используем русское название, если есть
            label_text = self.display_names.get(column, column)
            label = QLabel(label_text)
            self.layout.addWidget(label)

            field = QLineEdit()
            if self.data and i < len(self.data):
                # Если это колонка с датой, форматируем для отображения
                if column in self.date_columns:
                    formatted_date = DateValidator.format_date_for_display(str(self.data[i]))
                    field.setText(formatted_date if formatted_date else str(self.data[i]))
                else:
                    field.setText(str(self.data[i]))
            else:
                field.setText("")  # Пустое значение для новой записи

            if self.data and i == 0:  # Первое поле (ID) только для чтения при редактировании
                field.setReadOnly(True)

            self.fields[column] = field
            self.layout.addWidget(field)

        # Добавляем подсказку о форматах дат, если есть даты в форме
        if self.date_columns:
            hint_label = QLabel(f"Поддерживаемые форматы дат: {DateValidator.get_format_examples()}")
            hint_label.setStyleSheet("color: gray; font-size: 10px;")
            self.layout.addWidget(hint_label)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

        self.setLayout(self.layout)

    def validate_and_accept(self):
        """Проверяет валидность данных перед принятием"""
        # Проверяем даты
        for column in self.date_columns:
            if column in self.fields:
                date_value = self.fields[column].text().strip()
                if date_value:  # Если поле не пустое
                    if not DateValidator.parse_date(date_value):
                        QMessageBox.warning(
                            self,
                            "Неверный формат даты",
                            f"Поле '{self.display_names.get(column, column)}' содержит неверный формат даты.\n\n"
                            f"Поддерживаемые форматы:\n{DateValidator.get_format_examples()}"
                        )
                        return

        self.accept()

    def get_data(self):
        """Получить данные из полей ввода с преобразованием дат"""
        result = []
        for column in self.columns:
            if column in self.fields:
                value = self.fields[column].text()
                # Преобразуем даты в формат БД
                if column in self.date_columns:
                    if value and value.strip():  # Проверяем, что строка не пустая
                        db_date = DateValidator.format_date_for_db(value.strip())
                        result.append(db_date if db_date else value)
                    else:
                        result.append("")  # Пустая строка для пустых дат
                else:
                    result.append(value)
            else:
                result.append("")
        return result


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.check_layout()
        # self.setup_layout()

        # Настройка интерфейса
        self.setWindowTitle("Управление экспертизой проектов")
        self.setMinimumSize(800, 600)
        # Настраиваем адаптивный layout

        # Устанавливаем начальный размер окна (можно настроить под ваш экран)
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        self.resize(int(screen_geometry.width() * 0.8), int(screen_geometry.height() * 0.7))

        # Словари для русских названий столбцов
        self.column_display_names = {
            'expert': {
                'id': 'ID',
                'name': 'ФИО эксперта',
                'region': 'Регион',
                'city': 'Город',
                'grnti_code': 'Код ГРНТИ',
                'keywords': 'Ключевые слова',
                'participation_count': 'Количество участий',
                'input_date': 'Дата добавления'
            },
            'grnti_classifier': {
                'codrub': 'Код ГРНТИ',
                'description': 'Название рубрики'
            },
            'reg_obl_city': {
                'id': 'ID',
                'region': 'Федеральный округ',
                'oblname': 'Субъект федерации',
                'city': 'Город'
            },
            'expert_grnti': {
                'id': 'ID',
                'rubric': 'Рубрика',
                'subrubric': 'Сабрубрика',
                'siscipline': 'Дисциплина'
            }
        }

        # Столбцы, содержащие даты (для преобразования формата)
        self.date_columns = {
            'expert': ['input_date'],
            # Добавьте другие таблицы с датами по необходимости
        }


        # Подключение к базе данных
        try:
            self.db = DatabaseManager()
            self.connect_menu_actions()
            self.connect_button_actions()
            self.statusbar.showMessage("Подключение к базе данных успешно")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться к базе данных: {str(e)}")
            self.close()

        # Текущая таблица
        self.current_table = None

    # def check_layout(self):
    #     """Проверка структуры layout"""
    #     print("Центральный виджет:", self.centralwidget)
    #     print("Layout центрального виджета:", self.centralwidget.layout())
    #     print("Размер таблицы:", self.table_widget.size())
    #     print("Размер окна:", self.size())

    def format_date(self, date_string):
        """Преобразование даты в формат для отображения"""
        if not date_string:
            return ""
        return DateValidator.format_date_for_display(date_string) or str(date_string)
    def connect_menu_actions(self):
        """Связываем пункты меню с соответствующими таблицами"""
        # Связываем действие "Эксперты" с таблицей expert
        self.actionExperts.triggered.connect(lambda: self.show_table("expert"))

        # Связываем действие "ГРНТИ" с таблицей grnti_classifier
        self.actionGRNTI.triggered.connect(lambda: self.show_table("grnti_classifier"))

        # Связываем действие "Регионы" с таблицей reg_obl_city
        self.actionRegions.triggered.connect(lambda: self.show_table("reg_obl_city"))

        # Связываем действие "Регионы" с таблицей reg_obl_city
        self.actionCode.triggered.connect(lambda: self.show_table("expert_grnti"))

    def connect_button_actions(self):
        """Связываем кнопки с функциями"""
        self.addButton.clicked.connect(self.add_record)
        self.editButton.clicked.connect(self.edit_record)
        self.deleteButton.clicked.connect(self.delete_record)

    def show_table(self, table_name):
        """Отображение содержимого таблицы"""
        try:
            self.current_table = table_name
            data = self.db.get_table_data(table_name)
            columns = self.db.get_columns_names(table_name)

            self.table_widget.clear()

            # Получаем русские названия столбцов
            display_columns = []

            for col in columns:
                if table_name == 'expert' and col == 'id':
                    continue

                if (table_name in self.column_display_names and
                        col in self.column_display_names[table_name]):
                    display_columns.append(self.column_display_names[table_name][col])
                else:
                    display_columns.append(col)

            # Настраиваем таблицу
            self.table_widget.setColumnCount(len(display_columns))
            self.table_widget.setHorizontalHeaderLabels(display_columns)
            self.table_widget.setRowCount(len(data))

            # Заполняем таблицу данными
            date_columns = self.date_columns.get(table_name, [])

            for row_num, row_data in enumerate(data):
                col_num_display = 0
                for col_num, value in enumerate(row_data):
                    col_name = columns[col_num]

                    if table_name == 'expert' and col_name == 'id':
                        continue

                    # Форматируем даты
                    if col_name in date_columns and value is not None:
                        if hasattr(value, 'strftime'):
                            value = value.strftime('%d.%m.%Y')
                        else:
                            value = self.format_date(str(value))
                    else:
                        value = str(value) if value is not None else ""

                    item = QTableWidgetItem(value)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table_widget.setItem(row_num, col_num_display, item)
                    col_num_display += 1

            # Автоматическая настройка ширины столбцов
            self.table_widget.resizeColumnsToContents()

            # Устанавливаем растягивание
            header = self.table_widget.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

            self.statusbar.showMessage(f"Загружена таблица: {table_name}. Записей: {len(data)}")

            # Принудительное обновление геометрии
            self.table_widget.updateGeometry()
            self.centralwidget.updateGeometry()

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить таблицу: {str(e)}")

    def setup_adaptive_columns(self):
        """Настройка адаптивного поведения столбцов"""
        if not hasattr(self, 'table_widget') or self.table_widget.columnCount() == 0:
            return

        header = self.table_widget.horizontalHeader()

        # Сначала подгоняем по содержимому
        self.table_widget.resizeColumnsToContents()

        # Проверяем общую ширину столбцов
        total_columns_width = sum([self.table_widget.columnWidth(i) for i in range(self.table_widget.columnCount())])
        available_width = self.table_widget.viewport().width()

        # Если столбцы уже занимают всю ширину или больше, оставляем как есть
        if total_columns_width >= available_width:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        else:
            # Если есть свободное место, растягиваем столбцы
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def add_record(self):
        """Добавить новую запись"""
        if not self.current_table:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите таблицу")
            return

        try:
            columns = self.db.get_columns_names(self.current_table)
            display_names = self.column_display_names.get(self.current_table, {})

            # Получаем список колонок с датами для текущей таблицы
            date_columns = self.date_columns.get(self.current_table, [])

            dialog = EditDialog(
                self.current_table,
                columns,
                data=None,
                parent=self,
                display_names=display_names,
                date_columns=date_columns
            )

            if dialog.exec():
                data = dialog.get_data()
                self.db.insert_record(self.current_table, data)
                self.show_table(self.current_table)
                self.statusbar.showMessage("Запись успешно добавлена")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось добавить запись: {str(e)}")
            print(f"Ошибка при добавлении: {e}")

    def edit_record(self):
        """Редактировать выбранную запись"""
        if not self.current_table:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите таблицу")
            return

        selected_row = self.table_widget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования")
            return

        try:
            # Получаем СЫРЫЕ данные из базы данных для выбранной строки
            table_data = self.db.get_table_data(self.current_table)
            if selected_row >= len(table_data):
                QMessageBox.warning(self, "Ошибка", "Неверный индекс строки")
                return

            raw_row_data = table_data[selected_row]
            record_id = raw_row_data[0]  # ID записи из сырых данных

            # Преобразуем данные в строки, обрабатывая даты отдельно
            row_data = []
            columns = self.db.get_columns_names(self.current_table)
            date_columns = self.date_columns.get(self.current_table, [])

            for i, value in enumerate(raw_row_data):
                column_name = columns[i]
                # Для таблицы expert пропускаем ID в отображаемых данных
                if self.current_table == 'expert' and column_name == 'id':
                    continue

                if value is None:
                    row_data.append("")
                elif column_name in date_columns and hasattr(value, 'strftime'):
                    formatted_date = DateValidator.format_date_for_display(value.strftime('%Y-%m-%d'))
                    row_data.append(formatted_date if formatted_date else str(value))
                else:
                    row_data.append(str(value))

            display_names = self.column_display_names.get(self.current_table, {})

            # Для диалога используем все столбцы, включая ID (нужен для обновления)
            dialog_columns = columns.copy()
            if self.current_table == 'expert':
                # Убираем ID из отображаемых столбцов в диалоге
                dialog_display_names = display_names.copy()
            else:
                dialog_display_names = display_names

            dialog = EditDialog(
                self.current_table,
                columns,  # Передаем все столбцы (включая ID)
                [str(x) if x is not None else "" for x in raw_row_data],  # Все данные включая ID
                parent=self,
                display_names=dialog_display_names,
                date_columns=date_columns
            )

            if dialog.exec():
                data = dialog.get_data()
                # Для обновления передаем данные без ID
                self.db.update_record(self.current_table, record_id, data[1:])
                self.show_table(self.current_table)
                self.statusbar.showMessage("Запись успешно обновлена")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось обновить запись: {str(e)}")
            print(f"Ошибка при редактировании: {e}")

    def delete_record(self):
        """Удалить выбранную запись"""
        if not self.current_table:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите таблицу")
            return

        selected_row = self.table_widget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления")
            return

        try:
            # Получаем ID из базы данных, так как в интерфейсе он скрыт
            table_data = self.db.get_table_data(self.current_table)
            if selected_row >= len(table_data):
                QMessageBox.warning(self, "Ошибка", "Неверный индекс строки")
                return

            record_id = table_data[selected_row][0]  # ID из сырых данных

            # Подтверждение удаления
            reply = QMessageBox.question(self, "Подтверждение",
                                         "Вы уверены, что хотите удалить эту запись?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                self.db.delete_record(self.current_table, record_id)
                self.show_table(self.current_table)
                self.statusbar.showMessage("Запись успешно удалена")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось удалить запись: {str(e)}")

    def setup_layout(self):
        """Настройка адаптивного layout"""
        # Убеждаемся, что центральный виджет имеет layout
        if not self.centralwidget.layout():
            main_layout = QVBoxLayout(self.centralwidget)
        else:
            main_layout = self.centralwidget.layout()

        # Устанавливаем растягивающие свойства для таблицы
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

    def resizeEvent(self, event):
        """Обработчик изменения размера окна"""
        super().resizeEvent(event)

        # Небольшая задержка для корректного обновления
        from PySide6.QtCore import QTimer
        QTimer.singleShot(50, self.adaptive_resize_columns)

    def adaptive_resize_columns(self):
        """Адаптивное изменение столбцов при resize"""
        if not hasattr(self, 'table_widget') or self.table_widget.columnCount() == 0:
            return

        header = self.table_widget.horizontalHeader()
        table_width = self.table_widget.viewport().width()

        # Сначала подгоняем по содержимому
        self.table_widget.resizeColumnsToContents()

        # Проверяем общую ширину всех столбцов
        total_width = sum([self.table_widget.columnWidth(i) for i in range(self.table_widget.columnCount())])

        if total_width < table_width:
            # Если столбцы уже помещаются - растягиваем их равномерно
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        else:
            # Если не помещаются - включаем прокрутку
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

    # def adjust_table_size(self):
    #     """Корректировка размера таблицы при изменении размера окна"""
    #     if hasattr(self, 'table_widget') and self.table_widget.isVisible():
    #         # Обновляем растягивание столбцов
    #         header = self.table_widget.horizontalHeader()
    #
    #         # Сначала подгоняем по содержимому
    #         self.table_widget.resizeColumnsToContents()
    #
    #         # Проверяем, нужно ли растягивать
    #         total_width = sum([self.table_widget.columnWidth(i) for i in range(self.table_widget.columnCount())])
    #         table_width = self.table_widget.viewport().width()
    #
    #         if total_width < table_width:
    #             header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    #         else:
    #             header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    #
    #         # Принудительное обновление таблицы
    #         self.table_widget.updateGeometry()

    def closeEvent(self, event):
        """Закрытие соединения с базой данных при выходе"""
        if hasattr(self, 'db'):
            self.db.connection.close()
            print("Соединение с базой данных закрыто")
        event.accept()


class DateValidator:
    """Класс для валидации и преобразования дат"""

    @staticmethod
    def get_supported_formats():
        """Возвращает поддерживаемые форматы дат"""
        return [
            '%Y-%m-%d',  # 2023-12-31
            '%d.%m.%Y',  # 31.12.2023
            '%d/%m/%Y',  # 31/12/2023
            '%Y/%m/%d',  # 2023/12/31
            '%d-%m-%Y',  # 31-12-2023
        ]

    @staticmethod
    def parse_date(date_string):
        """Пытается распарсить дату в различных форматах"""
        if not date_string or date_string.strip() == "":
            return None

        date_string = date_string.strip()

        for fmt in DateValidator.get_supported_formats():
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        return None

    @staticmethod
    def format_date_for_db(date_string):
        """Преобразует дату в формат базы данных (YYYY-MM-DD)"""
        date_obj = DateValidator.parse_date(date_string)
        if date_obj:
            return date_obj.strftime('%Y-%m-%d')
        return None

    @staticmethod
    def format_date_for_display(date_input):
        """Преобразует дату в формат для отображения (DD.MM.YYYY)"""
        if not date_input:
            return None

        # Если пришел объект datetime или date
        if hasattr(date_input, 'strftime'):
            return date_input.strftime('%d.%m.%Y')

        # Если пришла строка
        date_string = str(date_input).strip()
        if not date_string:
            return None

        date_obj = DateValidator.parse_date(date_string)
        if date_obj:
            return date_obj.strftime('%d.%m.%Y')
        return None

    @staticmethod
    def get_format_examples():
        """Возвращает примеры правильных форматов для сообщения об ошибке"""
        examples = []
        today = datetime.now()
        for fmt in DateValidator.get_supported_formats():
            examples.append(today.strftime(fmt))
        return ", ".join(examples)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())