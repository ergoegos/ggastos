import psycopg2
from psycopg2.extras import DictCursor
import json
import pandas as pd

class Database():

    def __init__(self) -> None:
        self.conn = None
        self.conn = None


    def set_connection(self):
        self.conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="admin")
        self.cursor = self.conn.cursor(cursor_factory=DictCursor)



    def __enter__(self):
        self.set_connection()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()



    def insert_user(self, user, data):
        self.cursor.execute("INSERT INTO customer (username, email, full_name, password_hash) VALUES (%s, %s, %s, %s)", (user, data["email"], data["name"], data["password"]))
        self.conn.commit()


    def get_credentials(self):
        self.cursor.execute(f"SELECT username, username, full_name, password_hash FROM customer;")
        data = self.cursor.fetchall()
        credentials={}
        credentials["usernames"]={}
        
        for user in data:
            credentials["usernames"][user[0]] = {"username": user[1], "name": user[2], "password": user[3]}
        try:
            return credentials
        except:
            return None
        

    def insert_sheet_id(self, username, sheet_id):
        self.cursor.execute("UPDATE customer SET sheet_id = %s WHERE username = %s;", (sheet_id, username))
        self.conn.commit()

        

    def check_credentials(self, username):
        self.cursor.execute(f"SELECT credentials, sheet_id FROM customer WHERE username = '{username}';")
        data = self.cursor.fetchall()
        return data[0][0], data[0][1]

    def update_credentials(self, username:str, credentials):
        self.cursor.execute("UPDATE customer SET credentials = %s WHERE username = %s;", (json.dumps(credentials), username))
        self.conn.commit()

    def insert_credentials(self, username:str, credentials):
        self.cursor.execute(
    "INSERT INTO customer (username, credentials) VALUES (%s, %s)",
    (username, json.dumps(credentials)))
        self.conn.commit()




    def insert_fields(self, data, username, dimension, month):

        if dimension == "expense_projection":
            self.cursor.execute(f"DELETE FROM {dimension} WHERE username = '{username}' and month_id = '{month}'")
            for row in data:
                self.cursor.execute(
                "INSERT INTO expense_projection (username, concept, amount, month_id) VALUES (%s, %s, %s, %s)", tuple(row))
            self.conn.commit()


        if dimension == "income_projection":
            self.cursor.execute(f"DELETE FROM {dimension} WHERE username = '{username}' and month_id = '{month}'")
            for row in data:
                self.cursor.execute(
                "INSERT INTO income_projection (username, concept, amount, month_id) VALUES (%s, %s, %s, %s)", tuple(row))
            self.conn.commit()


        if dimension == "expense":
            self.cursor.execute(f"DELETE FROM {dimension} WHERE username = '{username}' and month_id = '{month}'")
            for row in data:
                self.cursor.execute(
                "INSERT INTO expense (username, concept, amount, subconcept,  month_id) VALUES (%s, %s, %s, %s, %s)", tuple(row))
            self.conn.commit()
            

        if dimension == "income":
            self.cursor.execute(f"DELETE FROM {dimension} WHERE username = '{username}' and month_id = '{month}'")
            for row in data:
                self.cursor.execute(
                "INSERT INTO income (username, concept, amount, subconcept,  month_id) VALUES (%s, %s, %s, %s, %s)", tuple(row))
            self.conn.commit()


        if dimension == "saving_projection":
            self.cursor.execute(f"DELETE FROM {dimension} WHERE username = '{username}' and month_id = '{month}'")
            print(data)
            for row in data:
                self.cursor.execute(
                "INSERT INTO saving_projection (username, amount, month_id) VALUES (%s, %s, %s)", tuple(row))
            self.conn.commit()


        

    def get_table(self, table, username):

        query = f"SELECT * FROM {table} WHERE username = '{username}'"
        df  = pd.read_sql(query, self.conn)
        return df 
    

    def query_table(self, query):
        df  = pd.read_sql(query, self.conn)
        return df 





