import sys
import psycopg2
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidgetItem,
                             QHeaderView, QMessageBox, QDialog, QVBoxLayout,
                             QLabel, QLineEdit, QDialogButtonBox, QHBoxLayout,
                             QPushButton, QTableWidget, QWidget, QScrollArea,
                             QComboBox, QCompleter)
from PyQt6.QtCore import Qt, QTimer
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

    def get_combined_data(self):
        """Получить объединенные данные из всех таблиц"""
        cursor = self.connection.cursor()
        
        # SQL запрос для объединения данных
        query = """
        SELECT 
            e.id as expert_id,
            e.name as expert_name,
            e.region,
            e.city,
            e.input_date,
            eg.rubric as grnti_code,
            gc.description as grnti_description,
            eg.subrubric,
            eg.siscipline
        FROM expert e
        LEFT JOIN expert_grnti eg ON e.id = eg.id
        LEFT JOIN grnti_classifier gc ON eg.rubric = gc.codrub
        ORDER BY e.name
        """
        
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        return data

    def get_combined_columns(self):
        """Получить названия столбцов для объединенной таблицы"""
        return [
            'expert_id', 'expert_name', 'region', 'city', 'input_date',
            'grnti_code', 'grnti_description', 'subrubric', 'siscipline'
        ]

    def insert_expert_with_grnti(self, expert_data, grnti_codes):
        """Добавить эксперта с кодами ГРНТИ"""
        cursor = self.connection.cursor()
        
        try:
            # Вставляем эксперта
            expert_query = """
                INSERT INTO expert (name, region, city, keywords, group_count, input_date) 
                VALUES (%s, %s, %s, %s, %s, %s) 
                RETURNING id
            """
            
            # Форматируем дату для базы данных
            date_str = expert_data[5]  # Дата добавления
            if date_str:
                db_date = DateValidator.format_date_for_db(date_str)
                if db_date:
                    expert_data[5] = db_date
                else:
                    expert_data[5] = datetime.now().strftime('%Y-%m-%d')
            else:
                expert_data[5] = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute(expert_query, expert_data)
            expert_id = cursor.fetchone()[0]
            
            # Вставляем коды ГРНТИ
            if grnti_codes:
                grnti_query = """
                    INSERT INTO expert_grnti (id, rubric, subrubric, siscipline) 
                    VALUES (%s, %s, %s, %s)
                """
                for code, subrubric, discipline in grnti_codes:
                    cursor.execute(grnti_query, (expert_id, code, subrubric, discipline))
            
            self.connection.commit()
            return expert_id
            
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()

    def get_regions(self):
        """Получить список уникальных регионов"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT DISTINCT region FROM reg_obl_city ORDER BY region")
        regions = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return regions

    def get_cities_by_region(self, region):
        """Получить список городов по региону"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT DISTINCT city FROM reg_obl_city WHERE region = %s ORDER BY city", (region,))
        cities = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return cities

    def search_cities(self, search_text):
        """Поиск городов по частичному совпадению"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT DISTINCT city, region, oblname
            FROM reg_obl_city
            WHERE city ILIKE %s
            ORDER BY city
        """, (f"%{search_text}%",))
        results = cursor.fetchall()
        cursor.close()
        return results

    def update_expert_with_grnti(self, expert_id, expert_data, grnti_codes):
        """Обновить эксперта с кодами ГРНТИ"""
        cursor = self.connection.cursor()
        
        try:
            # Обновляем данные эксперта
            expert_query = """
                UPDATE expert
                SET name = %s, region = %s, city = %s, keywords = %s, group_count = %s, input_date = %s
                WHERE id = %s
            """
            
            # Форматируем дату для базы данных
            date_str = expert_data[5]  # Дата добавления
            if date_str:
                db_date = DateValidator.format_date_for_db(date_str)
                if db_date:
                    expert_data[5] = db_date
                else:
                    expert_data[5] = datetime.now().strftime('%Y-%m-%d')
            else:
                expert_data[5] = datetime.now().strftime('%Y-%m-%d')
            
            # Добавляем expert_id в конец для WHERE условия
            update_data = expert_data + [expert_id]
            cursor.execute(expert_query, update_data)
            
            # Удаляем старые коды ГРНТИ
            cursor.execute("DELETE FROM expert_grnti WHERE id = %s", (expert_id,))
            
            # Вставляем новые коды ГРНТИ
            if grnti_codes:
                grnti_query = """
                    INSERT INTO expert_grnti (id, rubric, subrubric, siscipline)
                    VALUES (%s, %s, %s, %s)
                """
                for code, subrubric, discipline in grnti_codes:
                    cursor.execute(grnti_query, (expert_id, code, subrubric, discipline))
            
            self.connection.commit()
            return expert_id
            
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()


class CityComboBox(QComboBox):
    """ComboBox с автодополнением для городов"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        
        # Кэш для результатов поиска
        self.search_cache = {}
        
        # Таймер для задержки поиска
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        
        # Настройка автодополнения
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.setCompleter(self.completer)
        
        # Подключаем сигналы
        self.lineEdit().textChanged.connect(self.on_text_changed)
        self.currentTextChanged.connect(self.on_text_changed)
        
        # Загружаем все города при инициализации для быстрого поиска
        self.load_all_cities()
    
    def load_all_cities(self):
        """Загружает все города в кэш для быстрого поиска"""
        try:
            if not self.db_manager or not self.db_manager.connection:
                self.all_cities = []
                return
                
            cursor = self.db_manager.connection.cursor()
            cursor.execute("""
                SELECT DISTINCT city, region, oblname 
                FROM reg_obl_city 
                ORDER BY city
            """)
            self.all_cities = cursor.fetchall()
            cursor.close()
            print(f"Загружено {len(self.all_cities)} городов в кэш")
        except Exception as e:
            print(f"Ошибка загрузки городов: {e}")
            self.all_cities = []
    
    def on_text_changed(self, text):
        """Обновляет список городов при изменении текста"""
        # Останавливаем предыдущий таймер
        self.search_timer.stop()
        
        if len(text) >= 2:  # Начинаем поиск с 2 символов
            # Запускаем поиск с задержкой 300мс
            self.search_timer.start(300)
        else:
            self.clear()
    
    def perform_search(self):
        """Выполняет поиск городов"""
        text = self.lineEdit().text()
        if len(text) < 2:
            return
            
        # Проверяем кэш
        if text in self.search_cache:
            self.update_cities_list(self.search_cache[text])
            return
        
        # Выполняем поиск в кэше
        search_text = text.lower()
        filtered_cities = []
        
        for city, region, oblname in self.all_cities:
            if search_text in city.lower():
                filtered_cities.append((city, region, oblname))
                if len(filtered_cities) >= 20:  # Ограничиваем количество результатов
                    break
        
        # Сохраняем в кэш
        self.search_cache[text] = filtered_cities
        
        # Обновляем список
        self.update_cities_list(filtered_cities)
    
    def update_cities_list(self, cities):
        """Обновляет список городов в ComboBox"""
        current_text = self.lineEdit().text()
        self.clear()
        
        for city, region, oblname in cities:
            # Добавляем город с дополнительной информацией
            display_text = f"{city} ({region}, {oblname})"
            self.addItem(display_text, city)
        
        # Восстанавливаем введенный текст
        self.lineEdit().setText(current_text)
    
    def get_selected_city(self):
        """Возвращает выбранный город"""
        current_data = self.currentData()
        if current_data:
            return current_data
        return self.currentText().split(' (')[0]  # Берем только название города


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


class ExpertAddDialog(QDialog):
    """Диалоговое окно для добавления эксперта с кодами ГРНТИ"""

    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.grnti_codes = []  # Список кодов ГРНТИ
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Добавление эксперта")
        self.setMinimumSize(500, 400)
        
        main_layout = QVBoxLayout()
        
        # Основные поля эксперта
        expert_group = QWidget()
        expert_layout = QVBoxLayout(expert_group)
        
        # ФИО эксперта
        name_label = QLabel("ФИО эксперта *")
        self.name_field = QLineEdit()
        expert_layout.addWidget(name_label)
        expert_layout.addWidget(self.name_field)
        
        # Регион
        region_label = QLabel("Регион")
        self.region_combo = QComboBox()
        self.region_combo.setEditable(True)
        self.region_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        if self.db_manager:
            regions = self.db_manager.get_regions()
            self.region_combo.addItems(regions)
        expert_layout.addWidget(region_label)
        expert_layout.addWidget(self.region_combo)
        
        # Город
        city_label = QLabel("Город")
        if self.db_manager:
            self.city_combo = CityComboBox(self.db_manager)
            # Добавляем подсказку
            city_hint = QLabel("Начните вводить название города (минимум 2 символа)")
            city_hint.setStyleSheet("color: gray; font-size: 10px;")
            expert_layout.addWidget(city_label)
            expert_layout.addWidget(self.city_combo)
            expert_layout.addWidget(city_hint)
        else:
            self.city_combo = QLineEdit()
            expert_layout.addWidget(city_label)
            expert_layout.addWidget(self.city_combo)
        
        # Ключевые слова
        keywords_label = QLabel("Ключевые слова")
        self.keywords_field = QLineEdit()
        expert_layout.addWidget(keywords_label)
        expert_layout.addWidget(self.keywords_field)
        
        # Количество групп
        group_count_label = QLabel("Количество групп")
        self.group_count_field = QLineEdit()
        self.group_count_field.setText("0")
        expert_layout.addWidget(group_count_label)
        expert_layout.addWidget(self.group_count_field)
        
        # Дата добавления
        date_label = QLabel("Дата добавления")
        self.date_field = QLineEdit()
        self.date_field.setText(datetime.now().strftime('%d.%m.%Y'))
        expert_layout.addWidget(date_label)
        expert_layout.addWidget(self.date_field)
        
        main_layout.addWidget(expert_group)
        
        # Разделитель
        separator = QLabel("─" * 50)
        main_layout.addWidget(separator)
        
        # Коды ГРНТИ
        grnti_group = QWidget()
        grnti_layout = QVBoxLayout(grnti_group)
        
        grnti_header_layout = QHBoxLayout()
        grnti_label = QLabel("Коды ГРНТИ")
        self.add_grnti_button = QPushButton("+")
        self.add_grnti_button.setMaximumWidth(30)
        self.add_grnti_button.clicked.connect(self.add_grnti_code)
        grnti_header_layout.addWidget(grnti_label)
        grnti_header_layout.addStretch()
        grnti_header_layout.addWidget(self.add_grnti_button)
        grnti_layout.addLayout(grnti_header_layout)
        
        # Таблица для кодов ГРНТИ
        self.grnti_table = QTableWidget()
        self.grnti_table.setColumnCount(4)
        self.grnti_table.setHorizontalHeaderLabels(["Код ГРНТИ", "Подрубрика", "Дисциплина", "Удалить"])
        self.grnti_table.horizontalHeader().setStretchLastSection(True)
        grnti_layout.addWidget(self.grnti_table)
        
        main_layout.addWidget(grnti_group)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)
        
        self.setLayout(main_layout)
        
        # Добавляем первую строку для кода ГРНТИ
        self.add_grnti_code()

    def add_grnti_code(self):
        """Добавляет новую строку для кода ГРНТИ"""
        row_count = self.grnti_table.rowCount()
        self.grnti_table.insertRow(row_count)
        
        # Код ГРНТИ
        code_item = QTableWidgetItem("")
        self.grnti_table.setItem(row_count, 0, code_item)
        
        # Подрубрика
        subrubric_item = QTableWidgetItem("")
        self.grnti_table.setItem(row_count, 1, subrubric_item)
        
        # Дисциплина
        discipline_item = QTableWidgetItem("")
        self.grnti_table.setItem(row_count, 2, discipline_item)
        
        # Кнопка удаления
        delete_button = QPushButton("×")
        delete_button.setMaximumWidth(30)
        delete_button.clicked.connect(lambda: self.remove_grnti_code(row_count))
        self.grnti_table.setCellWidget(row_count, 3, delete_button)

    def remove_grnti_code(self, row):
        """Удаляет строку с кодом ГРНТИ"""
        self.grnti_table.removeRow(row)
        # Обновляем индексы для оставшихся кнопок удаления
        for i in range(self.grnti_table.rowCount()):
            button = self.grnti_table.cellWidget(i, 3)
            if button:
                button.clicked.disconnect()
                button.clicked.connect(lambda checked, r=i: self.remove_grnti_code(r))

    def validate_and_accept(self):
        """Проверяет валидность данных перед принятием"""
        # Проверяем обязательные поля
        if not self.name_field.text().strip():
            QMessageBox.warning(self, "Ошибка", "ФИО эксперта обязательно для заполнения")
            return
        
        # Проверяем дату
        if self.date_field.text().strip():
            if not DateValidator.parse_date(self.date_field.text().strip()):
                QMessageBox.warning(
                    self,
                    "Неверный формат даты",
                    f"Неверный формат даты.\n\n"
                    f"Поддерживаемые форматы:\n{DateValidator.get_format_examples()}"
                )
                return
        
        # Проверяем количество групп
        if self.group_count_field.text().strip():
            try:
                int(self.group_count_field.text().strip())
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Количество групп должно быть числом")
                return
        
        # Собираем коды ГРНТИ
        self.grnti_codes = []
        for row in range(self.grnti_table.rowCount()):
            code_item = self.grnti_table.item(row, 0)
            subrubric_item = self.grnti_table.item(row, 1)
            discipline_item = self.grnti_table.item(row, 2)
            
            code = code_item.text().strip() if code_item else ""
            subrubric = subrubric_item.text().strip() if subrubric_item else ""
            discipline = discipline_item.text().strip() if discipline_item else ""
            
            if code:  # Добавляем только если есть код
                try:
                    code_int = int(code)
                    subrubric_int = int(subrubric) if subrubric else None
                    discipline_int = int(discipline) if discipline else None
                    self.grnti_codes.append((code_int, subrubric_int, discipline_int))
                except ValueError:
                    QMessageBox.warning(self, "Ошибка", f"Код ГРНТИ в строке {row + 1} должен быть числом")
                    return
        
        self.accept()

    def get_expert_data(self):
        """Возвращает данные эксперта"""
        # Получаем регион
        region = self.region_combo.currentText().strip()
        
        # Получаем город
        if hasattr(self.city_combo, 'get_selected_city'):
            city = self.city_combo.get_selected_city()
        else:
            city = self.city_combo.text().strip()
        
        return [
            self.name_field.text().strip(),
            region,
            city,
            self.keywords_field.text().strip(),
            self.group_count_field.text().strip() or "0",
            self.date_field.text().strip() or datetime.now().strftime('%d.%m.%Y')
        ]

    def get_grnti_codes(self):
        """Возвращает коды ГРНТИ"""
        return self.grnti_codes


class ExpertEditDialog(QDialog):
    """Диалоговое окно для редактирования эксперта с кодами ГРНТИ"""

    def __init__(self, expert_data, expert_id, parent=None, db_manager=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.expert_id = expert_id
        self.expert_data = expert_data
        self.grnti_codes = []  # Список кодов ГРНТИ
        self.setup_ui()
        self.load_expert_data()
        self.load_grnti_codes()

    def setup_ui(self):
        self.setWindowTitle("Редактирование эксперта")
        self.setMinimumSize(500, 400)
        
        main_layout = QVBoxLayout()
        
        # Основные поля эксперта
        expert_group = QWidget()
        expert_layout = QVBoxLayout(expert_group)
        
        # ФИО эксперта
        name_label = QLabel("ФИО эксперта *")
        self.name_field = QLineEdit()
        expert_layout.addWidget(name_label)
        expert_layout.addWidget(self.name_field)
        
        # Регион
        region_label = QLabel("Регион")
        self.region_combo = QComboBox()
        self.region_combo.setEditable(True)
        self.region_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        if self.db_manager:
            regions = self.db_manager.get_regions()
            self.region_combo.addItems(regions)
        expert_layout.addWidget(region_label)
        expert_layout.addWidget(self.region_combo)
        
        # Город
        city_label = QLabel("Город")
        if self.db_manager:
            self.city_combo = CityComboBox(self.db_manager)
            # Добавляем подсказку
            city_hint = QLabel("Начните вводить название города (минимум 2 символа)")
            city_hint.setStyleSheet("color: gray; font-size: 10px;")
            expert_layout.addWidget(city_label)
            expert_layout.addWidget(self.city_combo)
            expert_layout.addWidget(city_hint)
        else:
            self.city_combo = QLineEdit()
            expert_layout.addWidget(city_label)
            expert_layout.addWidget(self.city_combo)
        
        # Ключевые слова
        keywords_label = QLabel("Ключевые слова")
        self.keywords_field = QLineEdit()
        expert_layout.addWidget(keywords_label)
        expert_layout.addWidget(self.keywords_field)
        
        # Количество групп
        group_count_label = QLabel("Количество групп")
        self.group_count_field = QLineEdit()
        expert_layout.addWidget(group_count_label)
        expert_layout.addWidget(self.group_count_field)
        
        # Дата добавления
        date_label = QLabel("Дата добавления")
        self.date_field = QLineEdit()
        expert_layout.addWidget(date_label)
        expert_layout.addWidget(self.date_field)
        
        main_layout.addWidget(expert_group)
        
        # Разделитель
        separator = QLabel("─" * 50)
        main_layout.addWidget(separator)
        
        # Коды ГРНТИ
        grnti_group = QWidget()
        grnti_layout = QVBoxLayout(grnti_group)
        
        grnti_header_layout = QHBoxLayout()
        grnti_label = QLabel("Коды ГРНТИ")
        self.add_grnti_button = QPushButton("+")
        self.add_grnti_button.setMaximumWidth(30)
        self.add_grnti_button.clicked.connect(self.add_grnti_code)
        grnti_header_layout.addWidget(grnti_label)
        grnti_header_layout.addStretch()
        grnti_header_layout.addWidget(self.add_grnti_button)
        grnti_layout.addLayout(grnti_header_layout)
        
        # Таблица для кодов ГРНТИ
        self.grnti_table = QTableWidget()
        self.grnti_table.setColumnCount(4)
        self.grnti_table.setHorizontalHeaderLabels(["Код ГРНТИ", "Подрубрика", "Дисциплина", "Удалить"])
        self.grnti_table.horizontalHeader().setStretchLastSection(True)
        grnti_layout.addWidget(self.grnti_table)
        
        main_layout.addWidget(grnti_group)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)
        
        self.setLayout(main_layout)

    def load_expert_data(self):
        """Загружает данные эксперта в поля формы"""
        if not self.expert_data:
            return
            
        # Заполняем поля данными эксперта
        # expert_data содержит: [id, name, region, city, keywords, group_count, input_date]
        if len(self.expert_data) > 1:
            self.name_field.setText(str(self.expert_data[1]) if self.expert_data[1] else "")
        if len(self.expert_data) > 2:
            region = str(self.expert_data[2]) if self.expert_data[2] else ""
            self.region_combo.setCurrentText(region)
        if len(self.expert_data) > 3:
            city = str(self.expert_data[3]) if self.expert_data[3] else ""
            if hasattr(self.city_combo, 'lineEdit'):
                self.city_combo.lineEdit().setText(city)
            else:
                self.city_combo.setText(city)
        if len(self.expert_data) > 4:
            self.keywords_field.setText(str(self.expert_data[4]) if self.expert_data[4] else "")
        if len(self.expert_data) > 5:
            self.group_count_field.setText(str(self.expert_data[5]) if self.expert_data[5] else "0")
        if len(self.expert_data) > 6:
            # Форматируем дату для отображения
            date_value = self.expert_data[6]
            if date_value:
                formatted_date = DateValidator.format_date_for_display(str(date_value))
                self.date_field.setText(formatted_date if formatted_date else str(date_value))

    def load_grnti_codes(self):
        """Загружает существующие коды ГРНТИ для эксперта"""
        if not self.db_manager or not self.expert_id:
            return
            
        try:
            cursor = self.db_manager.connection.cursor()
            cursor.execute("""
                SELECT rubric, subrubric, siscipline
                FROM expert_grnti
                WHERE id = %s
            """, (self.expert_id,))
            
            existing_codes = cursor.fetchall()
            cursor.close()
            
            # Добавляем существующие коды в таблицу
            for code, subrubric, discipline in existing_codes:
                self.add_grnti_code_with_data(code, subrubric, discipline)
                
            # Если нет кодов, добавляем пустую строку
            if not existing_codes:
                self.add_grnti_code()
                
        except Exception as e:
            print(f"Ошибка загрузки кодов ГРНТИ: {e}")
            # Добавляем пустую строку в случае ошибки
            self.add_grnti_code()

    def add_grnti_code(self):
        """Добавляет новую пустую строку для кода ГРНТИ"""
        self.add_grnti_code_with_data("", "", "")

    def add_grnti_code_with_data(self, code="", subrubric="", discipline=""):
        """Добавляет новую строку для кода ГРНТИ с данными"""
        row_count = self.grnti_table.rowCount()
        self.grnti_table.insertRow(row_count)
        
        # Код ГРНТИ
        code_item = QTableWidgetItem(str(code) if code else "")
        self.grnti_table.setItem(row_count, 0, code_item)
        
        # Подрубрика
        subrubric_item = QTableWidgetItem(str(subrubric) if subrubric else "")
        self.grnti_table.setItem(row_count, 1, subrubric_item)
        
        # Дисциплина
        discipline_item = QTableWidgetItem(str(discipline) if discipline else "")
        self.grnti_table.setItem(row_count, 2, discipline_item)
        
        # Кнопка удаления
        delete_button = QPushButton("×")
        delete_button.setMaximumWidth(30)
        delete_button.clicked.connect(lambda: self.remove_grnti_code(row_count))
        self.grnti_table.setCellWidget(row_count, 3, delete_button)

    def remove_grnti_code(self, row):
        """Удаляет строку с кодом ГРНТИ"""
        self.grnti_table.removeRow(row)
        # Обновляем индексы для оставшихся кнопок удаления
        for i in range(self.grnti_table.rowCount()):
            button = self.grnti_table.cellWidget(i, 3)
            if button:
                button.clicked.disconnect()
                button.clicked.connect(lambda checked, r=i: self.remove_grnti_code(r))

    def validate_and_accept(self):
        """Проверяет валидность данных перед принятием"""
        # Проверяем обязательные поля
        if not self.name_field.text().strip():
            QMessageBox.warning(self, "Ошибка", "ФИО эксперта обязательно для заполнения")
            return
        
        # Проверяем дату
        if self.date_field.text().strip():
            if not DateValidator.parse_date(self.date_field.text().strip()):
                QMessageBox.warning(
                    self,
                    "Неверный формат даты",
                    f"Неверный формат даты.\n\n"
                    f"Поддерживаемые форматы:\n{DateValidator.get_format_examples()}"
                )
                return
        
        # Проверяем количество групп
        if self.group_count_field.text().strip():
            try:
                int(self.group_count_field.text().strip())
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Количество групп должно быть числом")
                return
        
        # Собираем коды ГРНТИ
        self.grnti_codes = []
        for row in range(self.grnti_table.rowCount()):
            code_item = self.grnti_table.item(row, 0)
            subrubric_item = self.grnti_table.item(row, 1)
            discipline_item = self.grnti_table.item(row, 2)
            
            code = code_item.text().strip() if code_item else ""
            subrubric = subrubric_item.text().strip() if subrubric_item else ""
            discipline = discipline_item.text().strip() if discipline_item else ""
            
            if code:  # Добавляем только если есть код
                try:
                    code_int = int(code)
                    subrubric_int = int(subrubric) if subrubric else None
                    discipline_int = int(discipline) if discipline else None
                    self.grnti_codes.append((code_int, subrubric_int, discipline_int))
                except ValueError:
                    QMessageBox.warning(self, "Ошибка", f"Код ГРНТИ в строке {row + 1} должен быть числом")
                    return
        
        self.accept()

    def get_expert_data(self):
        """Возвращает данные эксперта"""
        # Получаем регион
        region = self.region_combo.currentText().strip()
        
        # Получаем город
        if hasattr(self.city_combo, 'get_selected_city'):
            city = self.city_combo.get_selected_city()
        else:
            city = self.city_combo.text().strip()
        
        return [
            self.name_field.text().strip(),
            region,
            city,
            self.keywords_field.text().strip(),
            self.group_count_field.text().strip() or "0",
            self.date_field.text().strip() or datetime.now().strftime('%d.%m.%Y')
        ]

    def get_grnti_codes(self):
        """Возвращает коды ГРНТИ"""
        return self.grnti_codes


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
        
        # Настройка сортировки таблицы
        self.setup_table_sorting()

        # Словари для русских названий столбцов
        self.column_display_names = {
            'expert': {
                'id': 'ID',
                'name': 'ФИО эксперта',
                'region': 'Регион',
                'city': 'Город',
                'keywords': 'Ключевые слова',
                'group_count': 'Количество групп',
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
                'subrubric': 'Подрубрика',
                'siscipline': 'Дисциплина'
            },
            'combined': {
                'expert_id': 'ID эксперта',
                'expert_name': 'ФИО эксперта',
                'region': 'Регион',
                'city': 'Город',
                'input_date': 'Дата добавления',
                'grnti_code': 'Код ГРНТИ',
                'grnti_description': 'Описание ГРНТИ',
                'subrubric': 'Подрубрика',
                'siscipline': 'Дисциплина'
            }
        }

        # Столбцы, содержащие даты (для преобразования формата)
        self.date_columns = {
            'expert': ['input_date'],
            'combined': ['input_date'],
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
        
        # Переменные для сортировки
        self.current_sort_column = -1
        self.sort_ascending = True

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
    
    def setup_table_sorting(self):
        """Настройка сортировки таблицы"""
        # Включаем сортировку
        self.table_widget.setSortingEnabled(True)
        
        # Подключаем обработчик клика по заголовкам
        header = self.table_widget.horizontalHeader()
        header.sectionClicked.connect(self.on_header_clicked)
        
        # Настраиваем заголовки для показа индикатора сортировки
        header.setSortIndicatorShown(True)
    
    def on_header_clicked(self, logical_index):
        """Обработчик клика по заголовку столбца"""
        if not self.current_table:
            return
            
        # Если кликнули по тому же столбцу, меняем направление сортировки
        if self.current_sort_column == logical_index:
            self.sort_ascending = not self.sort_ascending
        else:
            # Если кликнули по новому столбцу, сортируем по возрастанию
            self.sort_ascending = True
            self.current_sort_column = logical_index
        
        # Выполняем сортировку
        self.sort_table_data(logical_index, self.sort_ascending)
    
    def sort_table_data(self, column_index, ascending=True):
        """Сортировка данных таблицы по указанному столбцу"""
        if not self.current_table:
            return
            
        try:
            # Получаем данные в зависимости от типа таблицы
            if self.current_table == "combined":
                data = self.db.get_combined_data()
                columns = self.db.get_combined_columns()
                db_column_index = column_index
            else:
                data = self.db.get_table_data(self.current_table)
                columns = self.db.get_columns_names(self.current_table)
                
                # Определяем реальный индекс столбца в базе данных
                # Учитываем, что для таблицы expert первый столбец (id) скрыт
                if self.current_table == 'expert' and column_index >= 0:
                    db_column_index = column_index + 1  # +1 потому что id скрыт
                else:
                    db_column_index = column_index
            
            if db_column_index >= len(columns):
                return
                
            # Сортируем данные
            sorted_data = sorted(data, key=lambda row: self.get_sort_key(row[db_column_index]), reverse=not ascending)
            
            # Обновляем таблицу с отсортированными данными
            if self.current_table == "combined":
                self.populate_combined_table_with_data(sorted_data, columns)
            else:
                self.populate_table_with_data(sorted_data, columns)
            
            # Обновляем индикатор сортировки
            header = self.table_widget.horizontalHeader()
            header.setSortIndicator(column_index, Qt.SortOrder.AscendingOrder if ascending else Qt.SortOrder.DescendingOrder)
            
            self.statusbar.showMessage(f"Таблица отсортирована по столбцу {column_index + 1} ({'по возрастанию' if ascending else 'по убыванию'})")
            
        except Exception as e:
            QMessageBox.warning(self, "Ошибка сортировки", f"Не удалось отсортировать данные: {str(e)}")
    
    def get_sort_key(self, value):
        """Получает ключ для сортировки, обрабатывая разные типы данных"""
        if value is None:
            return (0, "")  # Возвращаем кортеж для правильной сортировки None значений
        
        # Пытаемся преобразовать в число
        try:
            if isinstance(value, (int, float)):
                return (1, value)  # Числа имеют приоритет 1
            # Пытаемся преобразовать строку в число
            if isinstance(value, str):
                # Убираем пробелы и проверяем, является ли строка числом
                clean_value = value.strip()
                if clean_value.replace('.', '').replace('-', '').replace('+', '').isdigit():
                    return (1, float(clean_value))  # Числа имеют приоритет 1
        except (ValueError, TypeError):
            pass
        
        # Для дат пытаемся преобразовать в datetime для корректной сортировки
        if hasattr(value, 'strftime'):
            return (2, value)  # Даты имеют приоритет 2
        
        # Для строк проверяем, является ли это датой
        date_obj = DateValidator.parse_date(str(value))
        if date_obj:
            return (2, date_obj)  # Даты имеют приоритет 2
        
        # Возвращаем строку в нижнем регистре для сортировки
        return (3, str(value).lower())  # Строки имеют приоритет 3
    
    def populate_table_with_data(self, data, columns):
        """Заполняет таблицу данными (используется для обновления после сортировки)"""
        # Получаем русские названия столбцов
        display_columns = []
        for col in columns:
            if self.current_table == 'expert' and col == 'id':
                continue
            if (self.current_table in self.column_display_names and
                    col in self.column_display_names[self.current_table]):
                display_columns.append(self.column_display_names[self.current_table][col])
            else:
                display_columns.append(col)
        
        # Настраиваем таблицу
        self.table_widget.setColumnCount(len(display_columns))
        self.table_widget.setHorizontalHeaderLabels(display_columns)
        self.table_widget.setRowCount(len(data))
        
        # Заполняем таблицу данными
        date_columns = self.date_columns.get(self.current_table, [])
        
        for row_num, row_data in enumerate(data):
            col_num_display = 0
            for col_num, value in enumerate(row_data):
                col_name = columns[col_num]
                
                if self.current_table == 'expert' and col_name == 'id':
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
        
        # Связываем действие "Общая таблица" с объединенными данными
        self.actionCombined.triggered.connect(self.show_combined_table)
        
        # Связываем действия для вкладки "Группы"
        self.actionGroups.triggered.connect(self.show_groups_info)
        
        # Связываем действия для вкладки "Помощь"
        self.actionHelp.triggered.connect(self.show_help)
        self.actionAbout.triggered.connect(self.show_about)

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

            # Сбрасываем состояние сортировки при загрузке новой таблицы
            self.current_sort_column = -1
            self.sort_ascending = True

            self.table_widget.clear()

            # Используем новый метод для заполнения таблицы
            self.populate_table_with_data(data, columns)

            self.statusbar.showMessage(f"Загружена таблица: {table_name}. Записей: {len(data)}")

            # Принудительное обновление геометрии
            self.table_widget.updateGeometry()
            self.centralwidget.updateGeometry()

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить таблицу: {str(e)}")

    def show_combined_table(self):
        """Отображение объединенной таблицы с данными из всех таблиц"""
        try:
            self.current_table = "combined"
            data = self.db.get_combined_data()
            columns = self.db.get_combined_columns()

            # Сбрасываем состояние сортировки при загрузке новой таблицы
            self.current_sort_column = -1
            self.sort_ascending = True

            self.table_widget.clear()

            # Используем метод для заполнения таблицы
            self.populate_combined_table_with_data(data, columns)

            self.statusbar.showMessage(f"Загружена объединенная таблица. Записей: {len(data)}")

            # Принудительное обновление геометрии
            self.table_widget.updateGeometry()
            self.centralwidget.updateGeometry()

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить объединенную таблицу: {str(e)}")

    def populate_combined_table_with_data(self, data, columns):
        """Заполняет таблицу объединенными данными"""
        # Получаем русские названия столбцов
        display_columns = []
        for col in columns:
            if (self.current_table in self.column_display_names and
                    col in self.column_display_names[self.current_table]):
                display_columns.append(self.column_display_names[self.current_table][col])
            else:
                display_columns.append(col)

        # Настраиваем таблицу
        self.table_widget.setColumnCount(len(display_columns))
        self.table_widget.setHorizontalHeaderLabels(display_columns)
        self.table_widget.setRowCount(len(data))

        # Заполняем таблицу данными
        date_columns = self.date_columns.get(self.current_table, [])

        for row_num, row_data in enumerate(data):
            for col_num, value in enumerate(row_data):
                col_name = columns[col_num]

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
                self.table_widget.setItem(row_num, col_num, item)

        # Автоматическая настройка ширины столбцов
        self.table_widget.resizeColumnsToContents()

        # Устанавливаем растягивание
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def show_groups_info(self):
        """Показать информацию о группах"""
        QMessageBox.information(
            self, 
            "Управление группами", 
            "Функционал управления группами будет добавлен в следующих версиях.\n\n"
            "Здесь будет возможность:\n"
            "• Создавать группы экспертов\n"
            "• Управлять составом групп\n"
            "• Назначать руководителей групп\n"
            "• Просматривать статистику по группам"
        )

    def show_help(self):
        """Показать справку"""
        QMessageBox.information(
            self, 
            "Справка", 
            "Управление экспертизой проектов\n\n"
            "Основные функции:\n"
            "• Просмотр и редактирование данных экспертов\n"
            "• Управление классификацией ГРНТИ\n"
            "• Работа с региональными данными\n"
            "• Сортировка данных по столбцам\n"
            "• Добавление, изменение и удаление записей\n\n"
            "Сортировка: кликните на заголовок столбца для сортировки\n"
            "Редактирование: выберите запись и нажмите 'Изменить'\n"
            "Добавление: нажмите 'Добавить' для создания новой записи"
        )

    def show_about(self):
        """Показать информацию о программе"""
        QMessageBox.about(
            self, 
            "О программе", 
            "Управление экспертизой проектов\n\n"
            "Версия: 1.0\n"
            "Разработчик: Система управления экспертизой\n\n"
            "Программа предназначена для управления данными экспертов,\n"
            "классификацией ГРНТИ и региональной информацией.\n\n"
            "© 2025 Все права защищены"
        )

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
            # Специальная обработка для таблицы expert
            if self.current_table == "expert":
                dialog = ExpertAddDialog(self, self.db)
                if dialog.exec():
                    expert_data = dialog.get_expert_data()
                    grnti_codes = dialog.get_grnti_codes()
                    
                    expert_id = self.db.insert_expert_with_grnti(expert_data, grnti_codes)
                    self.show_table(self.current_table)
                    self.statusbar.showMessage(f"Эксперт успешно добавлен с ID: {expert_id}")
            else:
                # Обычная обработка для других таблиц
                columns = self.db.get_columns_names(self.current_table)
                display_names = self.column_display_names.get(self.current_table, {})
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

            # Специальная обработка для таблицы expert
            if self.current_table == "expert":
                dialog = ExpertEditDialog(raw_row_data, record_id, self, self.db)
                if dialog.exec():
                    expert_data = dialog.get_expert_data()
                    grnti_codes = dialog.get_grnti_codes()
                    
                    self.db.update_expert_with_grnti(record_id, expert_data, grnti_codes)
                    self.show_table(self.current_table)
                    self.statusbar.showMessage(f"Эксперт успешно обновлен (ID: {record_id})")
            else:
                # Обычная обработка для других таблиц
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
        from PyQt6.QtCore import QTimer
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