import re


class Games:
    def __init__(self, title, graphics, devoloper, year, hours, rating, comm):
        """Свойства игры"""
        self.title = title
        self.graphics = graphics
        self.devoloper = devoloper
        self.year = year
        self.hours = hours
        self.rating = rating
        self.comm = comm

    def validate_title(self):
        return len(self.title) <= 40 and bool(re.match("^[а-яА-ЯёЁa-zA-Z0-9-:()'-_ ]+$", self.title))

    def validate_year(self):
        return (len(self.year) == 4 and bool(re.match("^[0-9]+$", self.year))
                and 1961 <= int(self.year) <= 2024)

    def validate_devoloper(self):
        return len(self.devoloper) <= 40 and bool(re.match("^[а-яА-ЯёЁa-zA-Z0-9-_:() ]+$", self.devoloper))

    def validate_hours(self):
        return len(self.hours) <= 5 and self.hours.isdigit()

    def validate_rating(self):
        return len(self.rating) <= 4 and bool(re.match("^[0-9.]+$", self.rating))
    
    def validate_comm(self):
        return len(self.comm) <= 55 


class Customer:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def validate_login(self):
        return len(self.username) <= 20 and bool(re.match("^[а-яА-ЯёЁa-zA-Z0-9_-]+$", self.username))

    def validate_password(self):
        return (20 >= len(self.password) >= 8 and bool(re.match("^[a-zA-Z0-9?!@*+%&_-]+$", self.password))
                and any(c.islower() for c in self.password) and
                any(c.isupper() for c in self.password) and any(c.isdigit() for c in self.password) and
                bool(re.search(r'[?!@*_+%&-]', self.password)))


