import pandas as pd
import numpy as np
from datetime import datetime
import re


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def create_checkbox_opt(b):
    options = []
    for i, opt in b.iterrows():
        options.append({"label": opt['type'], "value": opt['opt_id']})
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
                status_data['positions'][i][f'{items.strip().split()[1]}'] = int(items.strip().split()[0])
    return status_data



def subtract_selected_v2(current_listgroup, cards_values_all, selected_vals, cards_options): 
    listgroup_df = pd.DataFrame.from_dict(current_listgroup)
    cards_vals_df = pd.DataFrame.from_dict(cards_values_all)
    
    selected_type_id_int = list(selected_vals.keys())
    for item_id in selected_type_id_int:
        selected_row = cards_vals_df.loc[cards_vals_df['type_id_int'] == item_id]
        # Check if type_id_str is available in listgroup_df
        available_items = listgroup_df.loc[listgroup_df['type_id_str'] == selected_row['type_id_str'].values[0]]
        if not available_items.empty:
            mask = (listgroup_df['type_id_str']==selected_row['type_id_str'].values[0]) & (listgroup_df['quantity'] >= selected_row['quantity'].values[0])
            idx = mask.idxmax() if mask.any() else np.repeat(False, len(listgroup_df))
            listgroup_df.loc[idx, 'quantity'] = listgroup_df.loc[idx, 'quantity'] - selected_row['quantity'].values[0]
        else:
            print(f'disable this item: {selected_row["type_id_str"].values[0]} (not item available or quantity > stock)')
    
    for i, card_item in cards_vals_df.iterrows():
        total = sum(listgroup_df.loc[listgroup_df['type_id_str'] == card_item['type_id_str']]['quantity'])
        if card_item['quantity'] > total and card_item['type_id_int'] not in selected_type_id_int:
            cards_options[i][0]['disabled'] = True
        else:
            cards_options[i][0]['disabled'] = False
        
    return listgroup_df, cards_options

def subtract_selected_v3(current_listgroup, cards_values_all, selected_vals, card_options, card_values): 
    listgroup_df = pd.DataFrame.from_dict(current_listgroup)
    cards_vals_df = pd.DataFrame.from_dict(cards_values_all)
    
    selected_type_id_int = list(selected_vals.keys())
    for item_id in selected_type_id_int:
        selected_options = cards_vals_df.loc[(cards_vals_df['type_id_int'] == item_id) & (cards_vals_df['opt_id'].isin(card_values[item_id]))]
        # Check if type_id_str is available in listgroup_df
        for i, selected_row in selected_options.iterrows():
            available_items = listgroup_df.loc[listgroup_df['type_id_str'] == selected_row['type_id_str']]
            if not available_items.empty:
                mask = (listgroup_df['type_id_str']==selected_row['type_id_str']) & (listgroup_df['quantity'] >= selected_row['quantity'])
                idx = mask.idxmax() if mask.any() else np.repeat(False, len(listgroup_df))
                listgroup_df.loc[idx, 'quantity'] = listgroup_df.loc[idx, 'quantity'] - selected_row['quantity']
            else:
                print(f'disable this item: {selected_row["type_id_str"].values[0]} (not item available or quantity > stock)')
        
    drop_rows = pd.DataFrame()
    for card_id in selected_type_id_int: 
        drop_rows = drop_rows.append(cards_vals_df[(cards_vals_df['type_id_int'] == card_id) & (cards_vals_df['opt_id'].isin(card_values[card_id]))])
    cards_vals_df.drop(drop_rows.index, inplace=True)
    
    for i, card_item in cards_vals_df.iterrows():
        total = sum(listgroup_df.loc[listgroup_df['type_id_str'] == card_item['type_id_str']]['quantity'])
        if card_item['quantity'] > total:
            card_options[card_item['type_id_int']][card_item['opt_id']]['disabled'] = True
        else:
            card_options[card_item['type_id_int']][card_item['opt_id']]['disabled'] = False
        
    return listgroup_df, card_options

def commit_subtraction_v2(clicked_btn_index, cards_values_all, cards_subtraction_details, card_values):

    if cards_subtraction_details:
        cards_subtraction_details = pd.DataFrame.from_dict(cards_subtraction_details)
    else: 
        cards_subtraction_details = pd.DataFrame(columns=['type_id_int', 'type', 'total_quantity', 'type_id_str', 'opt_id'])
           
    cards_vals_df = pd.DataFrame.from_dict(cards_values_all)
    selected_card_val = cards_vals_df.loc[(cards_vals_df['type_id_int'] == clicked_btn_index) & (cards_vals_df['opt_id'].isin(card_values[clicked_btn_index]))]

    def edit_total_quantity(row, card_val):
        if row['type_id_int'] == int(clicked_btn_index) and row['type_id_str'] == card_val['type_id_str']: 
            return int(card_val['quantity']) + int(row['total_quantity'])
        return int(row['total_quantity'])
    
    if not selected_card_val.empty:
        for i, card_val in selected_card_val.iterrows():
            df = cards_subtraction_details.loc[
                (cards_subtraction_details['type_id_int'] == int(clicked_btn_index)) &
                (cards_subtraction_details['type_id_str'] == card_val['type_id_str'])
            ]
            if df.empty:
                cards_subtraction_details = cards_subtraction_details.append({
                        'type_id_int': int(clicked_btn_index), 
                        'type': card_val['type'],
                        'type_only': card_val['type_only'],
                        'total_quantity': int(card_val['quantity']),
                        'type_id_str': card_val['type_id_str'],
                        'opt_id': int(card_val['opt_id']),
                        'card_datetime': card_val['card_datetime'], 
                        'card_date': card_val['card_date'],
                        'card_time': card_val['card_time'],
                        'card_phrase': card_val['card_phrase'],
                        'card_index': card_val['card_index'], 
                        
                    }, ignore_index=True)
            else: 
                cards_subtraction_details['total_quantity'] = cards_subtraction_details.apply(lambda row: edit_total_quantity(row, card_val), axis=1)
            
    return cards_subtraction_details.to_dict('records')

def get_tot_quantity(item):
    return f'{item["total_quantity"]} {item["type_only"]}'



def process_input_listgroup(data_elements):
    quantity = {}
    cards_vals = {}
    for i, d in enumerate(data_elements):
        # split string after every number or '+' operation
        cards_vals[i] = []
        d = re.split(r'\s?(\d+|\+)\s?', d)
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
