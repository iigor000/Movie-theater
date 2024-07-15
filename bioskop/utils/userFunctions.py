from model import user


# Funkcija koja ucitava sve korisnike iz baze i vraca listu sa njima
def get_all_users():
    users = []
    with open('./database/users.txt', 'r') as file:
        for line in file.readlines():
            user_string = line.split('|')
            user_to_add = user.User(user_string[0], user_string[1], user_string[2], user_string[3], user_string[4].
                                    replace("\n", ""))
            # Ucitavamo liniju iz fajla, pretvaramo je u niz stringova od kojih pravimo korisnika i smestamo ga u listu
            users.append(user_to_add)
    return users


# Trazimo korisnika u listi po korisnickom imenu i brisemo ga
def delete_user(username, users):
    for one_user in users:
        if one_user.username == username:
            users.remove(one_user)


# Prvo proveravamo da li je neki od karaktera broj i da li postoji | u sifri,
# sto bi pokvarilo skladistenje korisnika u bazi, ako jeste proveravamo duzinu lozinke
def check_password(password):
    has_number = False
    for char in password:
        if char.isdigit():
            has_number = True
        if char == '|':
            return False
    if len(password) > 6 and has_number:
        return True
    return False


# Proveravamo da li u listi postoji korisnik sa istim korisnickim imenom
def check_username(username, users):
    if username == '' or '&' in username or '|' in username:
        return False
    for one_user in users:
        if username == one_user.username:
            return False
    return True


# Korisnik unese korisnicko ime i sifru, pa proveravamo da li postoji neko
# u listi sa tim korisnickim imenom i sifrom, i ako postoji vracamo tog korisnika
def login(users):
    while True:
        username = input("Unesite korisničko ime: ").strip()
        password = input("Unesite lozinku: ").strip()
        for one_user in users:
            if username == one_user.username and password == one_user.password:
                return one_user
        print('Pogrešno korisničko ime ili lozinka, unesite kraj ako želite da odustanete.')
        kraj = input().lower().strip()
        if kraj == 'kraj':
            return None


# Uzimamo sve podatke korisnika i dodajemo ga u listu
def register(users):
    while True:
        username = input("Unesite korisničko ime (| i & su nevalidni karakteri): ").strip()
        if check_username(username, users):
            break
        kraj = input("Već postoji korisnik sa tim korisničkim imenom, uneli ste prazno ime ili "
                     "ste uneli neki nevalidan karakter, unesite kraj ako želite da odustanete.\n").lower().strip()
        if kraj == 'kraj':
            return False
    while True:
        password = input("Unesite lozinku (lozinka mora biti duža od 6 karaktera, sadržati najmanje "
                         "jednu cifru u sebi i | nije validan karakter za lozinku): ").strip()
        good = check_password(password)
        if good:
            break
        kraj = input('Lozinka ne zadovoljava neki od zahteva, unesite kraj ako želite da odustanete.\n').lower().strip()
        if kraj == 'kraj':
            return False

    while True:
        name = input("Unesite ime: ").strip().replace("|", "")
        if name != '':
            break
        kraj = (input('Ime ne sme biti prazno, pokušajte ponovo ili unesite kraj ako želite da odustanete.\n').lower().
                strip())
        if kraj == 'kraj':
            return False
    while True:
        last_name = input("Unesite prezime: ").strip().replace('|', "")
        if last_name != '':
            break
        kraj = (input('Prezime ne sme biti prazno, pokušajte ponovo ili unesite kraj ako želite da odustanete.\n').
                lower().strip())
        if kraj == 'kraj':
            return False

    new_user = user.User(username, password, name, last_name, '0')
    users.append(new_user)
    return True


# Slicno kao funckija za dodavanje korisnika, samo sto sada menadzer bira koju ulogu ce imati korisnik kojeg dodaje
def manager_add_user(users):
    while True:
        role = input("Koja je uloga korisnika:\n1.Prodavac\n2.Menadzer\n").strip()
        if role == '1' or role == '2':
            break
        kraj = input("Pogrešan unos, pokušajte ponovo (ili unesite kraj ako želite da odustanete).").lower().strip()
        if kraj == "kraj":
            return False
    while True:
        username = input("Unesite korisničko ime (| i & su nevalidni karakteri): ").strip()
        good = check_username(username, users)
        if good:
            break
        kraj = input("Korisnik sa datim korisničkim imenom već postoji ili ste uneli nevalidni "
                     "karakter, unesite kraj ako želite da odustanete.\n").lower().strip()
        if kraj == 'kraj':
            return False
    while True:
        password = input("Unesite lozinku (lozinka mora biti duza od 6 karaktera, sadržati najmanje "
                         "jednu cifru u sebi i | nije validan karakter za lozinku): ").strip()
        good = check_password(password)
        if good:
            break
        kraj = input('Lozinka ne zadovoljava neki od zahteva, pokušajte ponovo ili unesite kraj ako '
                     'želite da odustanete.\n').lower().strip()
        if kraj == 'kraj':
            return False
    while True:
        name = input("Unesite ime: ").strip().replace("|", "")
        if name != '':
            break
        kraj = input(
            'Ime ne sme biti prazno, pokušajte ponovo ili unesite kraj ako želite da odustanete.\n').lower().strip()
        if kraj == 'kraj':
            return False
    while True:
        last_name = input("Unesite prezime: ").strip().replace('|', "")
        if last_name != '':
            break
        kraj = input(
            'Prezime ne sme biti prazno, pokušajte ponovo ili unesite kraj ako želite da odustanete.\n').lower().strip()
        if kraj == 'kraj':
            return False

    new_user = user.User(username, password, name, last_name, role)
    users.append(new_user)
    return True


# Cuva sve korisnike u listi nazad u fajl
def save_users(users):
    user_string = ''
    for one_user in users:
        user_string += (one_user.username + '|' + one_user.password + '|' + one_user.name + '|' + one_user.last_name +
                        '|' + one_user.access_level + '\n')
    with open('./database/users.txt', 'w') as file:
        file.write(user_string)


# Funkcija izlistava podatke korisniku i korisnik moze da bira da li
# ih menja ili ne prema tome da li postavi novu vrednost
def change_data(one_user, users):
    print("Vaši trenutni podatci su:\nLozinka: " + one_user.password + '\nIme: ' + one_user.name + '\nPrezime: ' +
          one_user.last_name + '\nNapišite nove podatke (ako ništa ne napišete podatak se ne menja)')
    while True:
        password = input(
            "Unesite lozinku (lozinka mora biti dugačka bar 6 karaktera, sadržati"
            " najmanje jednu cifru u sebi i | nije validan karakter za lozinku): ").strip()
        if password == "":
            password = one_user.password
            break
        good = check_password(password)
        if good:
            break
        kraj = input(
            'Lozinka ne zadovoljava neki od zahteva, unesite kraj ako želite da odustanete.\n').lower().strip()
        if kraj == 'kraj':
            return False
    one_user.password = password
    name = input('Unesite novo ime: ').replace("|", "").strip()
    if name == '':
        name = one_user.name
    one_user.name = name
    last_name = input("Unesite novo prezime: ").replace("|", "").strip()
    if last_name == '':
        last_name = one_user.last_name
    one_user.last_name = last_name

    delete_user(one_user.username, users)
    users.append(one_user)

    return True
