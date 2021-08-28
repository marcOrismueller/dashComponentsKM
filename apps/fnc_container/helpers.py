import pandas as pd
import numpy as np
from datetime import datetime
import re
import dash_html_components as html
import hashlib
import json
from app import engine
from apps.fnc_container import crud_op_db
import dash_dangerously_set_inner_html

def hash_name(name=None):
    new_name = ""
    for character in name:
        if character.isalnum():
            new_name += character.lower()
    hashName = int(hashlib.sha256(
        new_name.encode('utf-8')).hexdigest(), 16) % 10**8
    return str(hashName)

def list_items(product_type):
    price = "{:0,.2f}".format(float(product_type['price'])).replace('.', ',')
    disabled = False
    bonusBtnStyle = 'bonus_btn'
    if product_type['bonus'].strip() == '':
        disabled = True 
        bonusBtnStyle = 'bonus_btn_disabled'
    items = [
        html.Div([
                html.B(f"{product_type['production']}/{product_type['available_quantity']} {product_type['type_only']} {price}", className='main-food'),
                html.Div([
                    html.Span(b) for b in product_type['bonus'].split('\n')
                ], 
                className='hide-bonus',
                id={'id': 'bonus_section', 'index': product_type['type_id_str']} 
                )
            ], 
            className='listItemBtn', 
            id={'id': 'lst_item_btn', 'index': product_type['type_id_str']}
        ),
        html.Button(
            dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'''
                    <i class="fa fa-chevron-circle-down fa-2x" aria-hidden="true"></i>               
                '''),  
            id={
                'id': 'bonus_btn',
                'index': product_type['type_id_str']
            },
            disabled=disabled, 
            className=bonusBtnStyle
        )
            
    ]
    return html.Div(items, style={'display': 'flex', 'flexDirection':'row', 'alignItems': 'baseline'})



def type_line_break(product_type, btns=False, quantity=True):
    price = "{:0,.2f}".format(float(product_type['price'])).replace('.', ',')
    if btns:
        if quantity:
            return [
                html.B(f"{product_type['production']}/{product_type['available_quantity']} {product_type['type_only']} {price}", className='main-food'),
                html.Div([
                    html.Span(b) for b in product_type['bonus'].split('\n')
                ], className='bonus')
            ]
        else:
            return [
                html.P(l)
                for l in f"{product_type['available_quantity']} {product_type['type_only']} {price}".split('\n')
            ]
    return f"{product_type['type']} {price} \n{product_type['bonus']}"


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def card_body(b, previous_selected):
    result = []
    for gang_number in b.sort_values(by='gang_number')['gang_number'].drop_duplicates():
        options = []
        for i, opt in b.loc[b['gang_number'] == gang_number].reset_index(drop=True).iterrows():
            if i == 0:
                gang = html.Div([
                        html.Div([
                                html.H6(opt['gang_title']),
                            ], 
                            className='card-item', 
                            id={'id': 'card_body_value_gang', 'index': f'{opt["type_id_int"]}_{gang_number}'}
                        ),
                        html.Button(
                            dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'''
                                    <i class="fa fa-expand fa-2x" aria-hidden="true"></i>               
                                '''),  
                            id={
                                'id': 'show_gang_items',
                                'index': f'{opt["type_id_int"]}_{gang_number}'
                            },
                            className='bonus_btn'
                        )
                    ], className='gang-items', style={'display': 'none' if gang_number==0 else 'flex'})
            price = "{:0,.2f}".format(float(opt['price'])).replace('.', ',')
                
            options.append(
                html.Div([
                    html.Div([
                        html.B(
                            f"{opt['type']} {price}", 
                            className='main-food'
                        ),
                        html.Div([
                                html.Span(b) for b in opt['bonus'].split('\n')
                            ], 
                            className='hide-bonus',
                            id={'id': 'bonus_section_card', 'index': f"{opt['type_id_int']}_{gang_number}_{opt['type_id_str']}"} 
                        )], 
                        className='card-item crossout-item' if f"{opt['type_id_int']}_{gang_number}_{opt['type_id_str']}" in previous_selected else 'card-item', 
                        id={'id': 'card_body_value', 'index': f"{opt['type_id_int']}_{gang_number}_{opt['type_id_str']}"},
                        n_clicks=1 if f"{opt['type_id_int']}_{gang_number}_{opt['type_id_str']}" in previous_selected else 0
                    ),
                    html.Button(
                        dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'''
                                <i class="fa fa-chevron-circle-down fa-2x" aria-hidden="true"></i>               
                            '''),  
                        id={
                            'id': 'bonus_btn_card',
                            'index': f"{opt['type_id_int']}_{gang_number}_{opt['type_id_str']}"
                        },
                        disabled= True if opt['bonus'].strip() == '' else False, 
                        className= 'bonus_btn_disabled' if opt['bonus'].strip() == '' else 'bonus_btn'
                    )
                ], className='gang-items')
            )
        result.append(html.Div([
            gang, 
            html.Div(
                options, 
                className= '' if gang_number==0 else 'hide', 
                style={'marginLeft': '15px'}, id={'id': 'gang_items', 'index': f'{opt["type_id_int"]}_{gang_number}'}
            )
        ]))
    return result



def create_checkbox_opt(b):
    options = []
    for gang_number in b.sort_values(by='gang_number')['gang_number'].drop_duplicates():
        for i, opt in b.loc[b['gang_number'] == gang_number].reset_index(drop=True).iterrows():
            if i == 0:
                options.append(
                    {"label": f"{opt['gang_title']}", "value": f'gang_{gang_number}_card_{opt["type_id_int"]}'})
            options.append({"label": type_line_break(
                opt), "value": opt['type_id_str']})
    return options


def get_tot_quantity(item):
    return type_line_break(item, btns=True, quantity=False)


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

def update_val(row, item):
    if row['type_id_str'] == item['type_id_str']:
        row['production'] += item['available_quantity']
        row['available_quantity'] -= item['available_quantity']
    return row


def update_production(cards, current_production, checked_items=[]):
    def update(row):
        if row['type_id_int'] == current_production:
            return row['available_quantity']
        return row['production']

    def update_2(row):
        if row['type_id_str'] in checked_items:
            return row['production'] - row['available_quantity']
        return row['production']

    cards['production'] = cards.apply(update, axis=1)
    #cards['production'] = cards.apply(update_2, axis=1)
    return cards


def get_opts_vals(substruct_if_clicked, vals, cards):
    for card in substruct_if_clicked:
        if int(card.split('_')[1])+1 <= len(cards) and int(card.split('_')[0]) in cards['type_id_int'].tolist():
            vals[int(card.split('_')[1])] = substruct_if_clicked[card]

    return vals


def is_date(info='15-Apr-21'):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Juni',
              'Juli', 'Aug', 'Sept', 'Okt', 'Nov', 'Dez']
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


def get_type_details(chunk):
    result = {}
    price = 0
    quantity = 0
    prices = re.findall("\d+\.\d+", chunk)
    if prices:
        price = float(prices[0])
    quantities = re.findall(r'\d+', chunk)
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


def generate_opt_ids(df):
    result = pd.DataFrame()
    for type_id_int in df['type_id_int'].drop_duplicates():
        chunk_df = df.loc[df['type_id_int'] == type_id_int].copy()
        chunk_df['opt_id'] = list(range(len(chunk_df)))
        result = result.append(chunk_df, ignore_index=True)
    return result


# infos = '1. Gang 1x Ribollita 6.50/ 1 #Standard 6.50/ 1 1x Tomatencremesuppe 6.50/ 2 #Standard 6.50/ 2 2. Gang 6.50/ 2 6.50/ 2 1x Chili con Carne 8.50/ 2 #Standard 8.50/ 2 '
def extract_card_info(infos, header, idx):
    body = infos.replace(header, '').strip()
    body_infos = re.split(r'\s(?=\d+. Gang|\d+x)', body)
    df = pd.DataFrame()
    row = {
        'gang_title': '',
        'gang_number': 0,
        'gang_id': ''
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
            row['type_id_str'] = hash_name(info)
            row['bonus'] = '\n'.join(bonus)
            row['type_id_int'] = idx
            row['bonus_separtor'] = bonus_separtor
            if not header_success:
                row_dict = extract_header_infos(header)
                header_success = True
            row.update(row_dict)
            df = df.append(row, ignore_index=True)
    df = generate_opt_ids(df)
    return df


def extract_informations(input_data, cards_headers):
    data = pd.DataFrame()
    last_id = crud_op_db.get_last_card_id()
    for idx, (body, header) in enumerate(zip(input_data, cards_headers)):
        data = data.append(extract_card_info(
            body, header, idx+last_id), ignore_index=True)
    return data


def foods_listing(df):
    result = df.groupby(['type_id_str']).agg({
        'available_quantity': 'sum',
        'price': 'sum',
        'type': 'last',
        'type_only': 'last',
        'bonus': 'last',
        'production': 'sum',
        'selected': 'sum'
    }).reset_index()
    result['type_id_int'] = range(len(result))
    result['available_quantity'] -= result['production']
    return result


def intersection(current, food_tracer):
    result = pd.merge(
        current.drop(['available_quantity', 'production', 'selected', 'gang_number'], axis=1), food_tracer, how='left', on=['type_id_int', 'type_id_str']
    )
    return result


def item_selected(food_tracer, context): 
    context_dict = json.loads(context[0].get('prop_id', None).split('.')[0])
    if len(context_dict['index'].split('_')) > 2 :
        type_id_int = int(context_dict['index'].split('_')[0])
        gang_number = int(context_dict['index'].split('_')[1])
        type_id_str = context_dict['index'].split('_')[2]
        if context[0]['value']%2==0:
            food_tracer['selected'] = np.where(
                    (food_tracer['type_id_int'] == type_id_int) & (
                        food_tracer['type_id_str'] == type_id_str), 0, food_tracer['selected']
                )
        else:
            food_tracer['selected'] = np.where(
                        (food_tracer['type_id_int'] == type_id_int) & (
                            food_tracer['type_id_str'] == type_id_str), 1, food_tracer['selected']
                    )
    else: 
        if context[0]['value']%2==0:
            food_tracer['selected'] = np.where(
                    (food_tracer['type_id_int'] == int(context_dict['index'].split('_')[0])) & (
                        food_tracer['gang_number'] == int(context_dict['index'].split('_')[1])),
                    0,
                    food_tracer['selected']
                )
        else: 
            food_tracer['selected'] = np.where(
                (food_tracer['type_id_int'] == int(context_dict['index'].split('_')[0])) & (
                    food_tracer['gang_number'] == int(context_dict['index'].split('_')[1])),
                1,
                food_tracer['selected']
            )
    return food_tracer


def insert_selected_item(food_tracer, context):
    value = context[0].get('value', None)
    context_dict = context[0].get('prop_id', None)
    context_dict = json.loads(context_dict.split('.')[0])
    type_id_int = int(context_dict['index'].split('_')[0])
    food_tracer['selected'] = np.where(
        food_tracer['type_id_int'] == type_id_int, 0, food_tracer['selected'])
    for type_id_str in value:
        if 'gang_' in type_id_str:
            food_tracer['selected'] = np.where(
                (food_tracer['type_id_int'] == type_id_int) & (
                    food_tracer['gang_number'] == int(type_id_str.split('_')[1])),
                1,
                food_tracer['selected']
            )
        else:
            food_tracer['selected'] = np.where(
                (food_tracer['type_id_int'] == type_id_int) & (
                    food_tracer['type_id_str'] == type_id_str), 1, food_tracer['selected']
            )

    return food_tracer


def insert_selected_item_2(food_tracer, context, current_cards):
    context_dict = context[0].get('prop_id', None)
    context_dict = json.loads(context_dict.split('.')[0])
    type_id_str = context_dict['index'].split('_')[0]
    available_cards = current_cards.loc[
        (current_cards['type_id_str'] == type_id_str) &
        (current_cards['selected'] == 0) &
        (current_cards['production'] > 0)
    ]
    if not available_cards.empty:
        type_id_int = available_cards['type_id_int'].values[0]
        food_tracer['selected'] = np.where(
            (food_tracer['type_id_int'] == type_id_int) & (
                food_tracer['type_id_str'] == type_id_str), 1, food_tracer['selected']
        )
    return food_tracer

def hourly_converter(df, cols, daily=False):
    if daily:
        df['sales_created'] = pd.to_datetime(df['sales_created']).map(lambda x: x.replace(hour=0, minute=0, second=0))
    else:
        df['sales_created'] = pd.to_datetime(df['sales_created']).map(lambda x: x.replace(minute=0, second=0))
    df = df.groupby(cols).agg({
        'price': 'sum', 
        'available_quantity': 'sum', 
        'type_only': 'last', 
        'bonus': 'last'
    }).reset_index()
    # mask = df['type_only'].duplicated(keep=False)
    # df.loc[mask, 'type_only'] += df.groupby('type_only').cumcount().add(1).astype(str)
    df = df.rename(columns={
        'price': 'Price', 
        'available_quantity': 'Total quantity', 
        'type_only': 'Food', 
        'bonus': 'Bonus', 
        'sales_created': 'Date', 
        'table': 'Table'
    })
    
    return df


def groupdf(df):
    df = df.groupby(['type_id_str']).agg({
        'price': 'sum', 
        'available_quantity': 'sum', 
        'type_only': 'last'
    }).reset_index()
    df = df.rename(columns={
        'price': 'Total price', 
        'available_quantity': 'Total quantity', 
        'type_only': 'Food'
    })

    mask = df['Food'].duplicated(keep=False)
    df.loc[mask, 'Food'] += df.groupby('Food').cumcount().add(1).astype(str)
    
    return df

def all_selected(selectedCardItems, id):
    id = id.split('_')[1:]
    return set(selectedCardItems) == set(id)