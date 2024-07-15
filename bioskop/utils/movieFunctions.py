from model import movie
from tabulate import tabulate


def get_all_movies():
    movies = []
    with open('./database/movies.txt', 'r') as file:
        for line in file.readlines():
            line = line.split('|')
            directors = eval(line[3])
            actors = eval(line[4])
            one_movie = movie.Movie(line[0], line[1], line[2], directors, actors, line[5], line[6], line[7],
                                    eval(line[8]))
            movies.append(one_movie)
    return movies


# Korisitima tabulate biblioteku za ispisivanje
# Prvo napravimo listu koja sadrzi vise listi koje predstavljaju svaki objekat koji ce se ispisati
# Pravimo jos jednu listu sa naslovima za svaki od atributa koji ce se ispisivati i
# na kraju pozivamo tabulate funkciju koja ispisuje tabelu
def print_out_movies(movies):
    tabulate_movies = []
    for one_movie in movies:
        if one_movie.active:
            tabulate_movies.append([one_movie.name, one_movie.genre, one_movie.duration + 'min',
                                    ','.join(str(director) for director in one_movie.directors),
                                    ','.join(str(actor) for actor in one_movie.main_roles_array), one_movie.country,
                                    one_movie.year, one_movie.description])
    headers = ['Naziv', 'Žanr', 'Trajanje', 'Režiser(i)', 'Glavne uloge', 'Zemlja porekla', 'Godina produkcije',
               'Kratak opis']
    print(tabulate(tabulate_movies, headers=headers, tablefmt='pretty'))


# Funkcia uzima kriterijum po kojem se pretrazuje i ako film sa tim kriterijumom postoji dodaje ga u novu listu filmova.
# Kada je su filmovi dodati u listu, moguce je pretraziti ih po jos nekom kriterijumu i
# sve tako dok korisnik ne zeli da ih ispise, onda se ispisuje lista sa tim filmovima
def search(movies):
    filtered_movies = []
    active_movies = []
    for one_movie in movies:
        if one_movie.active:
            active_movies.append(one_movie)
    movies = active_movies
    while True:
        criteria = input(
            'Izaberite kriterijum po kojem želite da pretražite film:\n'
            '1. Naziv\n'
            '2. Žanr\n'
            '3. Minimalno trajanje\n'
            '4. Maksimalno trajanje\n'
            '5. Trajanje (navodite minimalnu i maksimalnu granicu trajanja filma)\n'
            '6. Režiseri\n'
            '7. Glavne uloge\n'
            '8. Zemlja porekla\n'
            '9. Godina proizvodnje\n'
            '0. Odustanite\n').strip()
        if criteria == '1':
            value = input('Unesite naziv: ').strip().lower()
            for one_movie in movies:
                if value in one_movie.name.lower():
                    filtered_movies.append(one_movie)
        elif criteria == '2':
            value = input('Unesite žanr: ').strip().lower()
            for one_movie in movies:
                if value in one_movie.genre.lower():
                    filtered_movies.append(one_movie)
        elif criteria == '6':
            value = input('Unesite režisera: ').strip().lower()
            for one_movie in movies:
                for director in one_movie.directors:
                    if value in director.lower():
                        filtered_movies.append(one_movie)
        elif criteria == '7':
            value = input('Unesite glumca: ').strip().lower()
            for one_movie in movies:
                for actor in one_movie.main_roles_array:
                    if value in actor.lower():
                        filtered_movies.append(one_movie)
        elif criteria == '8':
            value = input('Unesite zemlju porekla: ').strip().lower()
            for one_movie in movies:
                if value in one_movie.country.lower():
                    filtered_movies.append(one_movie)
        elif criteria == '9':
            while True:
                value = input('Unesite godinu proizvodnje: ').strip().lower()
                if value.isdigit():
                    for one_movie in movies:
                        if value in one_movie.year.lower():
                            filtered_movies.append(one_movie)
                    break
                kraj = input(
                    'Godina mora biti validan broj, pokušajte ponovo ili napisite kraj ako želite da odustanete: '
                ).strip().lower()
                if kraj == 'kraj':
                    return False
        elif criteria == '0':
            return
        elif criteria == '3':
            while True:
                try:
                    value = eval(input(
                        'Unesite minimalno trajanje (u minutima): '
                    ))
                    break
                except ValueError:
                    kraj = input(
                        'Uneli ste nevalidne karaktere, pokusšajte ponovo ili napišite kraj ako želite da odustanete: '
                    )
                    if kraj == 'kraj':
                        return False
            for one_movie in movies:
                if value <= int(one_movie.duration):
                    filtered_movies.append(one_movie)
        elif criteria == '4':
            while True:
                try:
                    value = eval(input(
                        'Unesite maximalno trajanje (u minutima): '
                    ))
                    break
                except ValueError:
                    kraj = input(
                        'Uneli ste nevalidne karaktere, pokušajte ponovo, ili napišite kraj ako želite da odustanete: '
                    )
                    if kraj == 'kraj':
                        return False
            for one_movie in movies:
                if value >= int(one_movie.duration):
                    filtered_movies.append(one_movie)
        elif criteria == '5':
            while True:
                try:
                    min_duration = eval(input(
                        'Unesite donju granicu (u minutima): '
                    ))
                    break
                except ValueError:
                    kraj = input(
                        'Uneli ste nevalidne karaktere, pokušajte ponovo, ili napišite kraj ako želite da odustanete'
                    )
                    if kraj == 'kraj':
                        return False
            while True:
                try:
                    max_duration = eval(input(
                        'Unesite gornju granicu (u minutima): '
                    ))
                    break
                except ValueError:
                    kraj = input(
                        'Uneli ste nevalidne karaktere, pokušajte ponovo, ili napišite kraj ako želite da odustanete'
                    )
                    if kraj == 'kraj':
                        return False
            for one_movie in movies:
                if min_duration <= int(one_movie.duration) <= max_duration:
                    filtered_movies.append(one_movie)
        else:
            print('Nevalidan unos')
        kraj = input(
            "Da li želite da pretrazite preko još kriterijuma (unesite da ako želite): "
        ).strip().lower()
        if kraj != 'da':
            break
        movies = filtered_movies
        filtered_movies = []
    print_out_movies(filtered_movies)
    return True


def make_movie(movies):
    while True:
        name = input("Unesite naziv filma: ").strip().replace("|", "")
        do_continue = False
        for one_movie in movies:
            if one_movie.active:
                if name.lower() in one_movie.name.lower():
                    kraj = input(
                        'Vec postoji film sa ovim imenom ili ste uneli prazan red, pokušajte ponovo ili'
                        ' unesite kraj ako želite da odustanete: ').strip().lower()
                    if kraj == 'kraj':
                        return False
                    do_continue = True
                    break
        if do_continue:
            continue
        if name != '':
            break
        kraj = input(
            'Nazim filma ne može biti prazan, pokušajte ponovo ili '
            'napišite kraj ako želite da odustanete: ').strip().lower()
        if kraj == 'kraj':
            return False
    while True:
        genre = input('Unesite žanr filma: ').strip().replace("|", "")
        if genre != '':
            break
        kraj = input(
            'Žanr filma ne može biti prazan pokušajte ponovo, '
            'ili napišite kraj ako želite da odustanete: ').strip().lower()
        if kraj == 'kraj':
            return False
    while True:
        duration = input('Unesite trajanje filma (u minutima): ').strip().replace("|", "")
        if duration.isdigit():
            break
        kraj = input(
            'Trajanje filma mora biti validan broj, pokušajte ponovo,'
            ' ili napisšite kraj ako želite da odustanete: ').strip().lower()
        if kraj == 'kraj':
            return False
    directors = []
    while True:
        director = input('Unesite režisera (napisite kraj kada zavrsite): ').strip().replace("|", "")
        if director == '':
            print('Režiser ne može biti prazan, pokusajte ponovo')
            continue
        if director.lower() == 'kraj':
            if len(directors) > 0:
                break
            print('Morate uneti bar jednog režisera')
            continue
        directors.append(director)
    actors = []
    while True:
        actor = input('Unesite glavnog glumca (napišite kraj kada završite): ').strip().replace("|", "")
        if actor == '':
            print('Glumac ne može biti prazan, pokusajte ponovo')
            continue
        if actor.lower() == 'kraj':
            if len(actors) > 0:
                break
            print('Morate uneti bar jednog glavnog glumca')
            continue
        actors.append(actor)
    while True:
        country = input("Unesite zemlju porekla: ").strip().replace("|", "")
        if country != '':
            break
        kraj = input(
            'Zemlja porekla ne može biti prazna, pokušajte ponovo'
            ' ili napisite kraj ako želite da odustante: ').strip().lower()
        if kraj == 'kraj':
            return False
    while True:
        year = input('Unesite godinu prozivodnje: ').strip().replace("|", "")
        if year.isdigit():
            break
        kraj = input(
            'Godina proizvodnje mora biti validan broj, pokušajte ponovo'
            ' ili napišite kraj ako želite da odustanete: ').strip().lower()
        if kraj == 'kraj':
            return False
    while True:
        description = input('Unesite skraceni opis filma: ').strip().replace("|", "")
        if description != '':
            break
        kraj = input(
            'Opis filma ne sme biti prazan, pokušajte ponovo ili'
            ' napišite kraj ako želite da odustanete: ').strip().lower()
        if kraj == 'kraj':
            return False
    movie_to_add = movie.Movie(name, genre, duration, directors, actors, country, year, description, True)
    movies.append(movie_to_add)
    return True


def save_movies(movies):
    movie_string = ''
    for one_movie in movies:
        movie_string += (one_movie.name + '|' + one_movie.genre + '|' + one_movie.duration + '|' + str(
            one_movie.directors) + '|' + str(
            one_movie.main_roles_array) + '|' + one_movie.country + '|' + one_movie.year + '|' + one_movie.description +
                         '|' + str(
            one_movie.active) + '\n')
    with open('./database/movies.txt', 'w') as file:
        file.write(movie_string)


def edit_movie(movies, screenings):
    print_out_movies(movies)
    name_changed = False
    old_name = None

    while True:
        movie_to_search = input('Izaberite film koji želite da promenite (unesite naziv): ').strip().lower()
        selected_movie = None
        do_break = False
        for one_movie in movies:
            if one_movie.active:
                if movie_to_search == one_movie.name.lower():
                    selected_movie = one_movie
                    do_break = True
        if do_break:
            break
        kraj = input('Nismo našli film sa tim imenom, unesite kraj ako želite da odustanete: ').strip().lower()
        if kraj == 'kraj':
            return

    print("Izabrali ste:")
    selected_movie_to_print = [selected_movie]
    print_out_movies(selected_movie_to_print)
    print('Napišite nove podatke (ako ništa ne napišete podatak se ne menja)')

    while True:
        name = input('Unesite novo ime: ').replace("|", "").strip()
        if name == '':
            break
        for one_movie in movies:
            if name in one_movie.name:
                kraj = input(
                    'Već postoji film sa ovim imenom, pokušajte ponovo ili'
                    ' unesite kraj ako želite da odustanete: ').strip().lower()
                if kraj == 'kraj':
                    return False
                continue
        old_name = selected_movie.name
        selected_movie.name = name
        name_changed = True
        break
    genre = input('Unesite novi zanr: ').replace("|", "").strip()
    if genre != '':
        selected_movie.genre = genre
    while True:
        duration = input('Unesite novo trajanje filma (u minutima): ').replace("|", "").strip()
        if duration.isdigit():
            selected_movie.duration = duration
            break
        elif duration == '':
            break
        kraj = input(
            'Trajanje filma mora biti validan broj, pokušajte ponovo'
            ' ili napišite kraj ako želite da odustanete: ').strip().lower()
        if kraj == 'kraj':
            return False
    country = input('Unesite novu zemlju prekla: ').replace("|", "").strip()
    if country != '':
        selected_movie.country = country
    while True:
        year = input('Unesite novu godinu proizvodnje: ').replace("|", "").strip()
        if year.isdigit():
            selected_movie.year = year
            break
        elif year == '':
            break
        kraj = input(
            'Godina proizvodnje mora biti validan broj, pokušajte'
            ' ponovo ili napišite kraj ako želite da odustanete: ').strip().lower()
        if kraj == 'kraj':
            return False
    description = input('Unesite novi opis filma: ').replace("|", "").strip()
    if description != '':
        selected_movie.description = description

    directors = []
    print('Za svakog od režisera napišite da ako želite da ostane u listi')
    for director in selected_movie.directors:
        stay = input(director + ': ').strip().lower()
        if stay == 'da':
            directors.append(director)
    while True:
        director = input('Unesite novog režisera (napišite kraj kada završite): ').strip().replace("|", "")
        if director == '':
            print('Režiser ne može biti prazan, pokušajte ponovo')
            continue
        if director.lower() == 'kraj':
            if len(directors) > 0:
                break
            print('Mora postojati bar jedan režiser za film')
            continue
        directors.append(director)
    selected_movie.directors = directors

    actors = []
    print('Za svakog od glavnih glumaca napišite da ako želite da ostane u listi')
    for actor in selected_movie.main_roles_array:
        stay = input(actor + ': ').strip().lower()
        if stay == 'da':
            actors.append(actor)
    while True:
        actor = input('Unesite glavnog glumca (napišite kraj kada završite): ').strip().replace("|", "")
        if actor == '':
            print('Glumac ne može biti prazan, pokušajte ponovo')
            continue
        if actor.lower() == 'kraj':
            if len(actors) > 0:
                break
            print('Mora postojati bar jedan glavni glumac za film')
            continue
        actors.append(actor)
    selected_movie.main_roles_array = actors

    if name_changed:
        for one_screening in screenings:
            if one_screening.movie == old_name:
                one_screening.movie = name

    return True


def delete_movie(movies, screenings, screening_dates, tickets):
    print_out_movies(movies)

    while True:
        movie_to_search = input('Izaberite film koji želite da promenite (unesite naziv): ').strip().lower()
        selected_movie = None
        do_break = False
        for one_movie in movies:
            if one_movie.active:
                if movie_to_search == one_movie.name.lower():
                    selected_movie = one_movie
                    do_break = True
        if do_break:
            break
        kraj = input('Nismo našli film sa tim imenom, unesite kraj ako želite da odustanete: ').strip().lower()
        if kraj == 'kraj':
            return

    print("Izabrali ste:")
    selected_movie_to_print = [selected_movie]
    print_out_movies(selected_movie_to_print)
    delete = input('Da li želite da obrišete ovaj film (unesite da ako želite)').strip().lower()
    if delete == 'da':
        selected_movie.active = False
        inactive_codes = []
        for one_screening in screenings:
            if one_screening.movie == selected_movie.name:
                one_screening.active = False
                inactive_codes.append(one_screening.code)
        for one_date in screening_dates:
            for code in inactive_codes:
                if code in one_date.code:
                    one_date.active = False
        for one_ticket in tickets:
            if not one_ticket.sold:
                for code in inactive_codes:
                    if code in one_ticket.screening_date.code:
                        tickets.remove(one_ticket)
        return True
    return False
