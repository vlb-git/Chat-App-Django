import sqlite3
import hashlib

# SQLite Version
'''
class Users():
    def __init__(self):
        self.createTable()

    def createTable(self):
        self.executeSQL("""CREATE TABLE IF NOT EXISTS users (
                        userId INTEGER NOT NULL PRIMARY KEY,
                        username TEXT NOT NULL UNIQUE,
                        email TEXT,
                        password TEXT,
                        dateOfBirth TEXT
                        );""")

    def executeSQL(self,sql, extraValues=(), fetch=False):
        conn=sqlite3.connect("data.db")
        rows=None
        if not fetch:
            if not extraValues:
                conn.execute(sql)
            else:
                conn.execute(sql,extraValues)
            conn.commit()
            
        else:
            cur = conn.cursor()
            if not extraValues:
                cur.execute(sql)
            else:
                cur.execute(sql,extraValues)
            rows = cur.fetchall()
        conn.close()
        return rows
    
    def createUser(self, username, email, password, dob):
        self.executeSQL("INSERT INTO users (username, email, password, dateOfBirth) VALUES (?, ?, ?, ?);"
                        , extraValues=(username, email, self.encrypt(password), dob))

    def deleteUser(self, userId):
        self.executeSQL("DELETE FROM users WHERE userId=?;", extraValues=(userId,))

    def fetchUser(self, userId):
        return self.executeSQL("SELECT * FROM users WHERE userId=?",(userId,), fetch=True)
    
    def fetchAllUsers(self):
        return self.executeSQL("SELECT * FROM users", fetch=True)
    
    def findUser(self, username):
        return self.executeSQL("SELECT * FROM users WHERE username=?",(username,), fetch=True)

    def editUserField(self, userId, field, value):
        self.executeSQL(f"UPDATE users SET {field}=? WHERE userId=?;", ( value, userId,))

    def editUser(self, userId, fields, values):
        errorList = []
        for f in range(len(fields)):
            try:
                self.editUserField(userId, fields[f], values[f])
            except:
                errorList.append(fields[f])
    def verifyUser(self, username, password):
        userInfo = self.findUser(username)
        if not userInfo:
            return False
        print(userInfo[0][3])
        if not self.checkPassword(password, userInfo[0][3]):
            return False
        return True
    def checkPassword(self, password, hashPass):# changed for encryption
        if self.encrypt(password) == hashPass:
            return True
        else:
            return False
    def encrypt(self, password):# changed for encryption
        hash_object = hashlib.sha256()
        # Convert the password to bytes and hash it
        hash_object.update(password.encode())
        # Get the hex digest of the hash
        hash_password = hash_object.hexdigest()
        return hash_password
'''

#MongoDB Version
from pymongo import MongoClient
import os
import dotenv

class Users():
    def __init__(self):
        dotenv.load_dotenv()
        self.MONGO_URI = os.environ["MONGO_URI"]
        client = MongoClient(self.MONGO_URI)
        self.db = client["Chat-App-DB"]
        self.users = self.db["users"]

    def createUser(self, username, email, password, dob):
        document = {
            "username": username,
            "email": email,
            "password": self.encrypt(password),
            "dateOfBirth": dob
        }
        self.users.insert_one(document)

    def deleteUser(self, userId):
        self.users.delete_one({"_id": userId})

    def fetchUser(self, userId):
        user = self.users.find_one({"_id": userId})
        if user:
            return {
                "userId": user["_id"],
                "username": user["username"],
                "email": user["email"],
                "dateOfBirth": user["dateOfBirth"]
            }
        return None

    def fetchAllUsers(self):
        users = self.users.find()
        return [
            [
                user["_id"],
                user["username"],
                user["email"],
                user["dateOfBirth"]
            ] for user in users
        ]

    def findUser(self, username):
        user = self.users.find_one({"username": username})
        if user: 
            return {
                "userId": str(user["_id"]),
                "username": user["username"],
                "email": user["email"],
                "password":user["password"],
                "dateOfBirth": user["dateOfBirth"]
            }
        return None

    def editUserField(self, userId, field, value):
        update_result = self.users.update_one({"_id": userId}, {"$set": {field: value}})
        return update_result.modified_count

    def editUser(self, userId, fields, values):
        errorList = []
        for f in range(len(fields)):
            try:
                self.editUserField(userId, fields[f], values[f])
            except Exception:
                errorList.append(fields[f])
        return errorList

    def verifyUser(self, username, password):
        user = self.findUser(username)
        print(user)
        if not user:
            return False
        if not self.checkPassword(password, user["password"]):
            return False
        return True

    def checkPassword(self, password, hashPass):
        return self.encrypt(password) == hashPass

    def encrypt(self, password):
        hash_object = hashlib.sha256()
        hash_object.update(password.encode())
        return hash_object.hexdigest()

