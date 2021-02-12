import pandas as pd
import numpy as np


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def create_checkbox_opt(b):
    options = []
    for i, opt in b.iterrows():
        options.append({"label": opt['type'], "value": opt['opt_id']})
    # if len(b.strip().split()) > 2:
    #     new_list = divide_chunks(b.strip().split(), 2)
    #     for x, item in enumerate(new_list):
    #         options.append(
    #             {"label": f'{" ".join(item)}', "value": x}
    #         )
    #     return options

    #options.append({"label": f"{b['quantity']} {b['type']}", "value": 0}) 
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
        
    # for i, card_item in cards_vals_df.iterrows():
    #     total = sum(listgroup_df.loc[listgroup_df['type_id_str'] == card_item['type_id_str']]['quantity'])
    #     if card_item['quantity'] > total and card_item['type_id_int'] not in selected_type_id_int:
    #         card_options[i][0]['disabled'] = True
    #     else:
    #         card_options[i][0]['disabled'] = False
        
    return listgroup_df#, card_options

def commit_subtraction(clicked_btn_index, cards_values_all, cards_subtraction_details):

    if cards_subtraction_details:
        cards_subtraction_details = pd.DataFrame.from_dict(cards_subtraction_details)
    else: 
        cards_subtraction_details = pd.DataFrame(columns=['type_id_int', 'type', 'total_quantity', 'type_id_str'])
           
    cards_vals_df = pd.DataFrame.from_dict(cards_values_all)
    card_val = cards_vals_df.loc[cards_vals_df['type_id_int'] == clicked_btn_index]

    def edit_total_quantity(row):
        if row['type_id_int'] == int(clicked_btn_index): 
            return int(card_val['quantity']) + int(row['total_quantity'])
        return int(row['total_quantity'])
    
    if not card_val.empty:
        if int(clicked_btn_index) not in list(cards_subtraction_details['type_id_int']):
            cards_subtraction_details = cards_subtraction_details.append({
                    'type_id_int': int(clicked_btn_index), 
                    'type': card_val['type'].values[0],
                    'total_quantity': int(card_val['quantity'].values[0]),
                    'type_id_str': card_val['type_id_str'].values[0]
                }, ignore_index=True)
        else: 
            cards_subtraction_details['total_quantity'] = cards_subtraction_details.apply(edit_total_quantity, axis=1)
            
    return cards_subtraction_details.to_dict('records')

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
                        'total_quantity': int(card_val['quantity']),
                        'type_id_str': card_val['type_id_str'],
                        'opt_id': int(card_val['opt_id'])
                    }, ignore_index=True)
            else: 
                cards_subtraction_details['total_quantity'] = cards_subtraction_details.apply(lambda row: edit_total_quantity(row, card_val), axis=1)
            
    return cards_subtraction_details.to_dict('records')