from app import engine
from flask_login import current_user
import pandas as pd

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
                    user_id
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
                {current_user.id}
            ) ON DUPLICATE KEY UPDATE 
                food.food_totquantity = food.food_totquantity+VALUES(food_totquantity), 
                food.food_available_quantity = food.food_available_quantity+VALUES(food_available_quantity)
        ;
        """)
    conn.close()
    return res

def get_last_card_id():
    con = engine.connect()
    last_id = con.execute(f'''
        SELECT MAX(food_type_id_int)
        FROM food
        WHERE user_id={current_user.id}
    ''' ).fetchone()
    con.close()
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
                        food_available_quantity > 0 AND 
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
                        food_available_quantity > 0 AND 
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
                        food_available_quantity > 0 AND 
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
                WHERE user_id={current_user.id} AND food_available_quantity > 0 
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
    con = engine.connect()
    for i, row in card_val.iterrows():
        # Update food table
        con.execute(f"""
            UPDATE food
            SET 
                food.food_totquantity = food.food_totquantity-{row['totquantity']}, 
                food.food_available_quantity = food.food_available_quantity-{row['available_quantity']}
            WHERE user_id={current_user.id} AND food_type_id_int={row['type_id_int']} AND food_type_id_str={row['type_id_str']}
        """)
        # Insert food to historical sales
        con.execute(f"""
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
    con.close()

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