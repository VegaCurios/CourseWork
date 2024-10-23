import tkinter
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from functions import *
from database import *
from Class import *


numbers = list(range(1961, 2025))
clicks = "Плохая"
changeClicks = "Плохая"
grade = list(range(0, 11))

def chooseGraphics(button):
    global clicks
    if clicks == "Плохая":
        clicks = "Хорошая"
        button["text"] = clicks
    else:
        clicks = "Плохая"
        button["text"] = clicks


def changeGraphics(button):
    global changeClicks
    if changeClicks == "Плохая":
        changeClicks = "Хорошая"
        button["text"] = changeClicks
    else:
        changeClicks = "Плохая"
        button["text"] = changeClicks

def authorization(loginEntry, passEntry, passWindow):
    try:
        login = loginEntry.get()
        val_customer = Customer(login, None)

        if not val_customer.validate_login():
            messagebox.showwarning("Ошибка", 'Введён некорректный логин!')
            return

        result = getID(login)
        if result is None:
            messagebox.showwarning("Ошибка", "Логина нет в базе! Введите существующий логин")
            log_user_action(f"Failed login attempt for user {login}", status="ERROR")
            return

        ID = 0
        enPass = ""
        for value in result:
            ID = value[0]
            enPass = value[1]

        password = passEntry.get()
        enPassword = hashlib.md5(password.encode()).hexdigest()

        if enPass == enPassword:
            messagebox.showinfo("Успех", "Пароль верный! Доступ разрешен")
            log_user_action(f"User {login} successfully authorized")
            passWindow.destroy()
            mainInterface(ID)
        else:
            messagebox.showerror("Ошибка", "Пароль неверный! Доступ запрещен")
            passEntry.delete(0, END)
            log_user_action(f"Failed password attempt for user {login}", status="ERROR")
    except Exception as e:
        log_user_action(f"Error during authorization for user {login}: {e}", status="ERROR")


def register(loginEntry, passwordEntry, repeatedEntry, regWindow):
    try:
        login = loginEntry.get()
        password = passwordEntry.get()
        repPassword = repeatedEntry.get()

        val_customer = Customer(login, password)

        if not val_customer.validate_login():
            messagebox.showwarning("Ошибка", 'Введён некорректный логин!\n'
                                             'Используйте кириллицу, латиницу,\n'
                                             'цифры, "-" и "_"')
            log_user_action(f"Failed registration attempt with invalid login: {login}", status="ERROR")
            return

        if checkUsername(login):
            messagebox.showwarning("Ошибка", "Логин занят! Придумайте другой")
            log_user_action(f"Failed registration attempt: login {login} is already taken", status="ERROR")
            return

        if not val_customer.validate_password():
            messagebox.showwarning("Ошибка", "Введён некорректный пароль!\n"
                                             "Используйте латиницу, цифры\n"
                                             "и специальные символы(?!@*_+-%&)")
            passwordEntry.delete(0, END)
            repeatedEntry.delete(0, END)
            log_user_action(f"Failed registration attempt with invalid password for user {login}", status="ERROR")
            return

        if password != repPassword:
            messagebox.showwarning("Ошибка", "Пароли не совпадают")
            passwordEntry.delete(0, END)
            repeatedEntry.delete(0, END)
            log_user_action(f"Failed registration attempt: passwords do not match for user {login}", status="ERROR")
            return

        enPassword = hashlib.md5(password.encode()).hexdigest()
        customer = Customer(login, enPassword)
        log_user_action(f"User {login} successfully registered")
        addCustomer(customer)
        result = getID(login)
        ID = 0
        for value in result:
            ID = value[0]
        createGameTable(ID)

        messagebox.showinfo("Успех", "Вы успешно зарегистрированы!")
        regWindow.destroy()
    except Exception as e:
        log_user_action(f"Error during registration for user {login}: {e}", status="ERROR")

def customerGamesTable(tree):
    items = tree.selection()
    if items == ():
        return

    customerWindow = Toplevel()

    customerWindow.geometry("1220x370+350+260")
    icon = PhotoImage(file="icons/icon.png")
    customerWindow.iconphoto(False, icon)
    customerWindow.resizable(width=False, height=False)

    table = ttk.Treeview(customerWindow)

    table["columns"] = ("1", "2", "3", "4", "5", "6", "7")
    table["show"] = "headings"
    table["height"] = "13"

    table.heading("1", text="Название")
    table.heading("2", text="Графика")
    table.heading("3", text="Разработчик")
    table.heading("4", text="Год выпуска")
    table.heading("5", text="Наигранные часы")
    table.heading("6", text="Оценка")
    table.heading("7", text="Комментарий")

    table.column("1", width=185)
    table.column("2", width=80)
    table.column("3", width=100)
    table.column("4", width=80)
    table.column("5", width=120)
    table.column("6", width=80)
    table.column("7", width=390)

    value = ""

    for item in items:
        line = tree.item(item)
        value = line["values"]
    print(value)
    customerWindow.title(f"Таблица пользователя {value[0]}")

    res = getID(value[0])
    ID = 0
    for item in res:
        ID = item[0]
    print(ID)
    result = connect(ID)
    for row in result:
        table.insert("", END, values=(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

    table.place(x=610, y=185, anchor=CENTER)


def deleteInterface(tree, ID):
    global deleteWindow
    deleteWindow = Toplevel()
    deleteWindow.title("Удаление")
    deleteWindow.geometry("280x180+800+375")
    icon = PhotoImage(file="icons/icon.png")
    deleteWindow.iconphoto(False, icon)
    deleteWindow.resizable(width=False, height=False)

    frame = ttk.Frame(deleteWindow)
    frame.pack(fill='both', expand=True)

    deleteLabel = ttk.Label(deleteWindow, text="Введите название игры,\nкоторую хотите удалить")
    deleteLabel.place(x=140, y=40, anchor=CENTER)
    deleteEntry = ttk.Entry(deleteWindow)
    deleteEntry.place(x=140, y=90, anchor=CENTER)

    deleteButton = ttk.Button(deleteWindow, text="Удалить", command=lambda: deleteGame(deleteEntry, tree, deleteWindow, ID))
    deleteButton.place(x=140, y=145, anchor=CENTER)
    deleteWindow.grab_set()

def addInterface(tree, ID):
    global addWindow
    addWindow = Toplevel()
    addWindow.title("Добавление игры")
    addWindow.geometry("320x600+800+150")
    icon = PhotoImage(file="icons/icon.png")
    addWindow.iconphoto(False, icon)
    addWindow.resizable(width=False, height=False)

    frame = ttk.Frame(addWindow)
    frame.pack(fill='both', expand=True)

    nameLabel = ttk.Label(addWindow, text="Название игры:")
    nameLabel.place(x=155, y=40, anchor=CENTER)
    nameEntry = ttk.Entry(addWindow)
    nameEntry.place(x=155, y=70, anchor=CENTER)

    graphicsLabel = ttk.Label(addWindow, text="Качество графики:")
    graphicsLabel.place(x=155, y=110, anchor=CENTER)
    graphicsButton = ttk.Button(addWindow, text="Плохая", command=lambda: chooseGraphics(graphicsButton))
    graphicsButton.place(x=155, y=140, anchor=CENTER)

    devoloperLabel = ttk.Label(addWindow, text="Разработчик игры:")
    devoloperLabel.place(x=155, y=180, anchor=CENTER)
    devoloperEntry = ttk.Entry(addWindow)
    devoloperEntry.place(x=155, y=210, anchor=CENTER)

    yearLabel = ttk.Label(addWindow, text="Год выпуска:")
    yearLabel.place(x=155, y=250, anchor=CENTER)
    combo = ttk.Combobox(addWindow)
    combo['values'] = numbers
    combo.current(39)
    combo.place(x=155, y=280, anchor=CENTER)

    hoursLabel = ttk.Label(addWindow, text="Часы в игре:")
    hoursLabel.place(x=155, y=320, anchor=CENTER)
    hoursEntry = ttk.Entry(addWindow)
    hoursEntry.place(x=155, y=350, anchor=CENTER)

    ratingLabel = ttk.Label(addWindow, text="Ваша оценка:")
    ratingLabel.place(x=155, y=390, anchor=CENTER)
    ratingEntry = ttk.Combobox(addWindow)
    ratingEntry['values'] = grade
    ratingEntry.current(0)
    ratingEntry.place(x=155, y=420, anchor=CENTER)

    CommLabel = ttk.Label(addWindow, text="Комментарий к игре (max 55 символов):")
    CommLabel.place(x=155, y=460, anchor=CENTER)
    CommEntry = ttk.Entry(addWindow)
    CommEntry.place(x=155, y=490, anchor=CENTER)

    saveButton = ttk.Button(addWindow, text="Сохранить", command=lambda: saveGame(nameEntry, clicks, devoloperEntry,
                                                                         combo, hoursEntry, ratingEntry, CommEntry, tree, ID))
    saveButton.place(x=155, y=553, anchor=CENTER)
    addWindow.grab_set()

def changeInterface(tree, ID):
    global changeWindow
    changeWindow = Toplevel()
    changeWindow.title("Изменение данных")
    changeWindow.geometry("320x650+800+145")
    icon = PhotoImage(file="icons/icon.png")
    changeWindow.iconphoto(False, icon)
    changeWindow.resizable(width=False, height=False)

    frame = ttk.Frame(changeWindow)
    frame.pack(fill='both', expand=True)

    changeNameLabel = ttk.Label(changeWindow, text="Название игры, данные которой хотите изменить:")
    changeNameLabel.place(x=160, y=30, anchor=CENTER)
    changeNameEntry = ttk.Entry(changeWindow)
    changeNameEntry.place(x=160, y=70, anchor=CENTER)

    changedNameLabel = ttk.Label(changeWindow, text="Название игры:")
    changedNameLabel.place(x=160, y=110, anchor=CENTER)
    changedNameEntry = ttk.Entry(changeWindow)
    changedNameEntry.place(x=160, y=140, anchor=CENTER)

    changedGraphicsLabel = ttk.Label(changeWindow, text="Качество графики:")
    changedGraphicsLabel.place(x=160, y=180, anchor=CENTER)
    changedGraphicsButton = ttk.Button(changeWindow, text="Плохая", command=lambda: changeGraphics(changedGraphicsButton))
    changedGraphicsButton.place(x=160, y=210, anchor=CENTER)

    changeddevoloperLabel = ttk.Label(changeWindow, text="Разработчик игры:")
    changeddevoloperLabel.place(x=160, y=250, anchor=CENTER)
    changeddevoloperEntry = ttk.Entry(changeWindow)
    changeddevoloperEntry.place(x=160, y=280, anchor=CENTER)

    changedYearLabel = ttk.Label(changeWindow, text="Год выпуска:")
    changedYearLabel.place(x=160, y=320, anchor=CENTER)
    changedCombo = ttk.Combobox(changeWindow)
    changedCombo['values'] = numbers
    changedCombo.current(39)
    changedCombo.place(x=160, y=350, anchor=CENTER)

    hoursLabel = ttk.Label(changeWindow, text="Часы в игре:")
    hoursLabel.place(x=160, y=390, anchor=CENTER)
    hoursEntry = ttk.Entry(changeWindow)
    hoursEntry.place(x=160, y=420, anchor=CENTER)

    changedRatingLabel = ttk.Label(changeWindow, text="Ваша оценка:")
    changedRatingLabel.place(x=160, y=460, anchor=CENTER)
    changedRatingEntry = ttk.Combobox(changeWindow)
    changedRatingEntry['values'] = grade
    changedRatingEntry.current(0)
    changedRatingEntry.place(x=160, y=490, anchor=CENTER)
    
    changedCommLabel = ttk.Label(changeWindow, text="Комментарий к игре (max 55 символов):")
    changedCommLabel.place(x=160, y=530, anchor=CENTER)
    changedCommEntry = ttk.Entry(changeWindow)
    changedCommEntry.place(x=160, y=560, anchor=CENTER)

    changeGameButton = ttk.Button(changeWindow, text="Сохранить", command=lambda: changeGame(changeNameEntry,
                                                                                         changedNameEntry,
                                                                                         changeClicks,
                                                                                         changeddevoloperEntry,
                                                                                         changedCombo,
                                                                                         hoursEntry,
                                                                                         changedRatingEntry,
                                                                                         changedCommEntry,
                                                                                         tree, ID))
    changeGameButton.place(x=160, y=615, anchor=CENTER)

    changeNameEntry.delete(0, END)
    changedNameEntry.delete(0, END)
    changedRatingEntry.delete(0, END)
    changeddevoloperEntry.delete(0, END)
    hoursEntry.delete(0, END)
    changedCommEntry.delete(0, END)
    changeWindow.grab_set()


def mainInterface(ID):
    mainWindow = tkinter.Tk()
    mainWindow.title("GamesDatabase")
    mainWindow.geometry("1320x480+300+185")
    icon = PhotoImage(file="icons/icon.png")
    mainWindow.iconphoto(False, icon)
    mainWindow.resizable(width=False, height=False)
    mainWindow.tk.call('source', 'Forest/forest-dark.tcl')
    ttk.Style().theme_use('forest-dark')


    setTableLabel = ttk.Label(mainWindow, text="Ваши игры", font=('Times', 18))
    setTableLabel.place(x=560, y=35, anchor=CENTER)

    setCustomerLabel = ttk.Label(mainWindow, text="Список пользователей", font=('Times', 13))
    setCustomerLabel.place(x=1203, y=35, anchor=CENTER)

    tree = ttk.Treeview(mainWindow, selectmode="browse")
    tree["columns"] = ("1", "2", "3", "4", "5", "6", "7")
    tree["show"] = "headings"
    tree["height"] = "13"

    tree.heading("1", text="Название")
    tree.heading("2", text="Графика")
    tree.heading("3", text="Разработчик")
    tree.heading("4", text="Год выпуска")
    tree.heading("5", text="Наигранные часы")
    tree.heading("6", text="Оценка")
    tree.heading("7", text="Комментарий")

    tree.column("1", width=185)
    tree.column("2", width=80)
    tree.column("3", width=100)
    tree.column("4", width=80)
    tree.column("5", width=120)
    tree.column("6", width=80)
    tree.column("7", width=390)

    result = connect(ID)
    for row in result:
        tree.insert("", END, values=(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

    tree.place(x=575, y=225, anchor=CENTER)

    addButton = ttk.Button(mainWindow, text="Добавить игру", command=lambda: addInterface(tree, ID))
    addButton.place(x=100, y=425, anchor=CENTER)

    deleteButton = ttk.Button(mainWindow, text="Удалить игру", command=lambda: deleteInterface(tree, ID))
    deleteButton.place(x=228, y=425,  anchor=CENTER)

    fileButton = ttk.Button(mainWindow, text="Сформировать таблицу в docx файл", command=lambda: makeFile(ID))
    fileButton.place(x=421, y=425, anchor=CENTER)

    changeButton = ttk.Button(mainWindow, text="Внести изменения", command=lambda: changeInterface(tree, ID))
    changeButton.place(x=631, y=425, anchor=CENTER)

    tableButton = ttk.Button(mainWindow, text="Сформировать таблицу выбранного пользователя", command=lambda: customerGamesTable(table))
    tableButton.place(x=882, y=425, anchor=CENTER)

    themeButton = ttk.Checkbutton(mainWindow, text="Сменить тему", style="Switch", command=lambda: [toggle_theme(mainWindow, ID, addWindow, deleteWindow, changeWindow),fix_table_size(tree),fix_table_size2(table)])
    themeButton.place(x=1136, y=415)

    saveRowButton = ttk.Button(mainWindow, text="  Экспортировать строку"  , command=lambda: save_selected_row(tree,ID))
    saveRowButton.place(x=1210, y=372, anchor=CENTER)

    loadRowButton = ttk.Button(mainWindow, text=" Импортировать строку  ", command=lambda: deserialize_row(tree, ID))
    loadRowButton.place(x=1210, y=317, anchor=CENTER)

    saveTableButton = ttk.Button(mainWindow, text="Экспортировать таблицу", command=lambda: serialize_table(ID))
    saveTableButton.place(x=1210, y=262, anchor=CENTER)

    loadTableButton = ttk.Button(mainWindow, text=" Импортировать таблицу ", command=lambda: deserialize_table(tree,ID))
    loadTableButton.place(x=1210, y=210, anchor=CENTER)


    table = ttk.Treeview(mainWindow, selectmode="browse")
    table["columns"] = "1"
    table["show"] = ""
    table["height"] = "4"

    table.column("1", width=110)

    result = getCustomersData()
    for row in result:
        table.insert("", END, values=(row[0]))

    table.place(x=1130, y=65)



    global fileResult
    global addWindow, deleteWindow, changeWindow
    addWindow = None
    deleteWindow = None
    changeWindow = None

    mainWindow.mainloop()


def loginInterface():
    createDB()
    passWindow = tkinter.Tk()
    passWindow.title("Вход")
    passWindow.geometry("500x400+700+300")
    icon = PhotoImage(file="icons/pass_icon.png")
    passWindow.tk.call('source', 'Forest/forest-dark.tcl')
    ttk.Style().theme_use('forest-dark')

    passWindow.iconphoto(False, icon)
    passWindow.resizable(width=False, height=False)

    mainlabel = ttk.Label(passWindow, text="GAMESDATABASE", font=('Fantasy', 14))
    mainlabel.place(x=240, y=52, anchor=CENTER)

    loginlabel = ttk.Label(passWindow, text="Введите логин:", font=('Monospace', 12))
    loginlabel.place(x=240, y=102, anchor=CENTER)
    loginEntry = ttk.Entry(passWindow, font=('Monospace', 12), foreground='#999999')
    loginEntry.place(x=240, y=142, anchor=CENTER)

    label = ttk.Label(passWindow, text="Введите пароль:", font=('Monospace', 12))
    label.place(x=240, y=192, anchor=CENTER)
    passEntry = ttk.Entry(passWindow, show="*", font=('Monospace', 12), foreground='#999999')
    passEntry.place(x=240, y=232, anchor=CENTER)

    passButton = ttk.Button(passWindow, text="Войти", command=lambda: authorization(
                                                            loginEntry, passEntry, passWindow))
    passButton.place(x=190, y=292, anchor=CENTER)

    registrationButton = ttk.Button(passWindow, text="Регистрация", command=registrationInterface)
    registrationButton.place(x=290, y=292, anchor=CENTER)

    passWindow.mainloop()


def registrationInterface():
    regWindow = tkinter.Toplevel()
    regWindow.title("Регистрация")
    regWindow.geometry("500x400+700+300")
    icon = PhotoImage(file="icons/pass_icon.png")

    regWindow.iconphoto(False, icon)
    regWindow.resizable(width=False, height=False)

    loginlabel = ttk.Label(regWindow, text="Регистрация", font=('Fantasy', 14))
    loginlabel.place(x=250, y=45, anchor=CENTER)

    loginlabel = ttk.Label(regWindow, text='Придумайте логин (до 20 символов):', font=('Monospace', 12))
    loginlabel.place(x=250, y=92, anchor=CENTER)
    loginEntry = ttk.Entry(regWindow, font=('Monospace', 12), foreground='#999999')
    loginEntry.place(x=250, y=132, anchor=CENTER)

    passwordlabel = ttk.Label(regWindow, text="Придумайте пароль (8-20 символов):", font=('Monospace', 12))
    passwordlabel.place(x=250, y=172, anchor=CENTER)
    passwordEntry = ttk.Entry(regWindow, show="*", font=('Monospace', 12), foreground='#999999')
    passwordEntry.place(x=250, y=212, anchor=CENTER)

    repeatedlabel = ttk.Label(regWindow, text="Повторите пароль:", font=('Monospace', 12))
    repeatedlabel.place(x=250, y=252, anchor=CENTER)
    repeatedEntry = ttk.Entry(regWindow, show="*", font=('Monospace', 12), foreground='#999999')
    repeatedEntry.place(x=250, y=292, anchor=CENTER)

    passButton = ttk.Button(regWindow, text="Зарегистрироваться", command=lambda: register(
                                                             loginEntry, passwordEntry, repeatedEntry, regWindow))
    passButton.place(x=250, y=352, anchor=CENTER)

    regWindow.grab_set()
    regWindow.mainloop()


loginInterface()





