from utils import (
    userFunctions, roomFunctions, screeningFunctions, screeningDateFunctions,
    ticketFunctions, loyaltyClubFunctions, reportFunctions
)
from utils import movieFunctions

movies = []
users = []
rooms = []
screenings = []
screeningDates = []
tickets = []
loyaltyClubMembers = []
reports = []


def main_menu():
    global users, movies, rooms, screenings, screeningDates, tickets, loyaltyClubMembers, reports
    rooms = roomFunctions.get_all_rooms()
    screenings = screeningFunctions.get_all_screenings(rooms)
    users = userFunctions.get_all_users()
    movies = movieFunctions.get_all_movies()
    screeningDates = screeningDateFunctions.get_all_screening_dates(screenings)
    tickets = ticketFunctions.get_all_tickets(screeningDates)
    loyaltyClubMembers = loyaltyClubFunctions.get_all_loyalty_club_members()
    reports = reportFunctions.get_all_reports()

    while True:
        choice = input('\nDobro došli u bioskop, upišite broj kako bi ste izabrali opciju:'
                       '\n1. Registrujte se\n2. Ulogujte se\n3. Pregledajte filmove\n4. Pretražite filmove'
                       '\n5. Pretražite termine bioskopskih projekcija\n0. Izadjite iz sistema\n').strip()

        if choice == '1':
            successful = userFunctions.register(users)
            if successful:
                print("\nUspešna registracija.")
        elif choice == '2':
            logged_in_user = userFunctions.login(users)
            if logged_in_user is not None:
                if logged_in_user.access_level == '0':
                    breaking = logged_in_menu(logged_in_user)
                    if breaking == 1:
                        break
                if logged_in_user.access_level == '1':
                    breaking = seller_menu(logged_in_user)
                    if breaking == 1:
                        break
                if logged_in_user.access_level == '2':
                    breaking = manager_menu(logged_in_user)
                    if breaking == 1:
                        break
        elif choice == '3':
            movieFunctions.print_out_movies(movies)
            input()
        elif choice == '4':
            value = movieFunctions.search(movies)
            if value:
                input()
        elif choice == '5':
            value = screeningDateFunctions.search_screening_dates(screeningDates)
            if value:
                input()
        elif choice == '0':
            break
        else:
            print('Pogrešan unos, probajte ponovo')

    userFunctions.save_users(users)
    movieFunctions.save_movies(movies)
    screeningFunctions.save_screenings(screenings)
    screeningDateFunctions.save_screening_dates(screeningDates)
    ticketFunctions.save_tickets(tickets)
    loyaltyClubFunctions.save_loyalty_club_members(loyaltyClubMembers)
    reportFunctions.save_reports(reports)


def logged_in_menu(logged_in_user):
    global users, movies, tickets, screeningDates, loyaltyClubMembers
    while True:
        choice = input("\nDobro došli " + str(logged_in_user.username) + ":\n1. Rezervišite kartu\n2. Izlogujte se"
                       "\n3. Promenite lične podatke\n4. Pregledajte rezervisane karte\n5. Poništite rezervaciju"
                       "\n6. Pregledajte filmove\n7. Pretražite filmove\n8. Pretražite termine bioskopskih projekcija"
                       "\n0. Izadjite iz sistema\n").strip()

        if choice == '1':
            ticketFunctions.reserve_ticket(tickets, screeningDates, logged_in_user, users, False, loyaltyClubMembers)
        elif choice == '2':
            break
        elif choice == '3':
            successful = userFunctions.change_data(logged_in_user, users)
            if successful:
                print("\nPodaci uspešno promenjeni")
        elif choice == '4':
            ticketFunctions.get_by_username(tickets, logged_in_user)
            input()
        elif choice == '5':
            value = ticketFunctions.delete_reservation(tickets, logged_in_user)
            if value:
                print('\nRezervacija je uspešno poništena')
        elif choice == '6':
            movieFunctions.print_out_movies(movies)
            input()
        elif choice == '7':
            value = movieFunctions.search(movies)
            if value:
                input()
        elif choice == '8':
            value = screeningDateFunctions.search_screening_dates(screeningDates)
            if value:
                input()
        elif choice == '0':
            return 1
        else:
            print('Pogrešan unos, pokušajte ponovo')
    return 0


def manager_menu(logged_in_user):
    global users, movies, screenings, rooms, screeningDates, loyaltyClubMembers
    while True:
        choice = input("\nDobro došli " + str(logged_in_user.username) + ":\n1. Dodajte korisnika\n2. Izlogujte se"
                       "\n3. Promenite lične podatke\n4. Dodajte film\n5. Pregledajte filmove\n6. Pretražite filmove"
                       "\n7. Promenite podatke filma\n8. Dodajte novu projekciju\n9. Generišite nove termine projekcija"
                       "\n10. Pretražite termine bioskopskih projekcija\n11. Pogledajte izveštaje\n"
                                                                         "12. Pogledajte sedišta projekcije"
                       "\n13. Dodelite karticu lojalnosti korisnicima\n14. Izbrišite film\n"
                                                                         "15. Promenite podatke projekcije"
                       "\n16. Izbrišite projekciju\n0. Izadjite iz sistema\n").replace(" ", "")

        if choice == '1':
            successful = userFunctions.manager_add_user(users)
            if successful:
                print("\nKorisnik je uspešno dodat")
        elif choice == '2':
            break
        elif choice == '3':
            successful = userFunctions.change_data(logged_in_user, users)
            if successful:
                print("\nPodaci uspešno promenjeni")
        elif choice == '4':
            value = movieFunctions.make_movie(movies)
            if value:
                print('\nFilm je uspešno dodat')
        elif choice == '5':
            movieFunctions.print_out_movies(movies)
            input()
        elif choice == '6':
            value = movieFunctions.search(movies)
            if value:
                input()
        elif choice == '7':
            value = movieFunctions.edit_movie(movies, screenings)
            if value:
                print('\nFilm je uspešno promenjen')
        elif choice == '8':
            value = screeningFunctions.make_screening(screenings, rooms, movies)
            if value:
                print('\nProjekcija je uspešno dodata')
        elif choice == '9':
            value = screeningDateFunctions.generate_dates(screeningDates, screenings)
            if value:
                print('\nTermini projekcije su generisani')
        elif choice == '10':
            value = screeningDateFunctions.search_screening_dates(screeningDates)
            if value:
                input()
        elif choice == '11':
            report_menu()
        elif choice == '12':
            value = roomFunctions.print_out_seats(screeningDates, tickets)
            if value:
                input()
        elif choice == '13':
            loyaltyClubFunctions.check_for_loyalty(users, tickets, loyaltyClubMembers)
        elif choice == '14':
            value = movieFunctions.delete_movie(movies, screenings, screeningDates, tickets)
            if value:
                print('\nFilm je uspešno izbrisan')
        elif choice == '15':
            value = screeningFunctions.edit_screening(screenings, movies, rooms, screeningDates, tickets)
            if value:
                print('\nProjekcija je uspešno izmenjena')
        elif choice == '16':
            value = screeningFunctions.delete_screening(screenings, screeningDates, tickets)
            if value:
                print('\nProjekcija je uspešno obrisana')
        elif choice == '0':
            return 1
        else:
            print('Pogrešan unos, pokušajte ponovo')
    return 0


def seller_menu(logged_in_user):
    global users, movies, tickets, screeningDates, loyaltyClubMembers
    while True:
        choice = input("\nDobro došli " + str(logged_in_user.username) + ":\n1. Rezervišite kartu\n2. Izlogujte se"
                       "\n3. Promenite lične podatke\n4. Pogledajte rezervisane karte\n5. Poništite rezervaciju"
                       "\n6. Pretražite karte\n7. Prodajte kartu\n8. Prodajte rezervisanu kartu\n9. Izmenite kartu"
                       "\n10. Automatski ponisštite rezervacije\n11. Pregledajte filmove\n12. Pretrazite filmove"
                       "\n13. Pretražite termine bioskopskih projekcija\n0. Izadjite iz sistema\n").strip()

        if choice == '1':
            ticketFunctions.reserve_ticket(tickets, screeningDates, logged_in_user, users, False, loyaltyClubMembers)
        elif choice == '2':
            break
        elif choice == '3':
            successful = userFunctions.change_data(logged_in_user, users)
            if successful:
                print("\nPodaci uspešno promenjeni")
        elif choice == '4':
            ticketFunctions.seller_print_out_reservations(tickets, users)
            input()
        elif choice == '5':
            ticketFunctions.seller_delete_reservation(tickets, users)
        elif choice == '6':
            value = ticketFunctions.search_tickets(tickets, users)
            if value:
                input()
        elif choice == '7':
            ticketFunctions.reserve_ticket(tickets, screeningDates, logged_in_user, users, True, loyaltyClubMembers)
        elif choice == '8':
            ticketFunctions.sell_reserved_ticket(tickets, users, logged_in_user, loyaltyClubMembers)
        elif choice == '9':
            value = ticketFunctions.seller_edit_ticket(tickets, users, screeningDates)
            if value:
                print('\nPodaci karte su uspešno promenjeni')
        elif choice == '10':
            ticketFunctions.automatic_cancel_reservations(tickets)
        elif choice == '11':
            movieFunctions.print_out_movies(movies)
            input()
        elif choice == '12':
            value = movieFunctions.search(movies)
            if value:
                input()
        elif choice == '13':
            value = screeningDateFunctions.search_screening_dates(screeningDates)
            if value:
                input()
        elif choice == '0':
            return 1
        else:
            print('Pogrešan unos, pokušajte ponovo')
    return 0


def report_menu():
    global tickets, users, reports
    while True:
        choice = input('Izaberite koji izveštaj želite:'
                       '\n1. Lista prodatih karata za odabran datum prodaje'
                       '\n2. Lista prodatih karata za odabran datum termina bioskopske projekcije'
                       '\n3. Lista prodatih karata za odabran datum prodaje i odabranog prodavca'
                       '\n4. Ukupan broj i ukupna cena prodatih karata za izabran dan (u nedelji) prodaje'
                       '\n5. Ukupan broj i ukupna cena prodatih karata za izabran dan (u nedelji) održavanja projekcije'
                       '\n6. Ukupna cena prodatih karata za zadati film u svim projekcijama'
                       '\n7. Ukupan broj i ukupna cena prodatih karata za izabran dan prodaje i odabranog prodavca'
                       '\n8. Ukupan broj i ukupna cena prodatih karata za prodavca u poslednjih 30 dana'
                       '\n9. Ispišite zapisane izveštaje\n0. Odustanite\n').strip()

        if choice == '1':
            ticketFunctions.get_sold_tickets_by_date(tickets, users, reports)
        elif choice == '2':
            ticketFunctions.get_sold_tickets_by_screening_date(tickets, users, screeningDates, reports)
        elif choice == '3':
            ticketFunctions.get_sold_tickets_by_date_and_seller(tickets, users, reports)
        elif choice == '4':
            ticketFunctions.get_sold_tickets_by_day_of_week(tickets, reports)
        elif choice == '5':
            ticketFunctions.get_sold_tickets_by_day_of_week_and_screening_date(tickets, screeningDates, reports)
        elif choice == '6':
            ticketFunctions.get_sold_tickets_by_movie(tickets, movies, reports)
        elif choice == '7':
            ticketFunctions.get_sold_tickets_by_day_of_week_and_seller(tickets, users, reports)
        elif choice == '8':
            ticketFunctions.get_sold_tickets_by_seller(tickets, users, reports)
        elif choice == '9':
            reportFunctions.print_reports(reports)
            input()
        elif choice == '0':
            return False
        else:
            print('Pogrešan unos, pokušajte ponovo')
