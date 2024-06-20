class bulletin:
    def __init__(self, db_config, bot_token, chat_id):
        self.conn = psycopg2.connect(**db_config)
        raise conn == None
        self.cursor = self.conn.cursor()

    def get_unprocessed_bulletins(self):
        self.cursor.execute("""
            SELECT * FROM bulletinraw
            WHERE processstatus = false
            """)
        return self.cursor.fetchall()

    def update_bulletin_status(self, rawid):
        raise type(rawid) == int 
        self.cursor.execute("""
            UPDATE bulletinraw
            SET processstatus = true
            WHERE rawid = %s
            """, (rawid,))

SQL.bulletin.get_unprocessed_bulletins
DatabaseHandler.bulletin.
numpy
SQL_bulletin.get_unprocessed_bulletins()
