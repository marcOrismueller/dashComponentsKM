import re
import io
import glob
import os
import json
from time import sleep
from apps.fnc_container import crud_op_db, helpers
import ast
import pandas as pd
from datetime import datetime
import hashlib


def final_process_header(x):
    return re.sub(r'[()]', '', x).replace(' Tisch:', '')

def final_process_body(x):
    return x.replace('…', '')


def read_files(folderPath='./samples', lastFileReaded=None):
    card_header_list = []
    card_body_list = []
    newLastFileReaded = 0.000001
    for ext in ('*.100001', '*.100003', '*.100058', '*.100005'):
        available_files = glob.glob(os.path.join(folderPath, ext))
        for path_file in available_files:
            if lastFileReaded is None or float(os.path.getmtime(path_file)) > lastFileReaded:
                if newLastFileReaded < float(os.path.getmtime(path_file)):
                    newLastFileReaded = float(os.path.getmtime(path_file))

                f = open(path_file, "rb")
                raw = json.dumps(f.read().decode(errors='replace'))

                regex_one = r"(?:(?:[VW]L)|(?:B\\u000f))(\\u([a-z]+|000\d))+((\$[A-Z])|(\$\d)|(\$)| |(?:\#[^A-Z ])|\\u[0-9a-z]+)*((?:[a-zA-Z0-9 \/\-:\.\+\,#&]+(?:(?:(?:(?:(?:\\u[a-zA-Z]+)? ?\(\d* ?[a-zA-Z.]+\) *\\ufffd)|\\ufffd(?:[A-Za-z]*)?)|(?:(?:(?:\$2\$L\$G)|(?:\$G\$2\$L\\u0000L\$G))\\u0000(?:\\ufffd[a-zA-Z]?)?[A-Za-z]*(?:\(?\d* ?[a-zA-Z.]+\)?)? *\\ufffd)|(?:\([^()]*\)))? ?[0-9\.\/ ,+]*)?)|(?:(?:\* ){3,5}[A-Z ]{3,50}(?:\* ){3,5}))"
                raw = re.split(r"\w* ?(?:Zusammenfassung|Total)", raw)[0]
    
                matches = re.finditer(regex_one, raw, re.MULTILINE)
                text = ""
    
                for match_num, match in enumerate(matches, start=1):
                    if len(match.groups()) == 7:
                        line = f"{match.group(7)}\n"
                        if len(line) > 1:
                            text += line
    
                regex = r"(^#COPY$)|(^E$)|(^e$)|(^\d+$)|(Nr.:\d+)|(^\-[A-Z][a-z]{2,10}\-\d{2} \d{2}:\d{2})|(^: (\d|\d{2}|\d{3}))|( …)|(^\. Gang)|(\d+ Total .*)|(^ *: *\d* *$)|(^\+(?=[A-Z]))"
    
                text = re.sub(regex, "", text, flags=re.MULTILINE)
    
                text = re.sub(r"(?:\$2\$L\$G\\u0000)|(?: ##)", " ", text, flags=re.MULTILINE)
                text = re.sub(r"\$G\$2\$L\\u0000L\$G\\u0000", "", text, flags=re.MULTILINE)
                text = re.sub(r"\\ufffdhnchen", "ähnchen", text, flags=re.MULTILINE)
                text = re.sub(r"Hirschpl\\ufffdttli", "Hirschplättli", text, flags=re.MULTILINE)
                text = re.sub(r"K\\ufffdse", "Käse", text, flags=re.MULTILINE)
                text = re.sub(r"K\\ufffdCHE", "KÜCHE", text, flags=re.MULTILINE)
                text = re.sub(r"Au\\ufffder", "AUSSER", text, flags=re.MULTILINE)
                text = re.sub(r"\bHaus\b", "HAUS", text, flags=re.MULTILINE)
                text = re.sub(r"\\ufffdC", "øC", text, flags=re.MULTILINE)
                text = re.sub(r"\\ufffdse", "se", text, flags=re.MULTILINE)
                text = re.sub(r"\\ufffd", "…", text, flags=re.MULTILINE)
                text = re.sub(r"(?:\n(?:^.$)?)+", "\n", text, flags=re.MULTILINE)
                text = re.sub(r"[^\S\n]+", " ", text, flags=re.MULTILINE)
                text = re.sub(r"(?:^ )|(?: $)", "", text, flags=re.MULTILINE)
                text = re.sub(r"^((?:.(?!…[\d\.\/ ]+))+)\n(.+)(…[\d\.\/ ]+)\n(.*)(\w+) (…[\d\.\/ ]+)\n\5 …[\d\.\/ ]+", r"\1 \3\n\2\6\n\4", text, flags=re.MULTILINE)
                text = re.sub(r"\bähnchen", "Hähnchen", text, flags=re.MULTILINE)
                text = re.sub(r"Wok-Gemse", "Wok-Gemüse", text, flags=re.MULTILINE)
                text = re.sub(r"Lieferdienste", "+ Lieferdienste", text, flags=re.MULTILINE)
                text = re.sub(r" …[\d\.\/ ]+\n…[\d\.\/ ]+", "", text, flags=re.MULTILINE)
                text = re.sub(r"\n", " ", text, flags=re.MULTILINE)
    
                text = re.sub(r"([A-Z]+ +)(?:\1)+", r"\1", text, flags=re.MULTILINE)
                # print(text)
                parts = re.split(r'(?:(?<=\:\s\d\d\d)\s+|(?<=\:\s\d\d)\s+|(?<=\:\s\d)\s+|(?<=.)\s(?=[A-Z\s]+\d{1,2}x\b)|(?<=.)\s(?=\d{1,2}x\b))', text, maxsplit=1)
    
                parts[0] = parts[0].lstrip().rstrip()
                parts[1] = parts[1].lstrip().rstrip()
    
                card_header_list.append(parts[0])
                card_body_list.append(parts[1])
        
    return card_header_list, card_body_list, newLastFileReaded


def get_type_details(chunk):
    result = {}
    price = 0
    quantity = 0
    prices = re.findall("\d+\.\d+", chunk)
    if prices:
        price = float(prices[0])
    quantities = re.findall(r"[+-]?\d+(?:\.\d+)?", chunk)
    if quantities:
        quantity = int(quantities[0])
    food_type_only = ''
    infos = chunk.replace('/', '').split()[1:]
    for i, x in enumerate(infos):
        if re.match(r'^[+-]?\d+(?:\.\d+)$|^[+-]?\d+(?:,\d+)$|^[+-]?\d+', x) is None:
            food_type_only += f'{x} '

    result = {
        'type': f'{quantity}x {food_type_only}',
        'type_only': food_type_only.strip(),
        'available_quantity': quantity,
        'price': price,
    }
    return result

def get_bonus_sepator(p):
    # The default separtor is "#"
    bonus_separtor = '#'
    # for p in card_body_input:
    if '#' in p:
        return bonus_separtor
    if '+ ' in p:
        for string in p.split('+ '):
            if not string.split(' ')[0].strip().replace('.', '').isnumeric():
                bonus_separtor = '+'
                break
    elif '&' in p:
        bonus_separtor = '&'
        # break
    elif 'mit' in p:
        bonus_separtor = 'mit'
        # break
    elif 'ohne' in p:
        bonus_separtor = 'ohne'
        # break
    return bonus_separtor

def is_date(info='15-Apr-21'):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Juni',
              'Juli', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
    infos = info.split('-')
    if len(infos) == 3 and infos[0].isnumeric() and infos[2].isnumeric() and infos[1] in months:
        return True
    return False


def extract_header_infos(header='PIZZA&PASTA 15-Apr-21 15:55 5 Restaurant Hypersoft 12'):
    # Since the order of the infos is not fixed between the input header,
    # we have to find a trick to extract this infos correctly,
    # so we will take the date index as a reference to identify the other infos.
    infos_dict = {
        'card_datetime': '',
        'card_date': '',
        'card_time': '',
        'station': '',
        'waitress': '',
        'process': 0,
        'table': ''
    }
    infos = header.split()
    for info in infos:
        if is_date(info):
            date_idx = infos.index(info)
            break

    infos_dict['card_datetime'] = datetime.strptime(
        f'{infos[date_idx]} {infos[date_idx+1]}', '%d-%b-%y %H:%M')
    infos_dict['card_date'] = infos_dict['card_datetime'].date()
    infos_dict['card_time'] = infos_dict['card_datetime'].time()
    # Check what info available in the left of the date index.
    target_idx = date_idx-1
    if target_idx >= 0:
        if infos[target_idx].isnumeric():
            # Vorgang/Process
            infos_dict['process'] = int(infos[target_idx])
        else:
            # Station
            infos_dict['station'] = ' '.join(infos[:target_idx+1])
    else:
        pass

    # Check what info available on the right of the date index.
    target_idx = date_idx+2
    if len(infos) > target_idx:
        process = False
        for idx in range(target_idx, len(infos), 1):
            if infos[target_idx].isnumeric() and not process:
                # Vorgang/Process
                infos_dict['process'] = int(infos[target_idx])
            elif not infos[idx].isnumeric():
                infos_dict['waitress'] += f' {infos[idx]}'
            else:
                infos_dict['table'] = int(infos[idx])
            process = True

    infos_dict['waitress'] = infos_dict['waitress'].strip()

    return infos_dict


def generate_opt_ids(df):
    result = pd.DataFrame()
    for type_id_int in df['type_id_int'].drop_duplicates():
        chunk_df = df.loc[df['type_id_int'] == type_id_int].copy()
        chunk_df['opt_id'] = list(range(len(chunk_df)))
        result = result.append(chunk_df, ignore_index=True)
    return result


def hash_name(name=None):
    new_name = ""
    for character in name:
        if character.isalnum():
            new_name += character.lower()
    hashName = int(hashlib.sha256(
        new_name.encode('utf-8')).hexdigest(), 16) % 10**8
    return str(hashName)

def clean_item(item): 
    order_type = 'order'
    if 'Fehlbestellung' in item: 
        order_type = 're_order'
    numbers = re.findall(r"[+-]?\d+(?:\.\d+)?", item)
    for n in numbers: 
        if float(n) < 0: 
            newItem = item[item.find(f'{n}x'):]
            return newItem, order_type
    return item, order_type

# infos = '1. Gang 1x Ribollita 6.50/ 1 #Standard 6.50/ 1 1x Tomatencremesuppe 6.50/ 2 #Standard 6.50/ 2 2. Gang 6.50/ 2 6.50/ 2 1x Chili con Carne 8.50/ 2 #Standard 8.50/ 2 '
def extract_card_info(infos, header, idx):
    infos, order_type = clean_item(infos)
    body = infos.replace(header, '').strip()
    body_infos = re.split(r'\s(?=\d+. Gang|\d+x)', body)
    df = pd.DataFrame()
    row = {
        'gang_title': '',
        'gang_number': 0,
        'gang_id': '', 
        'order_type': order_type
    }
    header_success = False
    for info in body_infos:
        if re.search(r'(?=[1-9]+. Gang)', info):
            gang_info = ' '.join(info.split()[:info.index('Gang')-1])
            row['gang_title'] = gang_info
            row['gang_number'] = int(re.findall(r'\d+', gang_info)[0])
            row['gang_id'] = gang_info.lower().replace(' ', '_')

        elif re.search(r'(\d+x)', info):
            bonus = []
            bonus_separtor = get_bonus_sepator(info)
            if bonus_separtor == '+':
                p_chunked = [
                    d.replace(bonus_separtor, f'{bonus_separtor} ')
                    if not f'{bonus_separtor} ' in d
                    else d
                    for d in re.split(f'.(?=\{bonus_separtor})', info)
                ]
            else:
                p_chunked = [
                    d.replace(bonus_separtor, f'{bonus_separtor} ')
                    if not f'{bonus_separtor} ' in d
                    else d
                    for d in re.split(f'.(?={bonus_separtor})', info)
                ]
            for chunk in p_chunked:
                if bonus_separtor in chunk:
                    bonus.append(chunk)
                else:
                    row.update(get_type_details(chunk))
            row['bonus'] = '\n'.join(bonus)
            row['type_id_int'] = idx
            row['bonus_separtor'] = bonus_separtor
            if not header_success:
                row_dict = extract_header_infos(header)
                header_success = True
            row['type_id_str'] = hash_name(
                (str(row_dict['station'])+str(row_dict['waitress'])+str(row_dict['table'])+str(row['type_only'])+str(row['bonus'])).lower().strip()
            )
            row.update(row_dict)
            df = df.append(row, ignore_index=True)
    df = generate_opt_ids(df)
    return df


# Read the new files only
card_header_list, card_body_list, newLastFileReaded = read_files(
    lastFileReaded=00.7328925
)

card_header_list = [final_process_header(x) for x in card_header_list]
card_body_list = [final_process_body(x) for x in card_body_list]

listgroup_values = ast.literal_eval(str(card_body_list))
cards_headers = ast.literal_eval(str(card_header_list))
df = extract_card_info(
        '5x Club Sandwich 8.50/ 0 #Standard 8.50/ 0', 
        'KALTE KÜCHE 24-Sep-21 16:47 Hypersoft 77',
        48
    )

df = df.append(extract_card_info(
        '* * * S T O R N O * * * 1: Fehlbestellung -3x Club Sandwich 8.50/ 0 #Standard 8.50/ 0', 
        'KALTE KÜCHE 24-Sep-21 16:47 Hypersoft 77',
        49
    ), ignore_index=True)

# Push the data to our database...
abs(-23)
