import pandas as pd
import re
import hashlib
from datetime import datetime


input_data = [
    '1. Gang 1x Hühner-Kokosnuss-Suppe 8.50 1x Karotten-Ingwer-Suppe 4.50 1x Ribollita 6.50 2. Gang 1x Caesar Salat 10.00 1x Chef Salat 10.00 # French Dressing 1x Chef Salat 10.00 # American Dressing',
    '1. Gang 1x Hühner-Kokosnuss-Suppe 8.50 1x Karotten-Ingwer-Suppe 4.50 1x Ribollita 6.50 2. Gang 1x Caesar Salat 10.00 1x Chef Salat 10.00 # French Dressing 1x Chef Salat 10.00 # American Dressing',
    '1. Gang 1x Hühner-Kokosnuss-Suppe 8.50 1x Karotten-Ingwer-Suppe 4.50 1x Ribollita 6.50 2. Gang 1x Caesar Salat 10.00 1x Chef Salat 10.00 # French Dressing 1x Chef Salat 10.00 # American Dressing',
    '1. Gang 1x Hühner-Kokosnuss-Suppe 8.50 1x Karotten-Ingwer-Suppe 4.50 1x Ribollita 6.50 2. Gang 1x Caesar Salat 10.00 1x Chef Salat 10.00 # French Dressing 1x Chef Salat 10.00 # American Dressing',
    '3. Gang 1x Burger Royal 21.00 # Bratkartoffel # extra Champignon + 1.50 1x Filet Steak 50.20 # 180 g 37,90 # Medium Rare (50øC) # Bratkartoffeln +4,90 # Kartoffelgratin +4,90 # Pepper Jus +2,50 1x Filet Steak 68.20 # 300 g 57,90 Medium Well (60øC) # Pommes +4,90 # Knoblauchbrot +2,90 # Sauce Bearnaise +2,50',
]

cards_headers = [
    '16-Mar-21 13:15 1 Burgermeister',
    '17-Mar-21 14:12 Burgermeister 2',
    '18-Mar-21 13:15 Hypersoft 3 5',
    '18-Mar-21 13:15 Burgermeister 2',
    '19-Mar-21 13:15 Hypersoft 5 1',
]


def hash_name(name=None):
    new_name = ""
    for character in name:
        if character.isalnum():
            new_name += character.lower()
    hashName = int(hashlib.sha256(
        new_name.encode('utf-8')).hexdigest(), 16) % 10**8
    return str(hashName)


def get_bonus_sepator(card_body_input):
    # The default separtor is "#"
    bonus_separtor = '#'
    for p in card_body_input:
        if '+ ' in p:
            for string in p.split('+ '):
                if not string.split(' ')[0].strip().replace('.', '').isnumeric():
                    bonus_separtor = '+'
                    break
        elif '&' in p:
            bonus_separtor = '&'
            break
        elif 'mit' in p:
            bonus_separtor = 'mit'
            break
        elif 'ohne' in p:
            bonus_separtor = 'ohne'
            break
    return bonus_separtor


def process_input_listgroup_v2(card_body_input):

    bonus_separtor = get_bonus_sepator(card_body_input)

    def get_type_details(chunk):
        result = {}

        price = re.findall("\d+\.\d+", chunk)
        if price:
            price = float(price[0])
        quantities = re.findall(r'\d+', chunk)
        if quantities:
            quantity = int(quantities[0])
        food_type_only = ' '.join(chunk.split()[1:-1])
        result = {
            'type': food_type_only,
            'quantity': quantity,
            'price': price,
            # 'type_id_str': f'{food_type_only}_{price}'.lower().strip().replace(' ', '_'),
        }
        return result

    cards = []
    for i in card_body_input:
        cards.append(re.split(r'\s(?=\d+. Gang|\d+x)', i))

    # I'm not very good on regex expressions; so i'll follow the tranditional way:
    df = pd.DataFrame()
    row = {}
    for i, part in enumerate(cards):
        for p in part:
            if 'gang' in p.lower():
                continue
            else:
                additionalInfo = []
                p_chunked = re.split(f'.(?={bonus_separtor})', p)
                for chunk in p_chunked:
                    if bonus_separtor in chunk:
                        additionalInfo.append(chunk)
                    else:
                        result = get_type_details(chunk)

                row['additionalInfo'] = '\n'.join(additionalInfo)
                row['type_id_str'] = hash_name(p)
                row.update(result)

                df = df.append(row, ignore_index=True)
    df = df.groupby(['type_id_str']).agg({
        'quantity': 'sum',
        'price': 'sum',
        'type': 'last',
        'additionalInfo': 'last'
    }).reset_index()
    df['type_id_int'] = list(range(len(df['type'])))
    df['production'] = 0
    return df


def process_input_cards_v2(card_body_input, card_header_input):
    bonus_separtor = get_bonus_sepator(card_body_input)

    def get_type_details(chunk):
        result = {}

        prices = re.findall("\d+\.\d+", chunk)
        if prices:
            price = float(prices[0])
        quantities = re.findall(r'\d+', chunk)
        if quantities:
            quantity = int(quantities[0])
        food_type_only = ' '.join(chunk.split()[1:-1])
        result = {
            'type': f'{quantity}x {food_type_only}',
            'type_only': food_type_only,
            'quantity': quantity,
            'price': price,
            # 'type_id_str': f'{food_type_only}_{price}'.lower().strip().replace(' ', '_'),
            # 'opt_id': int(opt_id)
        }
        return result

    def generate_opt_ids(df):
        result = pd.DataFrame()
        for type_id_int in df['type_id_int'].drop_duplicates():
            chunk_df = df.loc[df['type_id_int'] == type_id_int].copy()
            chunk_df['opt_id'] = list(range(len(chunk_df)))
            result = result.append(chunk_df, ignore_index=True)
        return result

    cards = []
    for i in card_body_input:
        cards.append(re.split(r'\s(?=\d+. Gang|\d+x)', i))

    # I'm not very good on regex expressions; so i'll follow the tranditional way:
    df = pd.DataFrame()
    row = {}
    for i, (part, header) in enumerate(zip(cards, card_header_input)):
        for p in part:
            if 'gang' in p.lower():
                row = {
                    'gang_title': p,
                    'gang_number': int(re.findall(r'\d+', p)[0]),
                    'gang_id': p.lower().replace(' ', '_')
                }
            else:
                additionalInfo = []
                p_chunked = re.split(f'.(?={bonus_separtor})', p)

                for chunk in p_chunked:
                    if bonus_separtor in chunk:
                        additionalInfo.append(chunk)
                    else:
                        result = get_type_details(chunk)
                row['type_id_str'] = hash_name(p)
                row['additionalInfo'] = '\n'.join(additionalInfo)
                row['type_id_int'] = i
                row['card_datetime'] = datetime.strptime(
                    ' '.join(header.split()[:2]), '%d-%b-%y %H:%M')
                row['card_date'] = row['card_datetime'].date()
                row['card_time'] = row['card_datetime'].time()
                if header.split()[2].isnumeric():
                    # Card index
                    row['process'] = int(header.split()[2])
                    # Card Phrase
                    row['waitress'] = ' '.join(header.split()[3:])
                else:
                    row['waitress'] = ' '.join(header.split()[2:-1])
                    row['process'] = int(header.split()[-1])

                row.update(result)

                df = df.append(row, ignore_index=True)

    df = generate_opt_ids(df)

    return df


new_listgroup_values = process_input_listgroup_v2(input_data)
new_cards_values = process_input_cards_v2(input_data, cards_headers)
