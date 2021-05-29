import glob
import os
import io
import re

# Words or annoying signs that appear in every file
static_symbols = ['#####', 'FILE=', 'ISBO=1', 'SBO=1', 'COPY=1', '_', 'Nr', '=1', '##', 'LE=', '(', ')', 'Ihre VKStelle', '!!!',
                  'VKStelle', 'Tisch:']

# numbers or unnecessary dates get removed
dynamic_symbols = [r'(?:[0-9]{8}[.][0-9]{3}[.][0-9]{6})', r'(?:[0-9]{3}[.][0-9]{6})', r'(?:[.][:][0-9]{9})', r'(?:[.][:][0-9]{7})', r'(?:[:][0-9]{7})',
                   r'(?:[0-9]{7})']

# non-printable characters are collected here to be removed
printer_symbols = [
    'áõ', 'vB', '°B', 'tB', 'zB', '~B', 'B', 'B', 'B', 'B   ', 'B',
    '¢B', '¦B', 'ªB', '®B', '´B   ', '´B', '¸B', 'VL   ', 'VL', '', '', '', '\x00',
    '"áõ', 'VL', 'VL', '§VL', '©VL', '·VL', '¹VL', '»VL', '½VL', '¿VL', 'ÂVL', 'ÌVL', 'ÎVL'
]

substitution = "\\1 \\2"
split_operations = [r"(?:(\$\d{1})(\d{1}x|\d{2}x|\d{3}x))", # split 11x to 1 1x for meal counting
                    r"(?:(\$\w)(\d{2}-\w{3}-\d{2}))", # split dd-mmm-yy from $E for date time interpretation
                    r"(?:((\d{1}|\d{2}|\d{3}\d{4}).\d{2})(\$\d{1}))", # split x.xx$ to x.xx $ to interpret price levels
                    r"(?:(\$\+)(\w+))", # split $+String to $+ String
                    r"(?:(\d{1})(\$\-))", # split #$- to # $-
                    r"(?:(\w+)(\$\w{1}))", # split String$#x to String $#x
                    r"(?:(\$\d{1})(\w+))", # split $1IN to $1 IN
                    r"(?:(\$\w)(\w+))"]

card_header_list = []
card_body_list = []

class Preprocessing:

    def __init__(self, data_elements_header, data_elements_body):
        self.data_elements_header = data_elements_header
        self.data_elements_body = data_elements_body

    # reads all types of txt files
    for ext in ('*.100001', '*.100003', '*.bons100005', '*.100058'):
        # path needs to be as follows in PRODUCTION: C:\Hypers-!\Kasse-!\MAND0001\PRTJOBS
        for filepath in glob.glob(os.path.join('./bons', ext)):
            with io.open(filepath, "rt", encoding="latin1") as file:
                for line in file:
                    # loops through list of elements above to remove symbols
                    for s in static_symbols:
                        line = line.replace(s, '')
                    for p in printer_symbols:
                        line = line.replace(p, '')
                    for d in dynamic_symbols:
                        line = re.sub(d, '', line)

                # split operations of elements above are executed here
                for o in split_operations:
                    line = re.sub(o, substitution, line, 0, re.MULTILINE)
                # removes d-mmm-yy hh:mm from string
                line = re.sub(r'\b(?:\d-\w{3}-\d{2} \d{2}:\d{2})\b', '', line)
                # removes for example 1INHOUSE
                line = re.sub(r'\b(?:\d[A-Z]+)\b', '', line)
                # removes ch: #
                line = re.sub(r'\b(?:[ch]+: (\d|\d{2}|\d{3}))\b', '', line)
                # removes 'G', 'L', 'GG'
                line = re.sub(r'\b(?:[L]|[G]|[G]{2})\b', '', line)

                line = re.sub(r'(?i)\b\W*(e Fries|hnik|meister|telle|eet Fries| ft | t )\W*\b', ' ', line)
                # maybe needs to be readjusted for other german words with letters like ä/ü/ö
                line = line.replace("", "Ü")
                # lambda removes every part of string including a $ sign
                remover = lambda shit: ' '.join(i for i in shit.split() if '$' not in i)
                line = remover(line)

                # number 2 & letter E get removed
                line = re.sub(r'(?i)\b\W*(2 2 2 2|2 2 2|E E)\W*\b', ' ', line)
                # last part of string gets removed because unnecessary
                line_split_one = line.split("Zusammenfassung", 1)
                line = line_split_one[0]
                line_split_two = line.split("Total", 1)
                line = line_split_two[0]

                # turn 20 12 20 20 to 12
                regex_match = r"(?:(\d+ \d+ \d+ \d+ ))"
                matches = re.finditer(regex_match, line, re.MULTILINE)

                for matchNum, match in enumerate(matches, start=1):
                    match.group()
                    replacement_variable = match.group().split()
                    replacement_variable = replacement_variable[1] + " "
                    line = re.sub(regex_match, replacement_variable, line, 0, re.MULTILINE)

                # remove duplicate occurrence of "Gang" e.g. 12. Gang after 2. Gang (12. Gang gets removed)
                regex_3 = r"(?:(\d{2}[.] Gang ))"
                regex_3_substitution = ""
                line = re.sub(regex_3, regex_3_substitution, line, 0, re.MULTILINE)

                # removes everything between first number and 1st date occurence
                regex_2 = r"(?:(\w+ \w+|\d+|\w+ [/] \w+) (.*?) (\d{2}-\w{3}-\d{2}))"
                regex_2_substitution = "\\1 \\3"
                line = re.sub(regex_2, regex_2_substitution, line, 0, re.MULTILINE)

                # split string before every #. #x or STRING
                parts = re.split(r'(?<=.\w)\s(?=[A-Z]+\b|\dx|\d{2}x|\d{3}x|\d\.[ ]\w+)', line, 1)

                # replace 15.50 15 with 15.50 in second part of string
                regex_replace_prices = r"(?:(\b\d.\d{2} \d \d|\d{2}.\d{2} \d{2} \d\b|\b\d{3}.\d{2} \d{3} \d\b|\b\d.\d{2} \d\b|\b\d{2}.\d{2} \d{2}\b|\b\d{3}.\d{2} \d{3}\b))"
                matches_prices = re.finditer(regex_replace_prices, parts[1], re.MULTILINE)

                for matchPrice, match_price in enumerate(matches_prices, start=1):
                    match_price.group()
                    replacement_price = match_price.group().split()
                    parts[1] = re.sub(regex_replace_prices, replacement_price[0], line, 0, re.MULTILINE)

                # separate splitted elements in two lists
                card_header_list.append(parts[0])
                card_body_list.append(parts[1])

    # put lists in card header and card body to start preprocessing
    def card_header(self):
        for i in range(len(card_header_list)):
            header_content = card_header_list[i]
            self.data_elements_header.append(header_content)
        return self.data_elements_header

    def card_body(self):
        for i in range(len(card_body_list)):
            body_content = card_body_list[i]
            self.data_elements_body.append(body_content)
        return self.data_elements_body


