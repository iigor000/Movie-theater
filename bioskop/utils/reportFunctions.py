def get_all_reports():
    with open('./database/reports.txt', 'r', encoding='utf-8') as file:
        text = file.read()
        text = text.split('\n')
    return text


def write_report(reports, string, header):
    write = input('Da li želite da upišete taj izveštaj u fajl? (upišite da ako želite): ').strip().lower()
    if write == 'da':
        string_to_write = header + '\n' + string
        reports.append(string_to_write)


def print_reports(reports):
    for one_report in reports:
        print(one_report)


def save_reports(reports):
    report_str = ''
    for report in reports:
        report_str += report + '\n'
    report_str = report_str[:-1]
    with open('./database/reports.txt', 'w', encoding='utf-8') as file:
        file.write(report_str)
