import sqlite3

connection = sqlite3.connect('app.db')

cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS user (
        id INT AUTO_INCREMENT,
        user_fname VARCHAR(45) NOT NULL,
        user_lname VARCHAR(45) NOT NULL,
        user_email VARCHAR(45) NOT NULL UNIQUE,
        user_phone VARCHAR(45) NULL,
        user_password TEXT NOT NULL,
        user_created DATETIME NOT NULL,
        user_modified DATETIME NOT NULL,
        PRIMARY KEY (id),
        UNIQUE(user_email))
    """
)

# print('create company')

# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS company (
#         company_id INT AUTO_INCREMENT,
#         company_name VARCHAR(100) NOT NULL,
#         company_ceo_name VARCHAR(45) NULL,
#         user_id INT NOT NULL,
#         PRIMARY KEY (company_id, user_id),
#         UNIQUE(company_name),
#         CONSTRAINT fk_company_user1
#             FOREIGN KEY (user_id)
#             REFERENCES user (id)
#             ON DELETE CASCADE
#             ON UPDATE CASCADE)
# """)


print('create restaurant')
cursor.execute("""
    CREATE TABLE IF NOT EXISTS restaurant (
        restaurant_id INT AUTO_INCREMENT,
        restaurant_name VARCHAR(45) NULL,
        restaurant_addr_street VARCHAR(255) NULL,
        restaurant_addr_zip_code VARCHAR(30) NOT NULL,
        restaurant_addr_zip_type VARCHAR(20) NOT NULL,
        restaurant_addr_country VARCHAR(45) NOT NULL,
        restaurant_created DATETIME NOT NULL,
        restaurant_modified DATETIME NOT NULL,
        user_id INT NOT NULL,
        PRIMARY KEY (restaurant_id, user_id),
        CONSTRAINT fk_restaurant_user
            FOREIGN KEY (user_id)
            REFERENCES user (id)
            ON DELETE CASCADE
            ON UPDATE CASCADE)
""")


connection.commit()