from model import ticket
from utils import screeningDateFunctions, movieFunctions
from datetime import datetime, timedelta
from tabulate import tabulate

from utils import reportFunctions


def get_all_tickets(screening_dates):
    tickets = []
    with open('./database/tickets.txt', 'r') as file:
        for line in file.readlines():
            line = line.split('|')
            for screening_date in screening_dates:
                if line[1] in screening_date.code:
                    screening_date_to_add = screening_date
            is_sold = line[4].replace('\n', '')
            if line[4] == 'False':
                is_sold = False
            one_ticket = ticket.Ticket(line[0], screening_date_to_add, line[2], line[3], is_sold, eval(line[5]))
            tickets.append(one_ticket)
    return tickets


# Funkcija ispisuje sedista i vraca podatke potrebne za proveravanje zauzetosti sedista
def print_out_seats(tickets, date):
    taken_seats = []
    for one_ticket in tickets:
        if one_ticket.screening_date == date:
            taken_seats.append(one_ticket.seat)

    ticket_row = date.screening.room.row
    tabulate_tickets = []
    row = []
    for i in range(date.screening.room.row_number):
        for j in ticket_row:
            seat = j + str(i)
            if seat in taken_seats:
                row.append('XX')
            else:
                row.append(seat)
        tabulate_tickets.append(row)
        row = []

    print(tabulate(tabulate_tickets, tablefmt='pretty'))
    return taken_seats, ticket_row


# Uz potrebne liste prosledjujemo i podatak ulogovanog korisnika,
# da li je karta prodata i korisnike koji su clanovi kluba lojalnosti
def reserve_ticket(tickets, screening_dates, logged_in_user, users, sold, loyalty_club_members):
    while True:
        screeningDateFunctions.print_current_dates(screening_dates)
        selected_date = None
        ticket_to_add = None
        while True:
            if sold:
                code = input('Unesite šifru termina projekcije karte koju želite da prodate: ').strip().upper()
            else:
                code = input('Unesite šifru termina projekcije koju želite da rezervišete: ').strip().upper()
            for screening_date in screening_dates:
                if code == screening_date.code:
                    selected_date = screening_date
                    break
            if selected_date is not None:
                break
            kraj = input(
                'Nije pronadjen termin sa tom šifrom, pokušajte ponovo ili napišite kraj'
                ' ako želite da odustanete: ').lower().strip()
            if kraj == 'kraj':
                return False

        taken_seats, ticket_row = print_out_seats(tickets, selected_date)

        price = selected_date.screening.price
        date = datetime.strptime(selected_date.date, '%Y-%m-%d')
        weekday = date.weekday()  # U zavisnosti od toga koji je dan projekcije podesavamo cenu
        if weekday == 1:
            price -= 50
        elif weekday == 5 or weekday == 6:
            price += 50

        while True:
            selected_seat = input('Unesite sedište: ').strip().upper()
            if selected_seat in taken_seats:
                kraj = input(
                    'Sedište je zauzeto, probajte ponovo ili napišite kraj do odustanete: ').lower().strip()
                if kraj == 'kraj':
                    return False
                continue
                # Proveravamo da li je unos sedista validan
            elif len(selected_seat) >= 2 and selected_seat[0] in ticket_row:
                try:
                    number = int(selected_seat[1:])
                    if number < selected_date.screening.room.row_number:
                        break
                except ValueError:
                    pass
            kraj = input('Nevalidan unos za sedište, probajte ponovo ili napišite kraj do odustanete: ').lower().strip()
            if kraj == 'kraj':
                return False

        date = datetime.now().strftime('%Y-%m-%d')
        if logged_in_user.access_level == '0':
            ticket_to_add = ticket.Ticket(logged_in_user.username, selected_date, selected_seat, date, sold, price)
        else:
            # Ako je korisnik registrovan u karti se zapisuje njegovo korisnicko
            # ime, a ako nije njegovo ime i prezime se unosi
            da_ne = input('Da li je kupac registrovan, ako jeste upišite da: ').strip().lower()
            if da_ne == 'da':
                while True:
                    do_break = False
                    username = input('Unesite korisničko ime: ')
                    for one_user in users:
                        if one_user.username == username and one_user.access_level == '0':
                            do_break = True
                            if sold is False:
                                ticket_to_add = ticket.Ticket(username, selected_date, selected_seat, date, sold, price)
                            else:
                                # Ako je korisnik u klubu lojalnosti, cena se smanjuje za 10%
                                if username in loyalty_club_members:
                                    price = (price * 90) / 100
                                ticket_to_add = ticket.Ticket(username, selected_date, selected_seat, date,
                                                              logged_in_user.username, price)
                    if do_break:
                        break
                    kraj = input('Nismo nasli korisnika sa ovim imenom, pokušajte'
                                 ' ponovo ili napišite kraj ako želite da odustanete: ').strip().lower()
                    if kraj == 'kraj':
                        return False
            else:
                while True:
                    name = input('Unesite ime: ').strip().replace('|', '').replace('&', '')
                    if name != '':
                        break
                    print('Ime ne sme biti prazno, napišite kraj ako želite da odustanete: ')
                while True:
                    last_name = input('Unesite prezime: ').strip().replace('|', '').replace('&', '')
                    if last_name != '':
                        break
                    print('Prezime ne sme biti prazno, napišite kraj ako želite da odustanete: ')
                if sold is False:
                    ticket_to_add = ticket.Ticket(name + '&' + last_name, selected_date, selected_seat,
                                                  date, sold, price)
                else:
                    ticket_to_add = ticket.Ticket(name + '&' + last_name, selected_date, selected_seat, date,
                                                  logged_in_user.username, price)
        tickets.append(ticket_to_add)
        if sold:
            print('Karta je uspesno prodata')
            kraj = input('Da li želite da prodate još karata, unesite da ako želite: ').strip().lower()
            if kraj != 'da':
                break
        else:
            print('Karta je uspesno rezervisana')
            kraj = input('Da li želite da rezervišete još karata, unesite da ako želite: ').strip().lower()
            if kraj != 'da':
                break

    return True


# Prodavac bira rezervisanu kartu da proda
def sell_reserved_ticket(tickets, users, logged_in_user, loyalty_club_members):
    seller_print_out_reservations(tickets, users)

    while True:
        while True:
            code = input('Unesite šifru projekcije rezervacije karte koju želite da prodate: ').strip().upper()
            do_break = False
            for one_ticket in tickets:
                if code == one_ticket.screening_date.code:
                    do_break = True
            if do_break:
                break
            kraj = input(
                'Nismo nasli projekciju sa tom šifrom, pokušajte ponovo ili napisite kraj ako'
                ' želite da odustanete: ').lower().strip()
            if kraj == 'kraj':
                return False

        while True:
            seat = input('Unesite sedište projekcije karte koju želite da prodate: ').strip().upper()
            do_break = False
            for one_ticket in tickets:
                if seat == one_ticket.seat:
                    do_break = True
            if do_break:
                break
            kraj = input(
                'Nismo našli projekciju sa tim sedištem, pokušajte ponovo ili napišite kraj ako'
                ' želite da odustanete: ').lower().strip()
            if kraj == 'kraj':
                return False

        for one_ticket in tickets:
            if one_ticket.seat == seat and one_ticket.screening_date.code == code:
                if one_ticket.username in loyalty_club_members:
                    one_ticket.price = (one_ticket.price * 90) / 100
                one_ticket.sold = logged_in_user.username
                print('Karta je uspešno prodata')
        kraj = input('Da li želite da nastavise (napišite da ako zelite): ').strip().lower()
        if kraj != 'da':
            break
    return True


# Funkcija ispisuje podatke koji su relevantni za prodavca
def seller_print_out_tickets(tickets, users):
    tabulate_tickets = []
    for one_ticket in tickets:
        if not one_ticket.sold:
            status = 'Rezervisana'
        else:
            status = 'Prodata'
        if '&' in one_ticket.username:
            name = one_ticket.username.split('&')
            tabulate_tickets.append(
                [one_ticket.screening_date.code, name[0] + ' ' + name[1], one_ticket.screening_date.screening.movie,
                 one_ticket.screening_date.date,
                 one_ticket.screening_date.screening.start_time, one_ticket.screening_date.screening.end_time,
                 one_ticket.seat, status, str(one_ticket.price)])
        else:
            name = None
            last_name = None
            for one_user in users:
                if one_ticket.username == one_user.username:
                    name = one_user.name
                    last_name = one_user.last_name
            tabulate_tickets.append(
                [one_ticket.screening_date.code, name + ' ' + last_name, one_ticket.screening_date.screening.movie,
                 one_ticket.screening_date.date,
                 one_ticket.screening_date.screening.start_time, one_ticket.screening_date.screening.end_time,
                 one_ticket.seat, status, str(one_ticket.price)])
    headers = ['Šifra projekcije', 'Ime i prezime kupovca', 'Naziv filma', 'Datum projekcije', 'Početak projekcije',
               'Kraj projekcije',
               'Sedište', 'Status karte', 'Cena karte']
    string = tabulate(tabulate_tickets, headers=headers, tablefmt='pretty')
    print(string)
    return string  # Funkcija vraca string ispisa, kako bi mogao da se upise u fajl kod izvestaja


def get_by_username(tickets, logged_in_user):  # Funkcija uzima sve karte za datog ulogovanog korisnika
    user_tickets = []
    for one_ticket in tickets:
        if logged_in_user.username == one_ticket.username:
            user_tickets.append(one_ticket)
    print_out_tickets(user_tickets)


def print_out_tickets(tickets):  # Funkcija ispisuje podatke koji su relevantni za obicnog korisnika
    tabulate_tickets = []
    for one_ticket in tickets:
        tabulate_tickets.append(
            [one_ticket.screening_date.code, one_ticket.screening_date.screening.movie, one_ticket.screening_date.date,
             one_ticket.screening_date.screening.start_time, one_ticket.screening_date.screening.end_time,
             one_ticket.seat, one_ticket.price])
    headers = ['Šifra projekcije', 'Naziv filma', 'Datum projekcije', 'Početak projekcije', 'Kraj projekcije',
               'Sedište', 'Cena karte']
    print(tabulate(tabulate_tickets, headers=headers, tablefmt='pretty'))


def seller_edit_ticket(tickets, users, screening_dates):

    while True:
        seller_print_out_tickets(tickets, users)

        while True:
            code = input('Unesite šifru projekcije rezervacije koju želite da izmenite: ').strip().upper()
            do_break = False
            for one_ticket in tickets:
                if code == one_ticket.screening_date.code:
                    do_break = True
            if do_break:
                break
            kraj = (input(
                'Nismo nasli projekciju sa tom šifrom, pokušajte ponovo ili napišite kraj ako želite da odustanete: ').
                    lower().strip())
            if kraj == 'kraj':
                return False

        while True:
            seat = input('Unesite sedište projekcije koju želite da izmenite: ').strip().upper()
            do_break = False
            for one_ticket in tickets:
                if seat == one_ticket.seat:
                    do_break = True
            if do_break:
                break
            kraj = input(
                'Nismo nasli to sedište, pokušajte ponovo ili napišite kraj ako želite da odustanete: ').lower().strip()
            if kraj == 'kraj':
                return False

        selected_ticket = None
        for one_ticket in tickets:
            if one_ticket.seat == seat and one_ticket.screening_date.code == code:
                selected_ticket = one_ticket
                tickets.remove(one_ticket)

        while True:
            name = input('Unesite ime: ').strip().lower()
            do_break = False
            if '&' in selected_ticket.username:
                user_name = selected_ticket.username.lower().split('&')
                if name in user_name[0]:
                    break
            else:
                for one_user in users:
                    if selected_ticket.username == one_user.username:
                        if name in one_user.name.lower():
                            do_break = True
            if do_break:
                break
            kraj = (input(
                'Nismo našli kupovca sa tim imenom, pokušajte ponovo ili napišite kraj ako želite da odustanete: ').
                    lower().strip())
            if kraj == 'kraj':
                return False

        while True:
            last_name = input('Unesite prezime: ').strip().lower()
            do_break = False
            if '&' in selected_ticket.username:
                user_last_name = selected_ticket.username.lower().split('&')
                if last_name in user_last_name[1]:
                    do_break = True
            else:
                for one_user in users:
                    if selected_ticket.username == one_user.username:
                        if last_name in one_user.last_name.lower():
                            do_break = True
            if do_break:
                break
            kraj = (input(
                'Nismo našli kupovca sa tim prezimenom, pokušajte ponovo ili napišite kraj ako želite da odustanete: ').
                    lower().strip())
            if kraj == 'kraj':
                return False

        print('Trenutni termin projekcije je: ')
        date_to_print = [selected_ticket.screening_date]
        screeningDateFunctions.print_out_dates(date_to_print)
        change_date = input('Da li želite da promenite termin projekcije, ako želite napišite da: ').lower().strip()
        if change_date == 'da':
            screeningDateFunctions.print_current_dates(screening_dates)
            do_break = False
            while True:
                code = input('Unesite šifru projekcije koju želite da stavite: ').upper()
                for one_date in screening_dates:
                    if code in one_date.code:
                        selected_ticket.screening_date = one_date
                        do_break = True
                if do_break:
                    break
                kraj = (
                    'Nismo našli termin projekcije sa tom šifrom, pokušajte ponovo ili napišite '
                    'kraj ako želite da odustanete: ').strip().lower()
                if kraj == 'kraj':
                    return False

        if change_date != 'da':
            change = input('Da li želite da promenite sedište, ako želite napišite da: ').lower().strip()
        else:
            change = 'da'
        if change == 'da':
            taken_seats, ticket_row = print_out_seats(tickets, selected_ticket.screening_date)
            while True:
                selected_seat = input('Unesite sedište: ').strip().upper()
                if selected_seat in taken_seats:
                    print('Ovo sedište je zauzeto')
                    continue
                elif len(selected_seat) >= 2 and selected_seat[0] in ticket_row and int(
                        selected_seat[1]) <= selected_ticket.screening_date.screening.room.row_number:
                    selected_ticket.seat = selected_seat
                    break
                kraj = input(
                    'Nevalidan unos za sedište, probajte ponovo ili napišite kraj do odustanete: ').lower().strip()
                if kraj == 'kraj':
                    return False

        change = input('Da li želite da promenite ime kupovca, ako želite napišite da: ').lower().strip()
        if change == 'da':
            if '&' in selected_ticket.username:
                while True:
                    name = input('Unesite novo ime za kupovca: ').strip().strip().replace('|', '').replace('&', '')
                    if name != '':
                        last_name = selected_ticket.username.split('&')
                        selected_ticket.username = name + '&' + last_name[1]
                    kraj = input(
                        'Ime ne sme biti prazno, pokušajte ponovo ili napišite kraj kako bi odustali: ').strip().lower()
                    if kraj == 'kraj':
                        return False
            else:
                print('Ulogovan korisnik je kupio ovu kartu, ne možete da promenite njegovo ime')

        change = input('Da li želite da promenite prezime kupovca, ako želite napisite da: ').lower().strip()
        if change == 'da':
            if '&' in selected_ticket.username:
                while True:
                    last_name = input('Unesite novo prezime za kupovca: ').strip().replace('|', '').replace('&', '')
                    if name != '':
                        name = selected_ticket.username.split('&')
                        selected_ticket.username = name[0] + '&' + last_name
                    kraj = (input(
                        'Prezime ne sme biti prazno, pokušajte ponovo ili napišite kraj kako bi odustali: ').strip().
                            lower())
                    if kraj == 'kraj':
                        return False
            else:
                print('Ulogovan korisnik je kupio ovu kartu, ne možete da promenite njegovo prezime')

        tickets.append(selected_ticket)

        kraj = input('Da li želite da nastavise (napišite da ako zelite): ').strip().lower()
        if kraj != 'da':
            break
    return True


def get_sold_tickets_by_date(tickets, users, reports):
    while True:
        date = input('Unesite datum (u formatu YYYY-mm-dd): ')
        try:
            date_to_search = datetime.strptime(date, '%Y-%m-%d')
            break
        except ValueError:
            print('Niste uneli validan datum, pokušajte ponovo ili unesite kraj ako želite da odustanete')
    tickets_to_print = []
    for one_ticket in tickets:
        date_of_ticket = datetime.strptime(one_ticket.date_of_sale, '%Y-%m-%d')
        if date_of_ticket == date_to_search and one_ticket.sold:
            tickets_to_print.append(one_ticket)

    string = seller_print_out_tickets(tickets_to_print, users)
    header = 'Karte prodate ' + date
    reportFunctions.write_report(reports, string, header)
    return True


def get_sold_tickets_by_screening_date(tickets, users, screening_dates, reports):
    screeningDateFunctions.print_out_dates(screening_dates)
    selected_date = None
    while True:
        code = input('Unesite šifru termina projekcije koju želite da rezervišete: ').strip().upper()
        for screening_date in screening_dates:
            if code == screening_date.code:
                selected_date = screening_date
                break
        if selected_date:
            break
        kraj = (input(
            'Nije pronadjen termin sa tom šifrom, pokušajte ponovo ili napišite kraj ako želite da odustanete: ').
                lower().strip())
        if kraj == 'kraj':
            return False

    tickets_to_print = []
    for one_ticket in tickets:
        if one_ticket.screening_date == selected_date and one_ticket.sold:
            tickets_to_print.append(one_ticket)
    string = seller_print_out_tickets(tickets_to_print, users)
    header = 'Karte prodate za projekciju ' + selected_date.code
    reportFunctions.write_report(reports, string, header)
    return True


def get_sold_tickets_by_date_and_seller(tickets, users, reports):
    while True:
        do_break = False
        username = input('Unesite korisničko ime prodavca: ').strip()
        for one_user in users:
            if one_user.username == username and one_user.access_level == '1':
                do_break = True
        if do_break:
            break
        kraj = input(
            'Nismo pronašli prodavca sa tim korisničkim imenom, pokusajte ponovo ili '
            'napišite kraj ako želite da odustanete: ').strip().lower()
        if kraj == 'kraj':
            return False
    while True:
        date = input('Unesite datum (u formatu YYYY-mm-dd): ')
        try:
            date_to_search = datetime.strptime(date, '%Y-%m-%d')
            break
        except ValueError:
            kraj = (input(
                'Niste uneli validan datum, pokušajte ponovo ili unesite kraj ako želite da odustanete: ').lower().
                    strip())
            if kraj == 'kraj':
                return False
    tickets_to_print = []
    for one_ticket in tickets:
        date_of_ticket = datetime.strptime(one_ticket.date_of_sale, '%Y-%m-%d')
        if date_of_ticket == date_to_search and one_ticket.sold == username:
            tickets_to_print.append(one_ticket)
    string = seller_print_out_tickets(tickets_to_print, users)
    header = 'Karte prodate od korisnika ' + username + 'datuma ' + date
    reportFunctions.write_report(reports, string, header)
    return True


def get_sold_tickets_by_day_of_week(tickets, reports):
    while True:
        day = input('Unesite dan u nedelji: ').strip().lower()
        if day == 'ponedeljak':
            day_num = 0
            break
        elif day == 'utorak':
            day_num = 1
            break
        elif day == 'sreda':
            day_num = 2
            break
        elif day == 'četvrtak':
            day_num = 3
            break
        elif day == 'petak':
            day_num = 4
            break
        elif day == 'subota':
            day_num = 5
            break
        elif day == 'nedelja':
            day_num = 6
            break
        else:
            kraj = input(
                'Nevalidan unos za dan, pokušajte ponovo ili napišite kraj ako želite da odustanete: ').strip().lower()
            if kraj == 'kraj':
                return False
    price = 0
    counter = 0
    for one_ticket in tickets:
        date = datetime.strptime(one_ticket.date_of_sale, '%Y-%m-%d')
        weekday = date.weekday()
        if day_num == weekday and one_ticket.sold:
            price += one_ticket.price
            counter += 1
    tabulate_data = [[price, counter]]
    headers = ['Ukupna cena', 'Ukupan broj prodatih karata']
    string = tabulate(tabulate_data, headers, tablefmt='pretty')
    print(string)
    header = 'Karte prodate na dan ' + day
    reportFunctions.write_report(reports, string, header)
    return True


def get_sold_tickets_by_day_of_week_and_screening_date(tickets, screening_dates, reports):
    screeningDateFunctions.print_current_dates(screening_dates)
    selected_date = None
    while True:
        code = input('Unesite šifru termina projekcije koju želite da rezervisete: ').strip().upper()
        for screening_date in screening_dates:
            if code == screening_date.code:
                selected_date = screening_date
                break
        if selected_date is not None:
            break
        kraj = (input(
            'Nije pronadjen termin sa tom šifrom, pokušajte ponovo ili napišite kraj ako želite da odustanete: ').
                lower().strip())
        if kraj == 'kraj':
            return False
    while True:
        day = input('Unesite dan u nedelji: ').strip().lower()
        if day == 'ponedeljak':
            day_num = 0
            break
        elif day == 'utorak':
            day_num = 1
            break
        elif day == 'sreda':
            day_num = 2
            break
        elif day == 'četvrtak':
            day_num = 3
            break
        elif day == 'petak':
            day_num = 4
            break
        elif day == 'subota':
            day_num = 5
            break
        elif day == 'nedelja':
            day_num = 6
            break
        else:
            kraj = input(
                'Nevalidan unos za dan, pokušajte ponovo ili napišite kraj ako želite da odustanete: ').strip().lower()
            if kraj == 'kraj':
                return False
    price = 0
    counter = 0
    for one_ticket in tickets:
        date = datetime.strptime(one_ticket.screening_date.date, '%Y-%m-%d')
        weekday = date.weekday()
        if day_num == weekday and one_ticket.screening_date == selected_date and one_ticket.sold:
            price += one_ticket.price
            counter += 1
    tabulate_data = [[price, counter]]
    headers = ['Ukupna cena', 'Ukupan broj prodatih karata']
    string = tabulate(tabulate_data, headers, tablefmt='pretty')
    print(string)
    header = 'Karte prodate dana ' + day + ' za termin projekcije ' + selected_date.code
    reportFunctions.write_report(reports, string, header)
    return True


def get_sold_tickets_by_movie(tickets, movies, reports):
    movieFunctions.print_out_movies(movies)
    selected_movie = None
    while True:
        do_break = False
        movie_to_search = input('Izaberite film: ').strip().lower()
        for one_movie in movies:
            if one_movie.active:
                if movie_to_search == one_movie.name.lower():
                    selected_movie = one_movie
                    do_break = True
        if do_break:
            break
        kraj = input('Nismo našli taj film, unesite kraj ako želite da odustanete: ').strip().lower()
        if kraj == 'kraj':
            return

    price = 0
    for one_ticket in tickets:
        if one_ticket.screening_date.screening.movie.lower() == selected_movie.name.lower() and one_ticket.sold:
            price += one_ticket.price
    tabulate_data = [[price]]
    headers = ['Ukupna cena']
    string = tabulate(tabulate_data, headers, tablefmt='pretty')
    print(string)
    header = 'Karte prodate za film ' + selected_movie.name
    reportFunctions.write_report(reports, string, header)
    return True


def get_sold_tickets_by_day_of_week_and_seller(tickets, users, reports):
    while True:
        day = input('Unesite dan u nedelji: ').strip().lower()
        if day == 'ponedeljak':
            day_num = 0
            break
        elif day == 'utorak':
            day_num = 1
            break
        elif day == 'sreda':
            day_num = 2
            break
        elif day == 'četvrtak':
            day_num = 3
            break
        elif day == 'petak':
            day_num = 4
            break
        elif day == 'subota':
            day_num = 5
            break
        elif day == 'nedelja':
            day_num = 6
            break
        else:
            kraj = input(
                'Nevalidan unos za dan, pokušajte ponovo ili napišite kraj ako želite da odustanete: ').strip().lower()
            if kraj == 'kraj':
                return False

    while True:
        do_break = False
        username = input('Unesite korisničko ime prodavca: ').strip()
        for one_user in users:
            if one_user.username == username and one_user.access_level == '1':
                do_break = True
        if do_break:
            break
        kraj = input(
            'Nismo pronasli prodavca sa tim korisničkim imenom, pokušajte ponovo ili napišite '
            'kraj ako želite da odustanete: ').strip().lower()
        if kraj == 'kraj':
            return False

    price = 0
    counter = 0
    for one_ticket in tickets:
        date = datetime.strptime(one_ticket.date_of_sale, '%Y-%m-%d')
        weekday = date.weekday()
        if day_num == weekday and one_ticket.sold == username:
            price += one_ticket.price
            counter += 1
    tabulate_data = [[price, counter]]
    headers = ['Ukupna cena', 'Ukupan broj prodatih karata']
    string = tabulate(tabulate_data, headers, tablefmt='pretty')
    print(string)
    header = 'Karte prodate za dan ' + day + ' za prodavca ' + username
    reportFunctions.write_report(reports, string, header)
    return True


def get_sold_tickets_by_seller(tickets, users, reports):
    while True:
        do_break = False
        username = input('Unesite korisničko ime prodavca: ').strip()
        for one_user in users:
            if one_user.username == username and one_user.access_level == '1':
                do_break = True
        if do_break:
            break
        kraj = input(
            'Nismo pronašli prodavca sa tim korisničkim imenom, pokušajte ponovo ili napišite '
            'kraj ako želite da odustanete: ').strip().lower()
        if kraj == 'kraj':
            return False

    now = datetime.now()
    time_to_compare = now - timedelta(days=30)
    price = 0
    counter = 0
    for one_ticket in tickets:
        if one_ticket.sold == username:
            date = datetime.strptime(one_ticket.screening_date.date, '%Y-%m-%d')
            if date > time_to_compare:
                price += one_ticket.price
                counter += 1
    tabulate_data = [[price, counter]]
    headers = ['Ukupna cena', 'Ukupan broj prodatih karata']
    string = tabulate(tabulate_data, headers, tablefmt='pretty')
    print(string)
    header = 'Karte prodate za korisnika ' + username
    reportFunctions.write_report(reports, string, header)
    return True


def automatic_cancel_reservations(tickets):  # Funkcija brise i rezervacije ciji su termini prosli
    time_to_delete = datetime.now() + timedelta(
        minutes=30)  # Stavljamo vreme pre kog se svaka rezervacija ponistava na 30 minuta od sad
    tickets_to_remove = []
    for one_ticket in tickets:
        if not one_ticket.sold:
            hours = one_ticket.screening_date.screening.start_time.split(':')
            date_of_ticket = datetime.strptime(one_ticket.screening_date.date, '%Y-%m-%d') + timedelta(
                hours=int(hours[0]), minutes=int(hours[1]))
            if date_of_ticket <= time_to_delete:
                tickets_to_remove.append(one_ticket)
    for one_ticket in tickets_to_remove:
        tickets.remove(one_ticket)
    print('\nRezervacije su otkazane')


def seller_print_out_reservations(tickets,
                                  users):  # Funkcija ispisuje rezervacije sa podacima koji su relevantni za prodavca
    tabulate_tickets = []
    for one_ticket in tickets:
        if not one_ticket.sold:
            if '&' in one_ticket.username:
                name = one_ticket.username.split('&')
                tabulate_tickets.append(
                    [one_ticket.screening_date.code, name[0] + ' ' + name[1], one_ticket.screening_date.screening.movie,
                     one_ticket.screening_date.date,
                     one_ticket.screening_date.screening.start_time, one_ticket.screening_date.screening.end_time,
                     one_ticket.seat, one_ticket.price])
            else:
                name = None
                last_name = None
                for one_user in users:
                    if one_ticket.username == one_user.username:
                        name = one_user.name
                        last_name = one_user.last_name
                tabulate_tickets.append(
                    [one_ticket.screening_date.code, name + ' ' + last_name, one_ticket.screening_date.screening.movie,
                     one_ticket.screening_date.date,
                     one_ticket.screening_date.screening.start_time, one_ticket.screening_date.screening.end_time,
                     one_ticket.seat, one_ticket.price])
    headers = ['Šifra projekcije', 'Ime i prezime kupovca', 'Naziv filma', 'Datum projekcije', 'Početak projekcije',
               'Kraj projekcije',
               'Sedište', 'Status karte', 'Cena karte']
    print(tabulate(tabulate_tickets, headers=headers, tablefmt='pretty'))


def search_tickets(tickets, users):
    filtered_tickets = []
    while True:
        criteria = input(
            '\nIzaberite kriterijum po kojem želite da pretrazite karte:\n1.Šifra projekcije\n2.Ime kupca\n'
            '3.Prezime kupca\n4.Datum projekcije\n5.Vreme početka projekcije\n'
            '6.Vreme kraja projekcije\n7.Status karte\n0.Odustanite\n').strip()
        if criteria == '1':
            value = input('Unesite šifru: ').strip().lower()
            for one_ticket in tickets:
                if value in one_ticket.screening_date.code.lower():
                    filtered_tickets.append(one_ticket)
        elif criteria == '2':
            value = input('Unesite ime: ').strip().lower()
            for one_ticket in tickets:
                if '&' in one_ticket.username:
                    name = one_ticket.username.lower().split('&')
                    if value in name[0]:
                        filtered_tickets.append(one_ticket)
                else:
                    for one_user in users:
                        if value in one_user.name.lower():
                            filtered_tickets.append(one_ticket)
        elif criteria == '3':
            value = input('Unesite prezime: ').strip().lower()
            for one_ticket in tickets:
                if '&' in one_ticket.username:
                    last_name = one_ticket.username.lower().split('&')
                    if value in last_name[1]:
                        filtered_tickets.append(one_ticket)
                else:
                    for one_user in users:
                        if value in one_user.last_name.lower():
                            filtered_tickets.append(one_ticket)
        elif criteria == '4':
            while True:
                value = input('Unesite datum (u formatu YYYY-mm-dd): ').strip().lower()
                try:
                    date = datetime.strptime(value, '%Y-%m-%d')
                except ValueError:
                    kraj = (input(
                        'Niste dobro uneli datum, pokušajte ponovo ili napišite kraj ako zelite da odustanete').strip().
                            lower())
                    if kraj == 'kraj':
                        return False
                    continue
                for one_ticket in tickets:
                    date_of_ticket = datetime.strptime(one_ticket.screening_date.date, '%Y-%m-%d')
                    if date == date_of_ticket:
                        filtered_tickets.append(one_ticket)
                break
        elif criteria == '5':
            while True:
                value = input('Unesite vreme početka projekcije (u formatu XX:XX): ').strip().lower()
                try:
                    datetime.strptime(value, '%H:%M')
                except ValueError:
                    kraj = (input(
                        'Niste dobro uneli vreme, pokušajte ponovo ili napišite kraj ako želite da odustanete').strip().
                            lower())
                    if kraj == 'kraj':
                        return False
                    continue
                for one_ticket in tickets:
                    if value in one_ticket.screening_date.screening.start_time:
                        filtered_tickets.append(one_ticket)
                break
        elif criteria == '6':
            while True:
                value = input('Unesite vreme kraja projekcije (u formatu XX:XX): ').strip().lower()
                try:
                    datetime.strptime(value, '%H:%M')
                except ValueError:
                    kraj = (input(
                        'Niste dobro uneli vreme, pokušajte ponovo ili napišite kraj ako želite da odustanete').strip().
                            lower())
                    if kraj == 'kraj':
                        return False
                    continue
                for one_ticket in tickets:
                    if value in one_ticket.screening_date.screening.end_time:
                        filtered_tickets.append(one_ticket)
                break
        elif criteria == '7':
            while True:
                value = input('Unesite status karte:\n1.Rezervisana\n2.Prodata\n').strip()
                if value == '1':
                    for one_ticket in tickets:
                        if not one_ticket.sold:
                            filtered_tickets.append(one_ticket)
                    break
                elif value == '2':
                    for one_ticket in tickets:
                        if one_ticket.sold:
                            filtered_tickets.append(one_ticket)
                    break
                kraj = input(
                    'Pogresan unos, pokušajte ponovo ili napišite kraj ako želite da odustanete: ').strip().lower()
                if kraj == 'kraj':
                    return False
        elif criteria == '0':
            return False
        else:
            print('Nevalidan unos')
        kraj = input("Da li želite da pretražite preko još kriterijuma (unesite da ako želite): ").strip().lower()
        if kraj != 'da':
            break
        tickets = filtered_tickets
        filtered_tickets = []
    seller_print_out_tickets(filtered_tickets, users)
    return True


def seller_delete_reservation(tickets, users):
    seller_print_out_tickets(tickets, users)

    while True:
        while True:
            code = input('Unesite šifru projekcije rezervacije koju želite da obrišete: ').strip().upper()
            do_break = False
            for one_ticket in tickets:
                if code == one_ticket.screening_date.code:
                    do_break = True
            if do_break:
                break
            kraj = (input(
                'Nismo nasli projekciju sa tom šifrom, pokušajte ponovo ili napišite kraj ako želite da odustanete: ').
                    lower().strip())
            if kraj == 'kraj':
                return False

        while True:
            seat = input('Unesite sedište projekcije koju želite da obrišete: ').strip().upper()
            do_break = False
            for one_ticket in tickets:
                if seat == one_ticket.seat:
                    do_break = True
            if do_break:
                break
            kraj = (input(
                'Nismo našli projekciju sa tim sedištem, pokušajte ponovo ili napišite kraj ako želite '
                'da odustanete: ').lower().strip())
            if kraj == 'kraj':
                return False

        for one_ticket in tickets:
            if one_ticket.seat == seat and one_ticket.screening_date.code == code:
                tickets.remove(one_ticket)
                print('Karta je uspešno izbrisana')
        kraj = input('Da li želite da nastavise (napišite da ako želite): ').strip().lower()
        if kraj != 'da':
            break
    return True


def delete_reservation(tickets, logged_in_user):
    user_tickets = []
    for one_ticket in tickets:
        if one_ticket.username == logged_in_user.username and not one_ticket.sold:
            user_tickets.append(one_ticket)
    print_out_tickets(user_tickets)

    while True:
        while True:
            code = input('Unesite šifru projekcije rezervacije koju želite da obrišete: ').strip().upper()
            do_break = False
            for one_ticket in user_tickets:
                if code == one_ticket.screening_date.code:
                    do_break = True
            if do_break:
                break
            kraj = (input(
                'Nismo našli projekciju sa tom šifrom, pokušajte ponovo ili napišite kraj ako želite da odustanete: ').
                    lower().strip())
            if kraj == 'kraj':
                return False

        while True:
            seat = input('Unesite sedište projekcije koju želite da obrišete: ').strip().upper()
            do_break = False
            for one_ticket in user_tickets:
                if seat == one_ticket.seat:
                    do_break = True
            if do_break:
                break
            kraj = (input(
                'Nismo našli projekciju sa tim sedištem, pokušajte ponovo ili napišite kraj ako '
                'želite da odustanete: ').lower().strip())
            if kraj == 'kraj':
                return False

        for one_ticket in tickets:
            if one_ticket.seat == seat and one_ticket.screening_date.code == code:
                tickets.remove(one_ticket)
                print('Rezervacija je uspešno izbrisana')
        kraj = input('Da li želite da nastavite (napišite da ako želite): ').strip().lower()
        if kraj != 'da':
            break
    return True


def save_tickets(tickets):
    ticket_str = ''
    for one_ticket in tickets:
        sold_status = one_ticket.sold
        if not one_ticket.sold:
            sold_status = str(one_ticket.sold)
        ticket_str += (one_ticket.username + '|' + one_ticket.screening_date.code + '|' + one_ticket.seat + '|' +
                       one_ticket.date_of_sale + '|' +
                       sold_status + '|' + str(one_ticket.price) + '\n')
    with open('./database/tickets.txt', 'w') as file:
        file.write(ticket_str)
