import pandas as pd
import numpy as np


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def create_checkbox_opt(b):
    options = []
    # if len(b.strip().split()) > 2:
    #     new_list = divide_chunks(b.strip().split(), 2)
    #     for x, item in enumerate(new_list):
    #         options.append(
    #             {"label": f'{" ".join(item)}', "value": x}
    #         )
    #     return options

    options.append({"label": f"{b['quantity']} {b['type']}", "value": 0}) 
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


def re_struct(data, is_df = False):
    if is_df: 
        df = pd.DataFrame.from_dict(data)
        data = list(df['quantity'].astype(str) + ' ' + df['type'])

    new_list = []
    for items in data:
        if not is_df and len(items.split()) > 2:
           l = [' '.join(items.split()[i * 2:(i + 1) * 2]) for i in range((len(items.split()) + 2 - 1) // 2 )]  
        else: 
           l = [items]
        new_list.append(l)
    return new_list

def aggr_listgroup_items(grouplists):
    item_value = {}
    for lst in grouplists:
        for item in lst:
            if item.split()[1] not in item_value:
                item_value[item.split()[1]] = int(item.split()[0])
                continue
            item_value[item.split()[1]] += int(item.split()[0])        
            
    
    return item_value

def flate_selected_items(selected_items): 
    return [items for card_id in selected_items for items in selected_items[card_id]]

def subtract_selected(grouplist, selected_options, cards_option, cards_value):    
    flatted_items = flate_selected_items(selected_options)
    for selected in flatted_items:
        for i, lst in enumerate(grouplist):
            item_found = False
            for j, item in enumerate(lst): 
                if selected.split()[1] == item.split()[1] and int(selected.split()[0]) <= int(item.split()[0]):
                    item_found = True
                    new_val = int(item.split()[0]) - int(selected.split()[0])
                    if new_val:
                        grouplist[i][j] = f'{new_val} {selected.split()[1]}'
                    else: 
                        # Drop the item 
                        lst.pop(j)
                    break
            if item_found:
                break
    

    grouplist_2 = [lst for lst in grouplist if lst]

    remaining_items = aggr_listgroup_items(grouplist_2)
    for i, (opts, vals) in enumerate(zip(cards_option, cards_value)):
        
        for opt_i, opt in enumerate(opts):
            if opt_i not in vals:
                if int(opt.get('label').split()[0]) > int(remaining_items[opt.get('label').split()[1]]):
                    cards_option[i][opt_i]['disabled'] = True
                else: 
                    cards_option[i][opt_i]['disabled'] = False


    grouplist = [' '.join(lst) for lst in grouplist if lst]
    return grouplist, cards_option

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



def commit_substraction(lst_items, checkboxes_disabled, card_value=None, init=True, display_next_page={'display':'none'}, clicked_idx=None):
    if init:
        lst_items = [[item] for item in lst_items]
        cards = {}
        data = {}
        metadata = {'total': {}}
        for idx, lst in enumerate(lst_items):
            for item in lst:
                new_item = divide_chunks(item.strip().split(), 2)
                for n_i in new_item:
                    if idx not in data:
                        data[idx] = {
                            f'{n_i[1]}': int(n_i[0])
                        }
                    else:
                        data[idx][f'{n_i[1]}'] = int(n_i[0])
                    if n_i[1] not in metadata['total']:
                        metadata['total'][f'{n_i[1]}'] = int(n_i[0])
                    else:
                        metadata['total'][f'{n_i[1]}'] += int(n_i[0])

        metadata['results'] = metadata['total']
        lst_items = {'data': data, 'metadata': metadata, 'cards': cards or {}}

    # Disable/Enable our cards values depends on the left lists/items
    new_options = []
    new_opt_value = []
    for idx1, options in enumerate(checkboxes_disabled):
        opts_list = []
        opts_value = []
        for idx2, option in enumerate(options):
            color = option['label'].split()[1]
            value = option['label'].split()[0]
            stock = lst_items['metadata']['results'].get(color, None)
            if stock and stock >= int(value):
                option['disabled'] = False
                opts_value.append(idx2)
            else:
                option['disabled'] = True
            opts_list.append(option)
        new_options.append(opts_list)

        new_opt_value.append(opts_value)

    lst_items['state_components'] = {
        'pie_page': display_next_page,
        'clicked_idx': clicked_idx,
    }

    return lst_items

  