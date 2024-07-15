
# User je klasa korisnika koja sadrzi korisnicko ime, lozinku, ime, prezime, i poziciju korisnika
class User:
    def __init__(self, username, password, name, last_name, access_level):
        self.username = username
        self.password = password
        self.name = name
        self.last_name = last_name
        self.access_level = access_level
