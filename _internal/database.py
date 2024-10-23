from Class import *
import sqlite3

file = open('_internal/query.txt', 'r')
a = file.readlines()


def createDB():
    cnx = sqlite3.connect('Coursework.db')
    cursor = cnx.cursor()

    query = a[0]

    cursor.execute(query)
    cnx.commit()
    cursor.close()
    cnx.close()


def addCustomer(customer):
    cnx = sqlite3.connect('Coursework.db')

    cursor = cnx.cursor()
    query = a[1]

    cursor.execute(query, (customer.username, customer.password))

    cnx.commit()
    cursor.close()
    cnx.close()


def createGameTable(ID):
    cnx = sqlite3.connect('Coursework.db')

    cursor = cnx.cursor()

    table_name = f'user{ID}games '
    line = a[2].split("!")
    query = line[0] + table_name + line[1] + str(ID) + line[2]
    cursor.execute(query)

    cursor.close()
    cnx.close()

def addDSGame(game, ID):
    cnx = sqlite3.connect('Coursework.db')

    cursor = cnx.cursor()

    table_name = f'user{ID}games'
    line = a[3].split("!")
    query = line[0] + table_name + line[1]
    cursor.execute(query, (game.title, game.graphics, game.devoloper, game.year, game.hours, game.rating, game.comm))

    cnx.commit()
    cursor.close()
    cnx.close()

def clear_user_games(ID):
    cnx = sqlite3.connect('Coursework.db')

    cursor = cnx.cursor()

    table_name = f'user{ID}games'
    line = a[12].split("!")
    query = line[0] + table_name

    cursor.execute(query)

    cnx.commit()
    cursor.close()
    cnx.close()

def addGame(game, ID):
    cnx = sqlite3.connect('Coursework.db')
    cursor = cnx.cursor()

    table_name = f'user{ID}games'
    
    line = a[3].split("!")
    query = line[0] + table_name + line[1]
    
    # Передаем данные как список
    cursor.execute(query, (game['title'], game['graphics'], game['devoloper'], game['year'], game['hours'], game['rating'], game['comm']))

    cnx.commit()
    cursor.close()
    cnx.close()


def deleteGameFromDatabase(name, ID):
    cnx = sqlite3.connect('Coursework.db')

    cursor = cnx.cursor()

    table_name = f'user{ID}games'
    line = a[4].split("!")
    query = line[0] + table_name + line[1]

    cursor.execute(query, (name, ))

    cnx.commit()
    cursor.close()
    cnx.close()


def changeData(game, oldName, ID):
    cnx = sqlite3.connect('Coursework.db')
    cursor = cnx.cursor()

    table_name = f'user{ID}games'
    line = a[5].split("!")
    query = line[0] + table_name + line[1]

    cursor.execute(query, (game.title, game.graphics, game.devoloper, game.year, game.hours, game.rating, game.comm, oldName))

    cnx.commit()

    cursor.close()
    cnx.close()


def connect(ID):
    mydb = sqlite3.connect('Coursework.db')

    cursor = mydb.cursor()

    table_name = f'user{ID}games'

    query = a[6] + table_name

    cursor.execute(query)

    result = cursor.fetchall()

    cursor.close()
    mydb.close()

    return result


def checkUsername(username):
    mydb = sqlite3.connect('Coursework.db')

    mycursor = mydb.cursor()

    query = a[7]

    mycursor.execute(query, (username, ))

    result = mycursor.fetchone()
    if result is not None:
        return True
    else:
        return False


def getID(username):
    mydb = sqlite3.connect('Coursework.db')

    mycursor = mydb.cursor()

    query = a[8]

    mycursor.execute(query, (username, ))

    result = mycursor.fetchall()
    if result is not None:
        return result
    else:
        return None


def check(name, ID):
    mydb = sqlite3.connect('Coursework.db')

    mycursor = mydb.cursor()

    table_name = f'user{ID}games'
    line = a[9].split("!")
    query = line[0] + table_name + line[1]
    mycursor.execute(query, (name, ))

    result = mycursor.fetchone()
    if result is not None:
        return True
    else:
        return False


def getGamesData(name, ID):
    mydb = sqlite3.connect('Coursework.db')

    mycursor = mydb.cursor()

    table_name = f'user{ID}games'
    line = a[10].split("!")
    query = line[0] + table_name + line[1]
    mycursor.execute(query, (name, ))
    result = mycursor.fetchall()
    if result is not None:

        for line in result:
            game = Games(line[0], line[1], line[2], line[3], line[4], line[5], line[6])

            return game
    else:
        return None


def getCustomersData():
    mydb = sqlite3.connect('Coursework.db')

    mycursor = mydb.cursor()

    query = a[11]

    mycursor.execute(query)

    result = mycursor.fetchall()

    mycursor.close()
    mydb.close()

    return result
