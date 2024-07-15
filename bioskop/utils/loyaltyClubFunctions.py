from datetime import datetime, timedelta


def get_all_loyalty_club_members():
    loyalty_club_members = []

    with open('./database/loyaltyClub.txt', 'r') as file:
        for line in file.readlines():
            loyalty_club_members.append(line.replace('\n', ''))

    return loyalty_club_members


def save_loyalty_club_members(loyalty_club_members):
    member_string = '\n'.join(loyalty_club_members) + '\n'

    with open('./database/loyaltyClub.txt', 'w') as file:
        file.write(member_string)


# Prolazimo kroz sve korisnike i gledamo da li su potrosili vise od 5000 u prethodnih godinu dana
def check_for_loyalty(users, tickets, loyalty_club_members):
    print('Korisnici kojima su dodeljene kartice lojalnosti: ')
    now = datetime.now()
    year_earlier = now - timedelta(days=365)

    for one_user in users:
        price = 0
        for one_ticket in tickets:
            if one_ticket.username == one_user.username:
                date = datetime.strptime(one_ticket.date_of_sale, '%Y-%m-%d')
                if date > year_earlier:
                    price += one_ticket.price
        if price > 5000 and one_user.username not in loyalty_club_members:
            print(one_user.username)
            loyalty_club_members.append(one_user.username)
