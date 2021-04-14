import pandas as pd
import numpy as np
from datetime import datetime
import re
import dash_html_components as html
import hashlib
import json


def hash_name(name=None):
    new_name = ""
    for character in name:
        if character.isalnum():
            new_name += character.lower()
    hashName = int(hashlib.sha256(
        new_name.encode('utf-8')).hexdigest(), 16) % 10**8
    return str(hashName)


def type_line_break(product_type, btns=False, quantity=True):
    price = "{:0,.2f}".format(float(product_type['price'])).replace('.', ',')
    if btns:
        if quantity:
            return [
                html.B(l)
                for l in f"{product_type['production']}/{product_type['quantity']} {product_type['type']} {price}\n{product_type['additionalInfo']}".split('\n')
            ]
        else:
            return [
                html.P(l)
                for l in f"{product_type['quantity']} {product_type['type_only']} {price}\n{product_type['additionalInfo']}".split('\n')
            ]
    return f"{product_type['type']} {price} \n{product_type['additionalInfo']}"


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


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


def initialize(current_listgroup):
    status_data = {
        'default': current_listgroup,
        'positions': {},
    }
    for i, lst in enumerate(current_listgroup):
        status_data['positions'][i] = {}
        for items in lst:
            if len(items.strip().split()) > 2:
                l = divide_chunks(items.strip().split(), 2)
                for j, el in enumerate(l):
                    status_data['positions'][i][f'{el[1]}'] = int(el[0])

            else:
                status_data['positions'][i][f'{items.strip().split()[1]}'] = int(
                    items.strip().split()[0])
    return status_data


def subtract_selected_v2(current_listgroup, cards_values_all, selected_vals, cards_options):
    listgroup_df = pd.DataFrame.from_dict(current_listgroup)
    cards_vals_df = pd.DataFrame.from_dict(cards_values_all)

    selected_type_id_int = list(selected_vals.keys())
    for item_id in selected_type_id_int:
        selected_row = cards_vals_df.loc[cards_vals_df['type_id_int'] == item_id]
        # Check if type_id_str is available in listgroup_df
        available_items = listgroup_df.loc[listgroup_df['type_id_str']
                                           == selected_row['type_id_str'].values[0]]
        if not available_items.empty:
            mask = (listgroup_df['type_id_str'] == selected_row['type_id_str'].values[0]) & (
                listgroup_df['quantity'] >= selected_row['quantity'].values[0])
            idx = mask.idxmax() if mask.any() else np.repeat(False, len(listgroup_df))
            listgroup_df.loc[idx, 'quantity'] = listgroup_df.loc[idx,
                                                                 'quantity'] - selected_row['quantity'].values[0]
        else:
            print(
                f'disable this item: {selected_row["type_id_str"].values[0]} (not item available or quantity > stock)')

    for i, card_item in cards_vals_df.iterrows():
        total = sum(listgroup_df.loc[listgroup_df['type_id_str']
                                     == card_item['type_id_str']]['quantity'])
        if card_item['quantity'] > total and card_item['type_id_int'] not in selected_type_id_int:
            cards_options[i][0]['disabled'] = True
        else:
            cards_options[i][0]['disabled'] = False

    return listgroup_df, cards_options


def subtract_selected_v3(input_data, substruct_if_clicked):
    listgroup_df = pd.DataFrame.from_dict(
        input_data['initial']['listgroup_values'])
    cards_vals_df = pd.DataFrame.from_dict(
        input_data['initial']['cards_values'])
    selected_type_id_int = list(substruct_if_clicked.keys())
    for item_id in selected_type_id_int:
        selected_options = cards_vals_df.loc[(cards_vals_df['type_id_int'] == int(item_id.split(
            '_')[0])) & (cards_vals_df['type_id_str'].isin(substruct_if_clicked[item_id]))]
        # Check if type_id_str is available in listgroup_df
        for i, selected_row in selected_options.iterrows():
            available_items = listgroup_df.loc[listgroup_df['type_id_str']
                                               == selected_row['type_id_str']]
            if not available_items.empty:
                mask = (listgroup_df['type_id_str'] == selected_row['type_id_str']) & (
                    listgroup_df['production'] >= selected_row['quantity'])
                idx = mask.idxmax() if mask.any() else np.repeat(False, len(listgroup_df))
                #listgroup_df.loc[idx, 'quantity'] = listgroup_df.loc[idx, 'quantity'] - selected_row['quantity']
                listgroup_df.loc[idx, 'production'] = listgroup_df.loc[idx,
                                                                       'production'] - selected_row['quantity']
            else:
                print(
                    f'disable this item: {selected_row["type_id_str"].values[0]} (not item available or quantity > stock)')

    return listgroup_df


def commit_subtraction_v2(cards_values_all, cards_subtraction_details, substruct_items):
    cards_vals_df = pd.DataFrame.from_dict(cards_values_all)

    cards_subtraction_details = cards_subtraction_details or {}
    cards_subtraction_details = pd.DataFrame.from_dict(
        cards_subtraction_details)

    for card in substruct_items:
        card_id = int(card.split('_')[0])
        data = cards_vals_df.loc[
            (cards_vals_df['type_id_int'] == int(card.split('_')[0])) &
            (cards_vals_df['type_id_str'].isin(
                substruct_items[card]))
        ]
        if not cards_subtraction_details.empty:
            if card_id not in cards_subtraction_details['type_id_int'].tolist():
                cards_subtraction_details = cards_subtraction_details.append(
                    data, ignore_index=True)
        else:
            cards_subtraction_details = cards_subtraction_details.append(
                data, ignore_index=True)

    return cards_subtraction_details.to_dict('records')


def get_tot_quantity(item):
    return type_line_break(item, btns=True, quantity=False)


def process_input_listgroup(data_elements):
    quantity = {}
    cards_vals = {}
    for i, d in enumerate(data_elements):
        # split string after every number or '+' operation
        cards_vals[i] = []
        #d = re.split(r'\s?(\d+|\+)\s?', d)
        d = re.split(r'\s?(\d+)\s?', d)
        # add up all elements separately
        for idx, value in enumerate(d):
            if value.isdigit() or value == '+':
                if value == '+':
                    count = 1
                else:
                    count = int(value)

                data = d[idx + 1]
                cards_vals[i].append({
                    f'{data}': count
                })

                quantity[data] = quantity.get(data, 0) + count

    df = pd.DataFrame()
    df['type'] = list(quantity.keys())
    df['quantity'] = list(quantity.values())
    df['type_id_str'] = df['type'].str.lower().str.replace(' ', '_')
    df['type_id_int'] = list(range(len(df['type'])))

    # If the select any cards selected field = 1
    return df


def process_input_cards(data_elements, cards_headers):
    cards_vals = pd.DataFrame()
    for i, (d, header) in enumerate(zip(data_elements, cards_headers)):
        # split string after every number or '+' operation
        #d = re.split(r'\s?(\d+|\+)\s?', d)
        d = re.split(r'\s?(\d+)\s?', d)
        # add up all elements separately
        opt_id = 0
        for idx, value in enumerate(d):
            if value.isdigit() or value == '+':
                if value == '+':
                    count = 1
                else:
                    count = int(value)

                data = d[idx + 1]

                cards_vals = cards_vals.append({
                    'type': f'{value} {data}',
                    'type_only': data,
                    'quantity': count,
                    'type_id_str': data.lower().strip().replace(' ', '_'),
                    'type_id_int': int(i),
                    'opt_id': int(opt_id),
                    'card_datetime': datetime.strptime(' '.join(header.split()[:2]), '%d-%b-%y %H:%M'),
                    'card_date': datetime.strptime(' '.join(header.split()[:2]), '%d-%b-%y %H:%M').date(),
                    'card_time': datetime.strptime(' '.join(header.split()[:2]), '%d-%b-%y %H:%M').time(),
                    'card_phrase': ' '.join(header.split()[2:-1]),
                    'card_index': int(header.split()[-1])
                }, ignore_index=True)
                opt_id += 1

    # If the select any cards selected field = 1
    return cards_vals


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
                    row['card_index'] = int(header.split()[2])
                    # Card Phrase
                    row['card_phrase'] = ' '.join(header.split()[3:])
                else:
                    row['card_phrase'] = ' '.join(header.split()[2:-1])
                    row['card_index'] = int(header.split()[-1])

                row.update(result)

                df = df.append(row, ignore_index=True)

    df = generate_opt_ids(df)

    return df


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


def process_input_lstgrp(data_elements):
    lstgrp = pd.DataFrame()
    for i, d in enumerate(data_elements):
        # split string after every number or '+' operation
        d = re.split(r'\s?(\d+|\+)\s?', d)
        # add up all elements separately
        opt_id = 0
        for idx, value in enumerate(d):
            if value.isdigit() or value == '+':
                if value == '+':
                    count = 1
                else:
                    count = int(value)

                data = d[idx + 1]

                lstgrp = lstgrp.append({
                    'type': f'{value} {data}',
                    'type_only': data,
                    'quantity': count,
                    'type_id_str': data.lower().strip().replace(' ', '_'),
                    'type_id_int': int(i),
                    'opt_id': int(opt_id),
                }, ignore_index=True)
                opt_id += 1

    # Aggr items from the same grp
    lstgrp = lstgrp.groupby(['type_id_int', 'type_id_str']).agg({
        'quantity': 'sum',
        'type': 'last',
        'type_only': 'last',
    }).reset_index()
    # If the select any cards selected field = 1
    return lstgrp


def id_format(item):
    item = ' '.join(item.split()[1:])
    return item.lower().strip().replace(' ', '_')


def click_list_handler(card_values, card_options, context, input_data):
    df = pd.DataFrame.from_dict(input_data['initial']['cards_values'])
    process_done = False
    for idx, (vals, opts) in enumerate(zip(card_values, card_options)):
        for i, opt in enumerate(opts):
            if i in vals:
                continue
            else:
                if opt['value'] == context['index']:
                    card_values[idx].append(opt['value'])
                    gang_number = df.loc[
                        (df['type_id_str'] == opt['value']) &
                        (df['type_id_int'] == idx)
                    ]
                    if not gang_number.empty:
                        gang_number = gang_number['gang_number'].values[0]
                        df = df.loc[
                            (df['type_id_int'] == idx) &
                            (df['gang_number'] == gang_number)

                        ]

                        if len([x for x in card_values[idx] if x in df['type_id_str'].tolist()]) == len(df):
                            card_values[idx].append(
                                f'gang_{gang_number}_card_{idx}')
                    process_done = True
                    break
        if process_done:
            break

    return card_values


def click_list_handler_1(current_listgroup, cards_values_all, substruct_if_clicked, context):
    listgroup_df = pd.DataFrame.from_dict(current_listgroup)
    cards_values = pd.DataFrame.from_dict(cards_values_all)

    item = listgroup_df.loc[listgroup_df['type_id_str'] == context['index']]
    cards_items = cards_values.loc[cards_values['type_id_str']
                                   == item['type_id_str'].values[0]]
    for card_idx in cards_items['type_id_int'].drop_duplicates():
        if str(card_idx) in [x.split('_')[0] for x in substruct_if_clicked]:
            index = [s for s in substruct_if_clicked if str(
                card_idx) == s.split('_')[0]][0]
            opt_id = cards_items.loc[cards_items['type_id_int']
                                     == card_idx]['type_id_str'].values[0]
            if opt_id in substruct_if_clicked[index]:
                continue
            else:
                # substruct_if_clicked[index].append(opt_id)
                return index.split('_')[0]
                # break
        else:
            #substruct_if_clicked[index] = [cards_items.loc[cards_items['type_id_int'] == card_idx]['type_id_str'].values[0]]
            return str(card_idx)
            break

    return None


def get_gang_subelements(cards_values_all, substruct_if_clicked, context_values, idx):
    card_df = pd.DataFrame.from_dict(cards_values_all)
    available_gangs = card_df['gang_number'].drop_duplicates().tolist()
    for gang_number in available_gangs:
        all_sub_elements = card_df.loc[
            (card_df['type_id_int'] == int(idx.split('_')[0])) &
            (card_df['gang_number'] == gang_number)]['type_id_str'].tolist()

        if f'gang_{gang_number}_card_{int(idx.split("_")[0])}' in context_values:

            if str(idx) in substruct_if_clicked and substruct_if_clicked[str(idx)]:
                substruct_if_clicked[str(
                    idx)] += (all_sub_elements + [f'gang_{gang_number}_card_{int(idx.split("_")[0])}'])
            else:
                substruct_if_clicked[str(idx)] = (
                    all_sub_elements + [f'gang_{gang_number}_card_{int(idx.split("_")[0])}'])
        else:
            if str(idx) in substruct_if_clicked:
                substruct_if_clicked[str(idx)] = [
                    x for x in substruct_if_clicked[str(idx)]
                    if x not in (all_sub_elements + [f'gang_{gang_number}_card_{int(idx.split("_")[0])}'])
                ]
            else:
                substruct_if_clicked[str(idx)] = []
    # for val in context_values:
    #     if 'gang' in val:
    #         gang_number = int(val.split('_')[1])
    #         card_idx = int(val.split('_')[-1])

    #         all_sub_elements = card_df.loc[
    #          (card_df['type_id_int'] == card_idx) &
    #          (card_df['gang_number'] == gang_number)]['type_id_str'].tolist()
    #         if str(card_idx) in substruct_if_clicked and substruct_if_clicked[str(card_idx)]:
    #             substruct_if_clicked[str(card_idx)] += all_sub_elements
    #         else:
    #             substruct_if_clicked[str(card_idx)] = all_sub_elements

    #     else:
    #         pass

    # for gang in gang_x:
    #     gang_number = int(gang.split('_')[1])
    #     card_idx = int(gang.split('_')[-1])
    #     card_df = pd.DataFrame.from_dict(cards_values_all)
    #     all_sub_elements = card_df.loc[
    #         (card_df['type_id_int'] == card_idx) &
    #         (card_df['gang_number'] == gang_number)
    #     ]['type_id_str'].tolist()
    #     if str(card_idx) in substruct_if_clicked and substruct_if_clicked[str(card_idx)]:
    #         substruct_if_clicked[str(card_idx)] += all_sub_elements
    #     else:
    #         substruct_if_clicked[str(card_idx)] = all_sub_elements
    #     substruct_if_clicked[str(card_idx)] = list(dict.fromkeys(substruct_if_clicked[str(card_idx)]))

    substruct_if_clicked[str(idx)] = list(
        dict.fromkeys(substruct_if_clicked[str(idx)]))

    return substruct_if_clicked


def init_substruct_if_clicked(context):
    substruct_if_clicked = {}
    for d in context:
        ids = json.loads(d['prop_id'].split('.')[0])
        if ids['id'] == 'card_value':
            substruct_if_clicked[ids['index']] = []

    return substruct_if_clicked


def gang_checker(substruct_if_clicked, cards, old_values, new_values, context_dict):
    if len(old_values) > len(new_values):
        diff = list(set(old_values) - set(new_values))
        if diff and 'gang_' in diff[0]:
            # deselect all values of that gang..
            gang_items = cards.loc[
                (cards['type_id_int'] == int(diff[0].split('_')[-1])) &
                (cards['gang_number'] == int(diff[0].split('_')[1]))
            ]['type_id_str'].tolist()
            substruct_if_clicked[context_dict['index']] = [
                x for x in new_values if x not in gang_items]
            return substruct_if_clicked
        else:
            return substruct_if_clicked

    for type_id_int in cards['type_id_int'].drop_duplicates():
        selected = [val for key, val in substruct_if_clicked.items()
                    if f'{int(type_id_int)}_' in key][0]
        for gang_number in cards.loc[cards['type_id_int'] == type_id_int]['gang_number'].drop_duplicates():
            gang_subselements = cards.loc[
                (cards['type_id_int'] == type_id_int) &
                (cards['gang_number'] == gang_number)
            ]

            key = list(dict(filter(
                lambda item: f'{int(type_id_int)}_' in item[0], substruct_if_clicked.items())).keys())[0]
            gang_id = f"gang_{int(gang_subselements['gang_number'].values[0])}_card_{int(type_id_int)}"

            if all(item in selected for item in gang_subselements['type_id_str'].tolist()) \
                    and gang_id not in selected:
                substruct_if_clicked[key] += [gang_id]

            elif gang_id in selected:
                substruct_if_clicked[key] += gang_subselements['type_id_str'].tolist()

            substruct_if_clicked[key] = list(
                dict.fromkeys(substruct_if_clicked[key]))

    return substruct_if_clicked


def subtract(cards, substruct_if_clicked, context_dict, card_body):
    if context_dict['id'] == 'lst_item_btn':
        type_id_str = context_dict['index']
        # selects all the elemets with in cards that have this type_id_str
        available_items = cards.loc[cards['type_id_str'] == type_id_str]
        for type_id_int in available_items['type_id_int'].drop_duplicates():
            selected = [val for key, val in substruct_if_clicked.items(
            ) if f'{int(type_id_int)}_' in key][0]
            # if this item is already crossed out... : Do nothing
            # But if not:
            if type_id_str not in selected:
                key = list(dict(filter(
                    lambda item: f'{int(type_id_int)}_' in item[0], substruct_if_clicked.items())).keys())[0]
                if card_body[int(key.split('_')[1])] != 'disabled':
                    substruct_if_clicked[key] += [type_id_str]
                    substruct_if_clicked[key] = list(
                        dict.fromkeys(substruct_if_clicked[key]))
                    break

    return substruct_if_clicked


def update_val(row, item):
    if row['type_id_str'] == item['type_id_str']:
        row['production'] += item['quantity']
        row['quantity'] -= item['quantity']
    return row


def substruct_all_card_items(cards, lists, card_idx):
    card_item = cards.loc[cards['type_id_int'] == int(card_idx.split('_')[1])]
    for i, item in card_item.iterrows():
        lists = lists.apply(lambda row: update_val(row, item), axis=1)
    #substruct_items[card_idx] = card_item['type_id_str'].tolist()
    # return substruct_items

    return lists.to_dict('records')


def get_opts_vals(substruct_if_clicked, vals):
    for card in substruct_if_clicked:
        vals[int(card.split('_')[1])] = substruct_if_clicked[card]

    return vals


def disable_commit_btns(card_values, substruct_if_clicked, card_options):
    btns_visibility = []
    for i, opts in enumerate(card_values):
        idx = [x for x in list(substruct_if_clicked.keys()) if f'_{i}' in x]
        current_vals = substruct_if_clicked.get(idx[0], [])
        if opts:
            if len(current_vals) == len(card_options[i]):
                btns_visibility.append(False)
            else:
                btns_visibility.append(True)
        else:
            btns_visibility.append(False)


def card_gangs_count(card_df):
    return len(card_df.drop_duplicates(subset=['gang_number']))


def check_if_selected_all(cards, substruct_if_clicked, disabled):
    for card in substruct_if_clicked:
        card_df = cards.loc[cards['type_id_int'] == int(card.split('_')[0])]
        items_count = len(card_df) + card_gangs_count(card_df)
        if items_count == len(substruct_if_clicked[card]) or len(substruct_if_clicked[card]) == 0:
            disabled[int(card.split('_')[1])] = False
        else:
            disabled[int(card.split('_')[1])] = True

    return disabled
