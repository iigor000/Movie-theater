from model import screening
from datetime import datetime, timedelta
from tabulate import tabulate


def get_all_screenings(rooms):
    screenings = []
    with open('./database/screenings.txt', 'r') as file:
        for line in file.readlines():
            line = line.split('|')
            days = eval(line[4])
            for room in rooms:
                if line[1] in room.code:
                    room_to_add = room
            one_screening = screening.Screening(line[0], room_to_add, line[2], line[3], days, line[5],
                                                eval(line[6]), eval(line[7]))
            screenings.append(one_screening)
    return screenings


def make_screening(screenings, rooms, movies):  # Funkcija radi po istom principu kao i za dodavanje filmova
    active_movies = []
    for one_movie in movies:
        if one_movie.active:
            active_movies.append(one_movie)
    movies = active_movies

    picked_movie = None
    picked_room = None

    # Kod se generise tako sto se doda jedan na kod poslednje projekcije
    # ili ako je ovo prva projekcija, pocetni kod je 1000
    if not screenings:
        code = 1000
    else:
        code = int(screenings[-1].code) + 1
    i = 0
    for movie in movies:  # Film i sobu prvo ispisujemo sa indexom i onda preko njega biramo
        if movie.active:
            i += 1
            print(str(i) + '. ' + movie.name)
    while True:
        try:
            i = eval(input('Unesite broj filma: ').strip())
        except ValueError:
            print("Nevalidan unos, pokušajte ponovo")
            continue
        try:
            picked_movie = movies[i - 1]
            break
        except IndexError:
            kraj = input('Film sa ovim brojem ne postoji, pokušajte ponovo ili napišite kraj ako'
                         ' želite da odustanete: ').strip().lower()
            if kraj == 'kraj':
                return False

    i = 0
    for room in rooms:
        i += 1
        print(str(i) + '. ' + room.name)
    while True:
        try:
            i = eval(input('Unesite broj sale u kojoj se projekcija održava: ').strip())
        except ValueError:
            print("Nevalidan unos, pokušajte ponovo")
            continue
        try:
            picked_room = rooms[i - 1]
            break
        except IndexError:
            kraj = input('Soba sa ovim brojem ne postoji, pokušajte ponovo ili napisšite kraj '
                         'ako želite da odustanete: ').strip().lower()
            if kraj == 'kraj':
                return False

    while True:
        start_time_str = input('Unesite vreme početka projekcije (u formatu xx:xx): ').strip().replace('|', '')
        try:
            start_time = datetime.strptime(start_time_str, '%H:%M')
            break
        except ValueError:
            kraj = input('Niste dobro uneli vreme, pokušajte ponovo ili napišite'
                         ' kraj ako želite da odustanete: ').strip().lower()
            if kraj == 'kraj':
                return False

    end_time = start_time + timedelta(minutes=int(picked_movie.duration))
    end_time_str = end_time.strftime("%H:%M")

    days = []
    while True:  # Dane unosimo kao brojeve radi lakseg unosa za korisnika
        day = input('Unesite dan u nedelji tokom kog se prikazuje film (dan unosite kao broj'
                    ' od 1 do 7, a kada žavrsite napisete kraj): ').strip().lower()
        if day == 'kraj':
            if len(days) > 0:
                break
            print('Film se mora prikazivati bar jednom nedeljno')
            continue
        try:
            days.append(str(int(day) - 1))
        except ValueError:
            print('Pogrešan unos za dan, pokusajte ponovo')

    while True:
        try:
            price = eval(input('Unesite cenu karte: '))
            break
        except ValueError:
            kraj = input('Uneli ste nevalidan broj, pokušajte ponovo ili napišite kraj'
                         ' ako želite da odustanete: ').strip().lower()
            if kraj == 'kraj':
                return False

    new_screening = screening.Screening(str(code), picked_room, start_time_str, end_time_str, str(days),
                                        picked_movie.name, price, True)
    screenings.append(new_screening)
    return True


def print_out_screenings(screenings):
    screenings_to_print = []
    for one_screening in screenings:  # Dane koji se cuvaju kao brojavi pretvaramo u odgovarajuce reci
        if one_screening.active:
            days = []

            if '0' in one_screening.day_array:
                days.append('Ponedeljak')
            if '1' in one_screening.day_array:
                days.append('Utorak')
            if '2' in one_screening.day_array:
                days.append('Sreda')
            if '3' in one_screening.day_array:
                days.append('Četvrtak')
            if '4' in one_screening.day_array:
                days.append('Petak')
            if '5' in one_screening.day_array:
                days.append('Subota')
            if '6' in one_screening.day_array:
                days.append('Nedelja')

            screenings_to_print.append([one_screening.code, one_screening.movie, one_screening.room.name,
                                        ','.join(days), one_screening.price, one_screening.start_time,
                                        one_screening.end_time])
    headers = ['Šifra', 'Naziv filma', 'Sala', 'Dani kojima se prikazuje', 'Cena karte', 'Vreme poČetka', 'Vreme kraja']
    print(tabulate(screenings_to_print, headers, tablefmt='pretty'))


def edit_screening(screenings, movies, rooms, screening_dates, tickets):
    active_movies = []
    for one_movie in movies:
        if one_movie.active:
            active_movies.append(one_movie)
    movies = active_movies
    need_to_delete = False  # Pratimo da li moramo da izbrisemo sve vezane termine projekcija

    selected_screening = None
    duration = None

    print_out_screenings(screenings)
    while True:
        do_break = False
        code = input('Unesite šifru projekcije koju želite da izmenite: ').strip()
        for one_screening in screenings:
            if one_screening.active:
                if one_screening.code == code:
                    selected_screening = one_screening
                    do_break = True
        if do_break:
            break
        kraj = input('Nismo našli projekciju sa tom šifrom, pokušajte ponovo'
                     ' ili napišite kraj ako želite da odustanete: ').strip().lower()
        if kraj == 'kraj':
            return False

    print_out_selected_screening = [selected_screening]
    print('Izabrana projekcija je:')
    print_out_screenings(print_out_selected_screening)
    print('Unesite nove podatke (ako ništa ne unesete podatak se ne menja)')

    i = 0
    for movie in movies:
        i += 1
        print(str(i) + '. ' + movie.name)
    while True:
        try:
            i = input('Unesite broj filma: ').strip()
            if i == '':
                for one_movie in movies:
                    if one_movie.name == selected_screening.movie:
                        duration = one_movie.duration
                break
            i = eval(i)

        except NameError:
            print("Nevalidan unos, pokušajte ponovo")
            continue
        try:
            selected_screening.movie = movies[i - 1].name
            duration = movies[i - 1].duration
            break
        except IndexError:
            kraj = input('Film sa ovim brojem ne postoji, pokušajte ponovo ili'
                         ' napišite kraj ako želite da odustanete: ').strip().lower()
            if kraj == 'kraj':
                return False

    i = 0
    for room in rooms:
        i += 1
        print(str(i) + '. ' + room.name)
    while True:
        try:
            i = input('Unesite broj sale u kojoj se projekcija održava: ').strip()
            if i == '':
                break
            i = eval(i)
        except NameError:
            print("Nevalidan unos, pokušajte ponovo")
            continue
        try:
            selected_screening.room = rooms[i - 1]
            break
        except IndexError:
            kraj = input(
                'Soba sa ovim brojem ne postoji, pokušajte ponovo ili '
                'napišite kraj ako želite da odustanete: ').strip().lower()
            if kraj == 'kraj':
                return False

    while True:
        start_time_str = input('Unesite vreme početka projekcije (u formatu xx:xx): ').strip().replace('|', '')
        if start_time_str == '':
            start_time = datetime.strptime(selected_screening.start_time, '%H:%M')
            break
        try:
            start_time = datetime.strptime(start_time_str, '%H:%M')
            selected_screening.start_time = start_time_str
            break
        except ValueError:
            kraj = input('Niste dobro uneli vreme, pokušajte ponovo ili '
                         'napišite kraj ako želite da odustanete: ').strip().lower()
            if kraj == 'kraj':
                return False

    end_time = start_time + timedelta(minutes=int(duration))
    end_time_str = end_time.strftime("%H:%M")
    selected_screening.end_time = end_time_str

    change_days = input('Da li želite da promenite dane u nedelji kada se film'
                        ' prikazuje, ako želite napišite da: ').strip().lower()
    if change_days == 'da':
        need_to_delete = True
        days = []
        while True:
            day = input(
                'Unesite dan u nedelji tokom kog se prikazuje film (dan unosite kao'
                ' broj od 1 do 7, a kada završite napišete kraj): ').strip().lower()
            if day == 'kraj':
                if len(days) > 0:
                    break
                print('Film se mora prikazivati bar jednom nedeljno')
                continue
            try:
                days.append(str(int(day) - 1))
            except ValueError:
                print('Pogrešan unos za dan, pokušajte ponovo')
        selected_screening.day_array = days

    while True:
        try:
            price = input('Unesite cenu karte: ')
            if price == '':
                break
            selected_screening.price = eval(price)
            break
        except ValueError:
            kraj = input(
                'Uneli ste nevalidan broj, pokušajte ponovo ili '
                'napišite kraj ako želite da odustanete: ').strip().lower()
            if kraj == 'kraj':
                return False
    if need_to_delete:
        for one_date in screening_dates:
            if selected_screening.code in one_date.code:
                one_date.active = False
        for one_ticket in tickets:
            if not one_ticket.sold:
                if selected_screening.code in one_ticket.screening_date.code:
                    tickets.remove(one_ticket)
        print('Morate ponovo generisati termine projekcija')

    return True


def delete_screening(screenings, screening_dates, tickets):
    print_out_screenings(screenings)

    selected_screening = None

    while True:
        do_break = False
        code = input('Unesite šifru projekcije koju želite da izmenite: ').strip()
        for one_screening in screenings:
            if one_screening.active:
                if one_screening.code == code:
                    selected_screening = one_screening
                    do_break = True
        if do_break:
            break
        kraj = input(
            'Nismo nasli projekciju sa tom šifrom, pokusšajte ponovo '
            'ili napišite kraj ako želite da odustanete: ').strip().lower()
        if kraj == 'kraj':
            return False

    print_out_selected_screening = [selected_screening]
    print('Izabrana projekcija je:')
    print_out_screenings(print_out_selected_screening)
    delete = input('Da li želite da izbrišete ovu projekciju, napisšite da ako zelite: ').strip().lower()
    if delete == 'da':
        selected_screening.active = False
        for one_date in screening_dates:
            if selected_screening.code in one_date.code:
                one_date.active = False
        for one_ticket in tickets:
            if not one_ticket.sold:
                if selected_screening.code in one_ticket.screening_date.code:
                    tickets.remove(one_ticket)
        return True
    return False


def save_screenings(screenings):
    screening_str = ''
    for one_screening in screenings:
        screening_str += (
            one_screening.code + '|' + one_screening.room.code + '|' + one_screening.start_time + '|' +
            one_screening.end_time + '|' + str(one_screening.day_array) + '|' + one_screening.movie + '|' +
            str(one_screening.price) + '|' + str(one_screening.active) + '\n'
        )
    with open('./database/screenings.txt', 'w') as file:
        file.write(screening_str)
