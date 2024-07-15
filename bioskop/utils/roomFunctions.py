from model import room
from tabulate import tabulate

from utils import screeningDateFunctions


def get_all_rooms():
    rooms = []
    with open('./database/rooms.txt', 'r') as file:
        for line in file.readlines():
            line = line.split('|')
            rows = eval(line[3])
            one_room = room.Room(line[0], line[1], eval(line[2]), rows)
            rooms.append(one_room)
    return rooms


def print_out_seats(screening_dates, tickets):
    screeningDateFunctions.print_current_dates(screening_dates)
    selected_date = None
    while True:
        code = input('Unesite šifru termina projekcije čija sedišta želite da pogledate: ').strip().upper()
        for screening_date in screening_dates:
            if code == screening_date.code:
                selected_date = screening_date
                break
        if selected_date is not None:
            break
        kraj = input(
            'Nije pronadjen termin sa tom šifrom, pokušajte ponovo ili '
            'napišite kraj ako želite da odustanete: ').lower().strip()
        if kraj == 'kraj':
            return False

    taken_seats = []
    for one_ticket in tickets:  # Uzimamo zauzeta sedista kako bi ih razlikovali od slobodnih
        if one_ticket.screening_date == selected_date:
            taken_seats.append(one_ticket.seat)

    tabulate_tickets = []
    row = []
    # Pravimo matricu sedista
    for i in range(selected_date.screening.room.row_number):
        for j in selected_date.screening.room.row:
            seat = j + str(i)
            if seat in taken_seats:
                row.append('XX')
            else:
                row.append(seat)
        tabulate_tickets.append(row)
        row = []
    print(tabulate(tabulate_tickets, tablefmt='pretty'))
    return True
