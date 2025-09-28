import sys

from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidgetItem,
                               QHeaderView, QMessageBox, QDialog, QVBoxLayout,
                               QLabel, QLineEdit, QDialogButtonBox)
from PySide6.QtCore import Qt
from PySide6.QtCore import qDebug
# from presentee.main import DateValidator
from usecase.expert.usecase import ExpertUseCase
from usecase.grnti.usecase import GrntiUseCase
from usecase.reg_obl_city.dto import CreateRegOblCityDtoIn
from usecase.reg_obl_city.usecase import RegOblCityUseCase
from presentee.main_form_layout import UiMainWindow


class EditDialog(QDialog):
    """Диалоговое окно для добавления/редактирования записей"""

    def __init__(self, table_name, columns, data=None, parent=None, display_names=None):
        super().__init__(parent)
        self.table_name = table_name
        self.columns = columns
        self.data = data
        self.display_names = display_names or {}
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
                    # formatted_date = DateValidator.format_date_for_display(str(self.data[i]))
                    # field.setText(formatted_date if formatted_date else str(self.data[i]))
                    pass
                else:
                    field.setText(str(self.data[i]))
            else:
                field.setText("")  # Пустое значение для новой записи

            if self.data and i == 0:  # Первое поле (ID) только для чтения при редактировании
                field.setReadOnly(True)

            self.fields[column] = field
            self.layout.addWidget(field)

        # Добавляем подсказку о форматах дат, если есть даты в форме
        # if self.date_columns:
        #     hint_label = QLabel(f"Поддерживаемые форматы дат: {DateValidator.get_format_examples()}")
        #     hint_label.setStyleSheet("color: gray; font-size: 10px;")
        #     self.layout.addWidget(hint_label)

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
                    # if not DateValidator.parse_date(date_value):
                    #     QMessageBox.warning(
                    #         self,
                    #         "Неверный формат даты",
                    #         f"Поле '{self.display_names.get(column, column)}' содержит неверный формат даты.\n\n"
                    #         f"Поддерживаемые форматы:\n{DateValidator.get_format_examples()}"
                    #     )
                    #     return
                    pass

        self.accept()


sys.stdout.reconfigure(line_buffering=True)


class MainWindow(QMainWindow, UiMainWindow):
    def __init__(self, expert_usecase: ExpertUseCase, grnti_usecase: GrntiUseCase,
                 reg_obl_city_usecase: RegOblCityUseCase):
        super().__init__()
        sys.stdout.flush()
        self.setupUi()
        self.expert_usecase = expert_usecase
        self.grnti_usecase = grnti_usecase
        self.reg_obl_city_usecase = reg_obl_city_usecase
        qDebug("2")

        # TODO: подумать как не хардкодить имена колонок
        self.display_names = ("region", "oblname", "city")

        # Настройка интерфейса
        self.setWindowTitle("Управление экспертизой проектов")
        self.setMinimumSize(800, 600)
        qDebug("3")
        # Устанавливаем начальный размер окна (можно настроить под ваш экран)
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        self.resize(int(screen_geometry.width() * 0.8), int(screen_geometry.height() * 0.7))

        # Словари для русских названий столбцов
        self.column_display_names = {
            'reg_obl_city': {
                'id': 'ID',
                'region': 'Федеральный округ',
                'oblname': 'Субъект федерации',
                'city': 'Город'
            }
        }

        qDebug("4")
        # Текущая таблица
        self.current_table = None

        self.actionRegions.triggered.connect(lambda: self.reg_obl_city_usecase.get_all_reg_obl_city())
        qDebug("5")
        self.addButton.clicked.connect(self.add_record)
        qDebug("6")
        self.editButton.clicked.connect(self.edit_record)
        qDebug("7")
        self.deleteButton.clicked.connect(self.delete_record)
        qDebug("8")

    def show_table(self):
        """Отображение содержимого таблицы"""
        try:
            # self.current_table = table_name
            data = self.reg_obl_city_usecase.get_all_reg_obl_city()
            columns = self.display_names

            self.table_widget.clear()

            # Получаем русские названия столбцов
            display_columns = []

            for col in columns:
                display_columns.append(self.column_display_names["reg_obl_city"][col])

            # Настраиваем таблицу
            self.table_widget.setColumnCount(len(display_columns))
            self.table_widget.setHorizontalHeaderLabels(display_columns)
            self.table_widget.setRowCount(len(data))

            # Заполняем таблицу данными
            for row_num, row_data in enumerate(data):
                item1 = QTableWidgetItem(row_data.region)
                item1.setFlags(item1.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table_widget.setItem(row_num, 0, item1)
                item2 = QTableWidgetItem(row_data.oblname)
                item2.setFlags(item2.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table_widget.setItem(row_num, 1, item2)
                item3 = QTableWidgetItem(row_data.city)
                item3.setFlags(item3.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table_widget.setItem(row_num, 3, item3)

            # Автоматическая настройка ширины столбцов
            self.table_widget.resizeColumnsToContents()

            # Устанавливаем растягивание
            header = self.table_widget.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

            self.statusbar.showMessage(f"Загружена таблица: reg_obl_city. Записей: {len(data)}")

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
        print("called add_record")
        """Добавить новую запись"""
        if not self.current_table:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите таблицу")
            return

        try:
            columns = self.reg_obl_city_usecase.get_all_reg_obl_city()

            dialog = EditDialog(
                self.current_table,
                columns,
                data=None,
                parent=self,
                display_names="",
            )

            if dialog.exec():
                data = dialog.get_data()
                dto = CreateRegOblCityDtoIn(
                    region=data[0],
                    oblname=data[1],
                    city=data[2],
                )
                self.reg_obl_city_usecase.create_reg_obl_city(dto)
                self.reg_obl_city_usecase.get_all_reg_obl_city()
                self.statusbar.showMessage("Запись успешно добавлена")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось добавить запись: {str(e)}")
            print(f"Ошибка при добавлении: {e}")

    def edit_record(self):
        print("called edit_record")
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
            table_data = self.reg_obl_city_usecase.get_all_reg_obl_city()
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
                    # formatted_date = DateValidator.format_date_for_display(value.strftime('%Y-%m-%d'))
                    # row_data.append(formatted_date if formatted_date else str(value))
                    pass
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
        print("called delete_record")
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
            table_data = self.reg_obl_city_usecase.get_all_reg_obl_city()
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

    def closeEvent(self, event):
        """Закрытие соединения с базой данных при выходе"""
        if hasattr(self, 'db'):
            self.db.connection.close()
            print("Соединение с базой данных закрыто")
        event.accept()
