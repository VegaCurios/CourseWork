import re
import json
import hashlib
from database import *
from datetime import datetime
from docx import Document
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from tkinter import *
from Class import *
import logging

fileResult = ()

logging.basicConfig(
    filename='user_actions.log',  # Файл для записи логов
    level=logging.INFO,           # Уровень логирования (можно установить DEBUG для более подробных логов)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат записи логов
    datefmt='%Y-%m-%d %H:%M:%S'   # Формат времени
)

def log_user_action(action, status="INFO"):
    """Функция для записи пользовательских действий в лог."""
    if status == "INFO":
        logging.info(action)
    elif status == "ERROR":
        logging.error(action)


def toggle_theme(mainWindow, ID, *additional_windows):
    try:
        current_theme = mainWindow.tk.call("ttk::style", "theme", "use")
        style = ttk.Style()
        
        if current_theme == "forest-dark":
            # Переключаем на светлую тему
            if not is_theme_loaded(mainWindow, 'forest-light'):
                mainWindow.tk.call('source', 'Forest/forest-light.tcl')
            style.theme_use('forest-light')
            
            # Изменение фона для окна
            mainWindow.tk_setPalette(background='white')  
            for window in additional_windows:
                if window and window.winfo_exists():
                    window.tk_setPalette(background='white')
            log_user_action(f"User {ID} toggled on light theme")
            
            # Настройка стиля для виджетов
            style.configure('Treeview', background='white', foreground='black', fieldbackground='white')
            style.map('Treeview', background=[('selected', '#217346')], foreground=[('selected', 'white')])
        else:
            # Переключаем на темную тему
            if not is_theme_loaded(mainWindow, 'forest-dark'):
                mainWindow.tk.call('source', 'Forest/forest-dark.tcl')
            style.theme_use('forest-dark')
            
            # Изменение фона для окна
            mainWindow.tk_setPalette(background='#333333')  
            for window in additional_windows:
                if window and window.winfo_exists():
                    window.tk_setPalette(background='#333333')
            log_user_action(f"User {ID} toggled on dark theme")
            # Настройка стиля для виджетов
            style.configure('Treeview', background='#333333', foreground='white', fieldbackground='#333333')
            style.map('Treeview', background=[('selected', '#007fff')], foreground=[('selected', '#444444')])
        
    
    except Exception as e:
        log_user_action(f"Error toggling theme for user {ID}: {e}", status="ERROR")



def fix_table_size(table_widget):
    """Фиксируем размеры столбцов и строк таблицы, чтобы они не менялись при смене тем"""
    # Установите фиксированные значения ширины для столбцов
    column_widths = {
        "1": 185,
        "2": 80,
        "3": 100,
        "4": 80,
        "5": 120,
        "6": 80,
        "7": 390
    }

    for col in table_widget['columns']:
        # Устанавливаем фиксированную ширину столбцов
        table_widget.column(col, width=column_widths[col])
    
    # Устанавливаем фиксированную высоту строк
    table_widget.configure(height=13)  # Это уже задано при инициализации таблицы

    # Обновляем виджет таблицы, чтобы отобразить изменения
    table_widget.update_idletasks()


def fix_table_size2(table_widget2):
    """Фиксируем размеры столбцов и строк таблицы, чтобы они не менялись при смене тем"""
    # Установите фиксированные значения ширины для столбцов
    column_widths = {
        "1": 110,
    }

    for col in table_widget2['columns']:
        # Устанавливаем фиксированную ширину столбцов
        table_widget2.column(col, width=column_widths[col])
    
    # Устанавливаем фиксированную высоту строк
    table_widget2.configure(height=4)  # Это уже задано при инициализации таблицы

    # Обновляем виджет таблицы, чтобы отобразить изменения
    table_widget2.update_idletasks()


def is_theme_loaded(mainWindow, theme_name):
    # Проверяем, загружена ли тема
    loaded_themes = mainWindow.tk.call("ttk::style", "theme", "names")
    return theme_name in loaded_themes


# Сериализация всей таблицы в JSON
def serialize_table(ID, filename="table_data.json"):
    try:
        # Получаем текущие дату и время в формате "YYYY-MM-DD_HH-MM"
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
        # Формируем имя файла с учетом времени
        filename = f"table_data_{current_time}.json"
        # Получаем данные таблицы из базы данных
        result = connect(ID)
        # Преобразуем результат в список словарей
        table_data = [{"Название": row[0], "Графика": row[1], "Разработчик": row[2], "Год выпуска": row[3],
                       "Наигранные часы": row[4], "Оценка": row[5], "Комментарий": row[6]} for row in result]

        # Сериализуем данные в файл JSON
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(table_data, f, ensure_ascii=False, indent=4)
        log_user_action(f"User {ID} serialized table data to {filename}")
        messagebox.showinfo("Успех", f"Table successfully saved to {filename}!")
    except Exception as e:
        log_user_action(f"Error saving table for user {ID}: {e}", status="ERROR")
        messagebox.showerror("Ошибка", f"Не удалось сохранить таблицу: {e}")


# Десериализация всей таблицы из JSON с выбором файла
def deserialize_table(tree, ID):
    try:
        # Открытие диалогового окна для выбора файла
        filename = filedialog.askopenfilename(
            title="Выберите JSON файл",
            filetypes=(("JSON файлы", "*.json"), ("Все файлы", "*.*"))
        )

        if not filename:  # Если файл не был выбран
            return

        # Чтение данных из выбранного JSON файла
        with open(filename, 'r', encoding='utf-8') as f:
            table_data = json.load(f)
        # Очищаем таблицу в интерфейсе
        for item in tree.get_children():
            tree.delete(item)

        # Очищаем данные в базе данных для данного пользователя
        clear_user_games(ID)
        # Вставляем данные в таблицу и в базу данных
        for row in table_data:
            # Вставляем данные в интерфейс
            tree.insert("", END, values=(row["Название"], row["Графика"], row["Разработчик"],
                                         row["Год выпуска"], row["Наигранные часы"], row["Оценка"], row["Комментарий"]))
            
            # Создаем словарь для передачи в функцию addGame
            game = {
                'title': row["Название"],
                'graphics': row["Графика"],
                'devoloper': row["Разработчик"],
                'year': row["Год выпуска"],
                'hours': row["Наигранные часы"],
                'rating': row["Оценка"],
                'comm': row["Комментарий"]
            }

            # Добавляем данные в базу данных
            addGame(game, ID) 
        log_user_action(f"User {ID} deserialized table from {filename}")
        messagebox.showinfo("Успех", "Таблица успешно загружена из файла и сохранена в базе данных!")
    except Exception as e:
        log_user_action(f"Error deserializing table for user {ID}: {e}", status="ERROR")
        messagebox.showerror("Ошибка", f"Не удалось загрузить таблицу: {e}")


# Сериализация отдельной строки
def serialize_row(row_data, ID, filename="row_data.json"):
    try:
        # Получаем текущие дату и время в формате "YYYY-MM-DD_HH-MM"
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
        
        # Формируем имя файла с учетом времени
        filename = f"row_data_{current_time}.json"

        # Преобразуем строку в словарь
        row_dict = {
            "Название": row_data[0],
            "Графика": row_data[1],
            "Разработчик": row_data[2],
            "Год выпуска": row_data[3],
            "Наигранные часы": row_data[4],
            "Оценка": row_data[5],
            "Комментарий": row_data[6]
        }

        # Сериализуем строку в JSON файл
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(row_dict, f, ensure_ascii=False, indent=4)
        log_user_action(f"User {ID} serialized row data to {filename}")
        messagebox.showinfo("Успех", f"Строка успешно сохранена в {filename}!")
    except Exception as e:
        log_user_action(f"Error saving row for user {ID}: {e}", status="ERROR")
        messagebox.showerror("Ошибка", f"Не удалось сохранить строку: {e}")

# Десериализация отдельной строки из JSON с выбором файла
def deserialize_row(tree, ID):
    try:
        # Открытие диалогового окна для выбора файла
        filename = filedialog.askopenfilename(
            title="Выберите JSON файл",
            filetypes=(("JSON файлы", "*.json"), ("Все файлы", "*.*"))
        )

        if not filename:  # Если файл не был выбран
            return

        # Чтение данных из выбранного JSON файла
        with open(filename, 'r', encoding='utf-8') as f:
            row_dict = json.load(f)

        # Вставляем строку в таблицу
        tree.insert("", END, values=(row_dict["Название"], row_dict["Графика"], row_dict["Разработчик"],
                                     row_dict["Год выпуска"], row_dict["Наигранные часы"],
                                     row_dict["Оценка"], row_dict["Комментарий"]))

        # Добавляем данные в базу данных
        game = {
            'title': row_dict["Название"],
            'graphics': row_dict["Графика"],
            'devoloper': row_dict["Разработчик"],
            'year': row_dict["Год выпуска"],
            'hours': row_dict["Наигранные часы"],
            'rating': row_dict["Оценка"],
            'comm': row_dict["Комментарий"]
        }
        
        addGame(game, ID)
        log_user_action(f"User {ID} deserialized row from {filename}")
        messagebox.showinfo("Успех", "Строка успешно загружена из файла и сохранена в базе данных!")
    except Exception as e:
        log_user_action(f"Error deserializing row for user {ID}: {e}", status="ERROR")
        messagebox.showerror("Ошибка", f"Не удалось загрузить строку: {e}")


def save_selected_row(tree, ID):
    items = tree.selection()
    if items:
        for item in items:
            row_data = tree.item(item, "values")
            serialize_row(row_data, ID)

def saveGame(nameEntry,  clicks, devoloperEntry, combo, hoursEntry, ratingEntry, commEntry, tree, ID):
    title = nameEntry.get()
    graphics = clicks
    devoloper = devoloperEntry.get()
    year = combo.get()
    hours = hoursEntry.get()
    rating = ratingEntry.get()
    comm = commEntry.get()
    val_game = Games(title, graphics, devoloper, year, hours, rating, comm)

    if not check(title, ID):

        if not title or not rating or not graphics or not devoloper or not year or not hours or not commEntry:
            messagebox.showwarning("Ошибка", "Заполните все поля")
            return
        if not val_game.validate_title():
            messagebox.showwarning("Ошибка", "Введено некорректное название")
            return

        if not val_game.validate_rating():
            messagebox.showwarning("Ошибка", "Введена некорректная оценка")
            return

        if not val_game.validate_hours():
            messagebox.showwarning("Ошибка", "Введено некорректное число часов в игре")
            return

        if not val_game.validate_devoloper():
            messagebox.showwarning("Ошибка", "Введён некорректный жанр")
            return

        if not val_game.validate_year():
            messagebox.showwarning("Ошибка", "Введён некорректный год")
            return
        
        if not val_game.validate_comm():
            messagebox.showwarning("Ошибка", "Введён лимит символов на комментарий")
            return
        
        if rating.count('.') > 1:
            messagebox.showwarning("Ошибка", "Введена некорректная оценка")
            return
        else:
            if float(rating) > 10:
                messagebox.showwarning("Ошибка", "Введена некорректная оценка")
                return

        if int(hours) < 0:
            messagebox.showwarning("Ошибка", "Введено некорректное число часов в игре")
            return

        newGame = Games(title, graphics, devoloper, year, int(hours), float(rating), comm)
        addDSGame(newGame, ID)
        updateTable(tree, ID)
        log_user_action(f"User {ID} saved game: {title}")
        nameEntry.delete(0, END)
        ratingEntry.delete(0, END)
        devoloperEntry.delete(0, END)
        hoursEntry.delete(0, END)
        commEntry.delete(0, END)
        
        messagebox.showinfo("Успех", "Данные успешно сохранены")

    else:
        messagebox.showwarning("Ошибка", "Игра с таким названием уже есть в базе данных")


def changeGame(changeName, nameEntry, clicks, devoloperEntry, yearEntry, hoursEntry, ratingEntry, commEntry, tree, ID):
    if check(changeName.get(), ID):
        oldGame = getGamesData(changeName.get(), ID)
        val_game = Games(nameEntry.get(), clicks, devoloperEntry.get(), yearEntry.get(), hoursEntry.get(), ratingEntry.get(), commEntry.get())

        if nameEntry.get() != "":
            if val_game.validate_title():
                title = nameEntry.get()
                if check(title, ID):
                    messagebox.showwarning("Ошибка", "Игра с таким названием уже есть в базе данных")
                    return
            else:
                messagebox.showwarning("Ошибка", "Введено некорректное название")
                return
        else:
            title = oldGame.title
        if ratingEntry.get() != "":
            if val_game.validate_rating():
                rating = ratingEntry.get()
            else:
                messagebox.showwarning("Ошибка", "Введена некорректная оценка")
                return
        else:
            rating = oldGame.rating

        if hoursEntry.get() != "":
            if val_game.validate_hours():
                hours = hoursEntry.get()
            else:
                messagebox.showwarning("Ошибка", "Введено некорректное число часов в игре")
                return
        else:
            hours = oldGame.hours

        if devoloperEntry.get() != "":
            if val_game.validate_devoloper():
                devoloper = devoloperEntry.get()
            else:
                messagebox.showwarning("Ошибка", "Введён некорректный разработчик")
                return
        else:
            devoloper = oldGame.devoloper

        if rating.count('.') > 1:
            messagebox.showwarning("Ошибка", "Введена некорректная оценка")
            return
        else:
            if float(rating) > 10:
                messagebox.showwarning("Ошибка", "Введена некорректная оценка")
                return

        if int(hours) < 0:
            messagebox.showwarning("Ошибка", "Введено некорректное число часов в игре")
            return

        year = yearEntry.get()

        if not val_game.validate_year():
            messagebox.showwarning("Ошибка", "Введён некорректный год")
            return
        
        if commEntry.get() != "":
            if val_game.validate_comm():
                comm = commEntry.get()
            else:
                messagebox.showwarning("Ошибка", "Введена некорректная оценка")
                return
        else:
            comm = oldGame.comm

        game = Games(title, clicks, devoloper, year, hours, rating, comm)

        changeData(game, changeName.get(), ID)
        updateTable(tree, ID)
        messagebox.showinfo("Успех", "Информация об игре успешно обновлена")
        log_user_action(f"User {ID} changed game: {changeName.get()} to {title}")
    else:
        messagebox.showwarning("Ошибка", "Игры с таким названием нет в базе данных")


def deleteGame(deleteEntry, tree, deleteWindow, ID):
    deleteName = deleteEntry.get()
    if check(deleteName, ID):
        deleteGameFromDatabase(deleteName, ID)
        deleteEntry.delete(0, END)
        updateTable(tree, ID)
        messagebox.showinfo("Успех", f"Игра {deleteName} успешно удалена из базы данных")
        deleteWindow.destroy()
        log_user_action(f"User {ID} deleted game: {deleteName}")
    else:
        messagebox.showwarning("Ошибка", "Игры с таким названием нет в базе данных")


def makeFile(ID):
    result = connect(ID)
    doc = Document()
    table = doc.add_table(rows=1, cols=7)

    hdr_cells = table.rows[0].cells

    hdr_cells[0].text = 'Название'
    hdr_cells[1].text = 'Графика'
    hdr_cells[2].text = 'Разработчик'
    hdr_cells[3].text = 'Год выпуска'
    hdr_cells[4].text = 'Наигранные часы'
    hdr_cells[5].text = 'Оценка'
    hdr_cells[6].text = 'Комментарий'

    for row in result:
        print(row)
        row_cells = table.add_row().cells
        for i in range(0, 6 + 1):
            row_cells[i].text = str(row[i])

    doc.save('GamesTable.docx')
    log_user_action(f"User {ID} created file: GamesTable.docx")
    messagebox.showinfo('Успех', "Файл GamesTable.docx успешно сформирован")


def updateTable(tree, ID):
    updateResult = connect(ID)

    for i in tree.get_children():
        tree.delete(i)
    for updateRow in updateResult:
        tree.insert("", END, values=(updateRow[0], updateRow[1], updateRow[2],
                                     updateRow[3], updateRow[4], updateRow[5], updateRow[6]))


