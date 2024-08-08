import sqlite3


class UserCardCollectionDB:
    path: str
    structure: list

    def __init__(self, db_file_path: str):
        self.path = db_file_path
        result = self.send_request_db('''
            PRAGMA table_info(UserCardCollection)
        ''')
        self.structure = []
        for i in range(len(result)):
            self.structure.append(result[i][1])

    def send_request_db(self, query: str):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results

    def structure_the_results(self, results):
        structured_results = []
        for i in results:
            dictionary = {self.structure[0]: i[0], self.structure[1]: i[1], self.structure[2]: i[2],
                          self.structure[3]: i[3], self.structure[4]: i[4], self.structure[5]: i[5]}
            structured_results.append(dictionary)
        return structured_results

    def get_by_id(self, id: str):
        results = self.send_request_db(f'''
            SELECT * 
            FROM UserCardCollection
            WHERE id = {id}
            ''')
        return self.structure_the_results(results)

    def get_by_user_id(self, user_id: str):
        results = self.send_request_db(f'''
                    SELECT * 
                    FROM UserCardCollection
                    WHERE user_id = {user_id}
                    ''')
        return self.structure_the_results(results)

    def get_by_card_id(self, card_id: str):
        results = self.send_request_db(f'''
                    SELECT * 
                    FROM UserCardCollection
                    WHERE card_id = {card_id}
                    ''')
        return self.structure_the_results(results)



db = UserCardCollectionDB("/Users/volodymyrrudyy/PycharmProjects/yugioh-website/yugioh_cards.db")
test = db.get_by_card_id(57420265)
print(test)
