import mysql.connector

class RecommendationList():
    def __init__(self):
        self.mydb = self.connectToDatabase()

    def connectToDatabase(self):
        return mysql.connector.connect(
            host="154.64.252.69",
            user="root",
            password="csci321fyp",
            database="csci321",
            auth_plugin='mysql_native_password'
        )

    def fetchOne(self, sql, val) -> dict:
        with self.mydb.cursor(dictionary=True) as cursor:
            cursor.execute(sql, val)
            result = cursor.fetchone()
        return result

    def fetchAll(self, sql, val) -> list:
        with self.mydb.cursor(dictionary=True) as cursor:
            cursor.execute(sql, val)
            result = cursor.fetchall()
        return result

    def commit(self, sql, val):
        with self.mydb.cursor() as cursor:
            cursor.execute(sql, val)
            self.mydb.commit()

    def __del__(self):
        if self.mydb.is_connected():
            self.mydb.close()

    def get_recommendations_by_id(self, accountId) -> list:
        sql = "SELECT recommendedStock FROM recommendationList WHERE accountId = %s"
        val = (accountId,)
        return self.fetchOne(sql, val)

    def insert_recommendation_by_accountId(self, accountId, recommendedStock):
        sql = "INSERT INTO recommendationList (accountId, recommendedStock) VALUES (%s, %s)"
        val = (accountId, recommendedStock)
        self.commit(sql, val)

    def update_recommendation_by_accountId(self, accountId, recommendedStock):
        sql = "UPDATE recommendationList SET recommendedStock = %s WHERE accountId = %s"
        val = (recommendedStock, accountId)
        self.commit(sql, val)
