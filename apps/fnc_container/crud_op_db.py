from app import engine
from flask_login import current_user
import pandas as pd
import json

def ctx2ID(context, current_cards=None):
    context_dict = context[0].get('prop_id', None)
    context_dict = json.loads(context_dict.split('.')[0])
    type_id_str = context_dict['index'].split('_')[-1]
    if len(context_dict['index'].split('_')) > 1:
        type_id_int = context_dict['index'].split('_')[0]
        gang_number = context_dict['index'].split('_')[1]
        return type_id_int, gang_number, type_id_str

    available_cards = current_cards.loc[
        (current_cards['type_id_str'] == type_id_str) &
        (current_cards['selected'] == 0) &
        (current_cards['production'] > 0)
    ]
    if not available_cards.empty:
        type_id_int = available_cards['type_id_int'].values[0]
        gang_number = available_cards['gang_number'].values[0]
        return type_id_int, gang_number, type_id_str
    
    return None, None
    
def on_production(type_id_int):
    conn = engine.connect()
    res = conn.execute(f'''
        INSERT INTO current_production_cards_tmp (
            user_id,
            type_id_int
        ) VALUES (
            {current_user.id},
            {type_id_int}
        ) ON DUPLICATE KEY UPDATE user_id={current_user.id};
    ''')

    # Check the order type (order or re_order)
    re_order = False
    rows = conn.execute(f'''
        SELECT 
            food_type_id_int AS type_id_int, 
            food_type_id_str AS type_id_str,
            food_available_quantity AS available_quantity, 
            food_totquantity AS totquantity,
            order_type
        FROM food
        WHERE user_id={current_user.id} AND food_type_id_int={type_id_int} AND order_type='re_order';
    ''')
    df = pd.DataFrame(rows.fetchall())
    # If re_order than update the old card
    if not df.empty:
        re_order = True
        df.columns = [key for key in rows.keys()]
        for i, row in df.iterrows():
            conn.execute(f"""
                UPDATE food
                SET 
                    food.food_totquantity = food.food_totquantity-{abs(row['totquantity'])}, 
                    food.food_available_quantity = food.food_available_quantity-{abs(row['available_quantity'])}
                WHERE user_id={current_user.id} AND food_type_id_str={row['type_id_str']} AND order_type='order'
            """)
    conn.close()
    return re_order

def get_on_production(): 
    conn = engine.connect()
    q = f'''
        SELECT user_id, type_id_int 
        FROM current_production_cards_tmp 
        WHERE user_id={current_user.id};
    '''
    rows = conn.execute(q)
    selected_items = pd.DataFrame(rows.fetchall())
    if not selected_items.empty:
        selected_items.columns = [key for key in rows.keys()]
        conn.close()
        return selected_items
    return selected_items

def out_production(type_id_int):
    conn = engine.connect()
    res = conn.execute(f'''
        DELETE FROM current_production_cards_tmp 
        WHERE user_id={current_user.id} AND type_id_int={type_id_int};
    ''')
    conn.close()
    return res


def insert_selected_item(context): #, clicked='cardItem', current_cards=None
    conn = engine.connect()
    values = context['index'].split('_')
    res = conn.execute(f'''
        INSERT INTO current_selected_items_tmp (
            user_id,
            type_id_int,
            gang_number,
            type_id_str
        ) VALUES (
            {current_user.id},
            {values[0]},
            {values[1]},
            {values[2]}
        ) ON DUPLICATE KEY UPDATE user_id={current_user.id};
    ''')
    conn.close()
    return res

def insert_selected_items(context):
    conn = engine.connect()
    res = conn.execute(f'''
        INSERT INTO current_selected_items_tmp (
            user_id,
            type_id_int,
            gang_number,
            type_id_str
        ) 
        SELECT user_id, food_type_id_int as type_id_int, food_gang_number as gang_number, food_type_id_str as type_id_str 
        FROM food
        WHERE user_id={current_user.id} AND 
        food_type_id_int={int(context['index'].split('_')[0])} AND 
        food_gang_number={int(context['index'].split('_')[1])}
        ON DUPLICATE KEY UPDATE user_id={current_user.id};
    ''')
    conn.close()
    return res

def delete_selected_item(context):
    conn = engine.connect()
    values = [int(v) for v in context['index'].split('_')]
    res = conn.execute(f'''
        DELETE FROM current_selected_items_tmp 
        WHERE 
            user_id = {current_user.id} AND 
            type_id_int={values[0]} AND 
            gang_number={values[1]} AND
            type_id_str={values[2]};
    ''')
    conn.close()
    return res

def delete_selected_items(selected_items):
    conn = engine.connect()
    for i, row in selected_items.iterrows():
        res = conn.execute(f'''
            DELETE FROM current_selected_items_tmp 
            WHERE 
                user_id = {current_user.id} AND 
                type_id_int={row['type_id_int']} AND 
                type_id_str={row['type_id_str']};
        ''')
    conn.close()
    return res

def delete_selected_items_gang(context):
    conn = engine.connect()
    res = conn.execute(f'''
        DELETE FROM current_selected_items_tmp 
        WHERE 
            user_id = {current_user.id} AND 
            type_id_int={int(context['index'].split('_')[0])} AND 
            gang_number={int(context['index'].split('_')[1])};
    ''')
    conn.close()
    return res


def get_selected_items(type_id_int=None):
    conn = engine.connect()
    if type_id_int is not None: 
        q = f'''
            SELECT * 
            FROM current_selected_items_tmp 
            WHERE user_id={current_user.id} AND type_id_int={type_id_int};
        '''
    else: 
        q = f'''
            SELECT * 
            FROM current_selected_items_tmp 
            WHERE user_id={current_user.id};
        '''
    rows = conn.execute(q)
    selected_items = pd.DataFrame(rows.fetchall())
    if not selected_items.empty:
        selected_items.columns = [key for key in rows.keys()]
        conn.close()
        return selected_items
    return selected_items

def update_printers_folder_path(folderPath):
    conn = engine.connect()
    x = '\\'
    x2 = '\\\\'
    newFolderPath = folderPath.replace("/", "//").replace(x, x2)
    res = conn.execute(f'''
        INSERT INTO account_configs (
            user_id,
            orders_folderPath
        ) VALUES (
            {current_user.id},
            '{newFolderPath}'
        ) ON DUPLICATE KEY UPDATE orders_folderPath='{newFolderPath}';
    ''')
    conn.close()
    return res

def get_printer_folder_path():
    conn = engine.connect()
    result = conn.execute(f'''
        SELECT orders_folderPath as folderPath, lastFileTimestamp as lastFileTs
        FROM account_configs
        WHERE user_id={current_user.id}
    ''' ).fetchone()
    conn.close()
    return result

def update_lastFileTs(ts):
    conn = engine.connect()
    res = conn.execute(f'''
        UPDATE account_configs 
        SET lastFileTimestamp = '{ts}'
        WHERE user_id={current_user.id}
    ''')
    conn.close()
    return res 

def update_foods(df):
    conn = engine.connect()
    for i, row in df.iterrows():
        res = conn.execute(f"""
            INSERT INTO food 
                (
                    food_bonus, 
                    food_bonus_sep, 
                    food_card_date,
                    food_card_datetime, 
                    food_card_time,
                    food_gang_id, 
                    food_gang_number, 
                    food_gang_title,
                    food_price, 
                    food_totquantity, 
                    food_available_quantity,
                    food_process,
                    food_station,
                    food_table,
                    food_type,
                    food_type_id_int,
                    food_type_id_str,
                    food_type_only,
                    food_waitress,
                    food_opt_id,
                    user_id, 
                    order_type
                ) 
            VALUES (
                '{row["bonus"]}',
                '{row["bonus_separtor"]}',
                '{row["card_date"]}',
                '{row["card_datetime"]}', 
                '{row["card_time"]}',
                '{row["gang_id"]}',
                '{row["gang_number"]}',
                '{row["gang_title"]}',
                '{row["price"]}',
                '{row["available_quantity"]}',
                '{row["available_quantity"]}',
                '{row["process"]}',
                '{row["station"]}',
                '{row["table"]}',
                '{row["type"].strip()}',
                '{row["type_id_int"]}',
                '{row["type_id_str"]}',
                '{row["type_only"]}',
                '{row["waitress"]}',
                '{row["opt_id"]}',
                {current_user.id}, 
                '{row["order_type"]}'
            ) ON DUPLICATE KEY UPDATE 
                food.food_totquantity = food.food_totquantity+VALUES(food_totquantity), 
                food.food_available_quantity = food.food_available_quantity+VALUES(food_available_quantity)
        ;
        """)
    conn.close()
    return res

def get_last_card_id():
    conn = engine.connect()
    last_id = conn.execute(f'''
        SELECT MAX(food_type_id_int)
        FROM food
        WHERE user_id={current_user.id}
    ''' ).fetchone()
    conn.close()
    if last_id[0]: 
        return last_id[0]+1
    return 0

def read_food_cards(show_all=False, id_int=None, next=True): 
    if id_int: 
        if next: 
            q = f"""
                SELECT * FROM food
                INNER JOIN (
                    SELECT DISTINCT food_type_id_int AS id_int
                    FROM food 
                    WHERE user_id={current_user.id} AND
                        food_available_quantity != 0 AND 
                        food_type_id_int > {id_int}
                    ORDER BY food_type_id_int ASC
                    LIMIT 10
                ) AS card_ids 
                ON food.food_type_id_int = card_ids.id_int
                WHERE user_id={current_user.id}
                ORDER BY food_type_id_int ASC
            """
        else: 
            q = f"""
                SELECT * FROM food
                INNER JOIN (
                    SELECT DISTINCT food_type_id_int AS id_int
                    FROM food 
                    WHERE user_id={current_user.id} AND
                        food_available_quantity != 0 AND 
                        food_type_id_int <= {id_int}
                    ORDER BY food_type_id_int DESC
                    LIMIT 10
                ) AS card_ids 
                ON food.food_type_id_int = card_ids.id_int
                WHERE user_id={current_user.id}
                ORDER BY food_type_id_int ASC
            """
    else: 
        if not show_all: 
            q = f"""
                SELECT * FROM food
                INNER JOIN (
                    SELECT DISTINCT food_type_id_int AS id_int
                    FROM food 
                    WHERE user_id={current_user.id} AND
                        food_available_quantity != 0 AND 
                        food_type_id_int >=0
                    ORDER BY food_type_id_int ASC
                    LIMIT 10
                ) AS card_ids 
                ON food.food_type_id_int = card_ids.id_int
                WHERE user_id={current_user.id}
                ORDER BY food_type_id_int ASC
            """
        else: 
            q = f"""
                SELECT * FROM food
                WHERE user_id={current_user.id} AND food_available_quantity != 0 
                ORDER BY food_type_id_int ASC
            """
    # Fetch data
    conn = engine.connect()
    rows = conn.execute(q)
    conn.close()
    cards_df = pd.DataFrame(rows.fetchall())
    if not cards_df.empty: 
        cards_df.columns = [key.replace('food_', '') for key in rows.keys()]
    cards_df['selected'] = 0
    return cards_df

# Test 1: 
def update_production(card):
    conn = engine.connect()
    for i, row in card: 
        conn.execute(f"""
            UPDATE food
            SET food_production = {row['available_quantity']}
            WHERE 
                food_type_id_int = {row['type_id_int']} AND
                food_type_id_str = {row['type_id_str']} AND
                user_id = {current_user.id}
        """) 
    conn.close()

def update_vals(card_val): 
    conn = engine.connect()
    for i, row in card_val.iterrows():
        # Update food table
        conn.execute(f"""
            UPDATE food
            SET 
                food.food_totquantity = food.food_totquantity-{row['totquantity']}, 
                food.food_available_quantity = food.food_available_quantity-{row['available_quantity']}
            WHERE user_id={current_user.id} AND food_type_id_int={row['type_id_int']} AND food_type_id_str={row['type_id_str']}
        """)
        # Insert food to historical sales
        conn.execute(f"""
            INSERT INTO historical_sales
            (
                food_food_id, 
                food_user_id, 
                sales_price,
                sales_quantity
            ) VALUES (
                {row['id']}, 
                {current_user.id}, 
                {row['price']}, 
                {row['available_quantity']}
            )
        """)
    conn.close()

    # update historical_sales table

def update_filter_options(table):
    q = f"""
        SELECT * FROM {table} 
        WHERE user_id={current_user.id} AND food_available_quantity > 0
    """ 
    conn = engine.connect()
    rows = conn.execute(q)
    conn.close()
    data = pd.DataFrame(rows.fetchall()) 
    if not data.empty:
        data.columns = [key.replace('food_', '') for key in rows.keys()]
        data['selected'] = 0
        return data
    return None

def init_cards_tracer(): 
    q = f"""
        SELECT
            food_type_id_int, food_type_id_str, food_available_quantity, food_production, food_gang_number
        FROM food
        WHERE user_id={current_user.id} AND food_available_quantity > 0
    """ 
    conn = engine.connect()
    rows = conn.execute(q)
    conn.close()
    data = pd.DataFrame(rows.fetchall()) 
    if not data.empty:
        data.columns = [key.replace('food_', '') for key in rows.keys()]
        data['selected'] = 0
        return data.to_dict('records')
    return None

# Query for dashboard: 
def historical(): 
    q = f"""
        SELECT 
            sales_created, 
            sales_price AS price, 
            sales_quantity AS available_quantity,
            food_bonus,
            food_card_date, 
            food_card_datetime, 
            food_gang_number, 
            food_process, 
            food_station, 
            food_table, 
            food_type, 
            food_type_id_int, 
            food_type_id_str, 
            food_type_only,
            food_waitress, 
            food_opt_id
        FROM historical_sales as hs
        INNER JOIN food as f ON hs.food_food_id = f.food_id
        WHERE food_user_id = {current_user.id}
        ORDER BY sales_created DESC
    """
    conn = engine.connect()
    rows = conn.execute(q)
    conn.close()
    data = pd.DataFrame(rows.fetchall()) 
    if not data.empty:
        data.columns = [key.replace('food_', '')  for key in rows.keys()]
        data['available_quantity'] = data['available_quantity'].astype(int)
        data['table'] = data['table'].map(lambda x: 0 if x=='' else int(float(x)))
        return data.to_dict('records')
    
    return None