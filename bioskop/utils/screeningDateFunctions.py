from model import screeningDate
from datetime import datetime, timedelta
from tabulate import tabulate


def get_all_screening_dates(screenings):
    screening_dates = []
    with open('./database/screeningDates.txt', 'r') as file:
        for line in file.readlines():
            line = line.split('|')
            for screening in screenings:
                if line[0][:4] in screening.code:
                    screening_to_add = screening
            one_date = screeningDate.ScreeningDate(line[0], line[1].replace('\n', ''), screening_to_add, eval(line[2]))
            screening_dates.append(one_date)
    return screening_dates


def generate_dates(screening_dates, screenings):
    now = datetime.now()
    # Postavljamo trenutno vreme bez sata minuta i sekundi,
    # kako bi ga mogli porediti sa vremenom vec postojecih termina projekcija
    now = datetime(now.year, now.month, now.day)
    current_screening_date_codes = []
    # Ako ne postoji ni jedan termin projekcija, kazemo programu da generise sve
    # projekcije od sada i stavljamo pocetna slova na AA
    if not screening_dates:
        start = now
        letters = 'AA'
    else:
        # Pocetna slova za generaciju uzimamo kao prvu generaciju slova posle poslednjeg termina projekcije u listi
        letters = generate_letters(screening_dates[-1].code)
        start = datetime.strptime(screening_dates[-1].date, '%Y-%m-%d') + timedelta(days=1)
        # Proveravamo koji termin projekcije ima najnoviji datum, i pocinjemo generaciju od njega
        for one_date in screening_dates:
            if one_date.active:
                # Zapisujemo bitne podatke svih postojecih projekcija, za poredjenje,
                # u slucaju da je dodata nova projekcija ciji se termini trebaju generisati
                current_screening_date_codes.append(one_date.screening.code + one_date.date +
                                                    one_date.screening.start_time)
                date = datetime.strptime(one_date.date, '%Y-%m-%d')
                if date > start:
                    start = date
    # Kraj generacije je dve nedelje od danasnjeg dana plus jedan dan, kako vi se zapravo generisalo 14 dana
    end = now + timedelta(days=20)

    while True:  # Petlja za generisanje novo dodatih projekcija
        # Ako dodjemo do vremena za koje trebaju sve funkcije da se generisu, prebacujemo se na tu petlju
        if now == start:
            break
        day = now.weekday()
        for one_screening in screenings:
            if one_screening.active:
                # Za svaku projekciju proveravamo da li je treba da se prikazuje datog dana u nedelji
                if str(day) in one_screening.day_array:
                    # Pravimo string za upisivanje u termin projekcije i poredjenje sa vec postojecim projekcijama
                    date = now.strftime('%Y-%m-%d')
                    # Ako se podaci ne poklapaju, to znaci da postoji projekcija za
                    # koju nisu generisani termini, to jest nova dodata projekcija
                    if one_screening.code + date + one_screening.start_time not in current_screening_date_codes:
                        code = one_screening.code + letters
                        date_to_add = screeningDate.ScreeningDate(code, date, one_screening, True)
                        screening_dates.append(date_to_add)
                        # Generisemo sledeca slova za termin projekcije
                        letters = generate_letters(code)
        # Prebacujemo generaciju na seldeci dan
        now += timedelta(days=1)
    # Ako je pocetak jednak kraju ili jedan dan ispred kraja, znaci da te termine ne treba generisati
    if start == end:
        return True
    # Petlja za generisanje projekcija posle 'starta', radi po istom principu
    # kao i prethodna, samo sto ne proverava da li je projekcija vec dodata
    while True:
        if start == end:
            break
        day = start.weekday()
        for one_screening in screenings:
            if one_screening.active:
                if str(day) in one_screening.day_array:
                    date = start.strftime('%Y-%m-%d')
                    code = one_screening.code + letters
                    date_to_add = screeningDate.ScreeningDate(code, date, one_screening, True)
                    screening_dates.append(date_to_add)
                    letters = generate_letters(code)
        start += timedelta(days=1)
    return True


# Funkcija generise slova, tako sto dodaje 1 njihovom ascii zapisu, proveravamo da
# li smo stigli na drugom do Z i ako jesmo prebacujemo prvo ili ako smo na prvom stigli da Z krecemo iz pocetka
def generate_letters(last_code):
    first_letter = ord(last_code[4])
    last_letter = ord(last_code[5])

    if last_letter < ord('Z'):
        last_letter += 1
    else:
        if first_letter == ord('Z'):
            return 'AA'
        else:
            first_letter += 1
            last_letter = ord('A')

    return chr(first_letter) + chr(last_letter)


# Ispisujemo po istom principu kao i filmove
def print_out_dates(screening_dates):
    tabulate_dates = []
    for one_date in screening_dates:
        if one_date.active:
            tabulate_dates.append([one_date.code, one_date.screening.movie, one_date.screening.room.name,
                                   one_date.date, one_date.screening.start_time, one_date.screening.end_time])
    headers = ['Šifra', 'Naziv filma', 'Sala', 'Datum projekcije', 'Vreme početka', 'Vreme kraja']
    print(tabulate(tabulate_dates, headers=headers, tablefmt='pretty'))


# Izbacujemo termine koji su u proslosti
def get_current_dates(screening_dates):
    now = datetime.now()
    new_dates = []
    for one_date in screening_dates:
        if one_date.active:
            hours = one_date.screening.start_time.split(':')
            date_obj = (datetime.strptime(one_date.date, '%Y-%m-%d') +
                        timedelta(hours=int(hours[0]), minutes=int(hours[1])))
            if date_obj >= now:
                new_dates.append(one_date)
    return new_dates


def print_current_dates(screening_dates):
    current_dates = get_current_dates(screening_dates)
    print_out_dates(current_dates)


def search_screening_dates(screening_dates):
    filtered_dates = []
    screening_dates = get_current_dates(screening_dates)
    while True:
        criteria = input(
            'Izaberite kriterijum po kojem želite da pretražite projekcije:\n1.Naziv filma'
            '\n2.Sala\n3.Datum\n4.Vreme početka\n5.Vreme kraja\n0.Odustanite\n').strip()
        if criteria == '1':
            value = input('Unesite naziv filma: ').strip().lower()
            for one_screening_date in screening_dates:
                if value in one_screening_date.screening.movie.lower():
                    filtered_dates.append(one_screening_date)
        elif criteria == '2':
            value = input('Unesite naziv sale: ').strip().lower()
            for one_screening_date in screening_dates:
                if value in one_screening_date.screening.room.name.lower():
                    filtered_dates.append(one_screening_date)
        elif criteria == '3':
            while True:
                value = input('Unesite datum (u formatu YYYY-mm-dd): ').strip().lower()
                try:
                    date = datetime.strptime(value, '%Y-%m-%d')
                except ValueError:
                    kraj = input('Niste dobro uneli datum, pokušajte ponovo ili napišite kraj '
                                 'ako želite da odustanete').strip().lower()
                    if kraj == 'kraj':
                        return False
                    continue
                for one_screening_date in screening_dates:
                    date_of_screening_date = datetime.strptime(one_screening_date.date, '%Y-%m-%d')
                    if date == date_of_screening_date:
                        filtered_dates.append(one_screening_date)
                break
        elif criteria == '4':
            while True:
                value = input('Unesite vreme početka (u formatu xx:xx): ').strip().lower()
                try:
                    datetime.strptime(value, '%H:%M')
                except ValueError:
                    kraj = input('Niste dobro uneli vreme, pokušajte ponovo ili napišite'
                                 ' kraj ako želite da odustanete').strip().lower()
                    if kraj == 'kraj':
                        return False
                    continue
                for one_screening_date in screening_dates:
                    if value in one_screening_date.screening.start_time.lower():
                        filtered_dates.append(one_screening_date)
                break
        elif criteria == '5':
            while True:
                value = input('Unesite vreme kraja (u formatu xx:xx): ').strip().lower()
                try:
                    datetime.strptime(value, '%H:%M')
                except ValueError:
                    kraj = input(
                        'Niste dobro uneli vreme, pokušajte ponovo ili napišite'
                        ' kraj ako želite da odustanete').strip().lower()
                    if kraj == 'kraj':
                        return False
                    continue
                for one_screening_date in screening_dates:
                    if value in one_screening_date.screening.end_time.lower():
                        filtered_dates.append(one_screening_date)
                break
        elif criteria == '0':
            return
        else:
            print('Nevalidan unos')
        kraj = input("Da li želite da pretražite preko još kriterijuma (unesite da ako želite): ").strip().lower()
        if kraj != 'da':
            break
        screening_dates = filtered_dates
        filtered_dates = []
    print_out_dates(filtered_dates)
    return True


def save_screening_dates(screening_dates):
    screening_date_str = ''
    for one_screening_date in screening_dates:
        screening_date_str += (one_screening_date.code + '|' + one_screening_date.date + '|' +
                               str(one_screening_date.active) + '\n')
    with open('./database/screeningDates.txt', 'w') as file:
        file.write(screening_date_str)
