import sqlite3
import hashlib

#MongoDB Version
from pymongo import MongoClient
import os
import dotenv

class Users():
    client = None
    def __init__(self, mongodbClient = None):
        if not mongodbClient:
            dotenv.load_dotenv()
            self.MONGO_URI = os.environ["MONGO_URI"]
            self.client = MongoClient(self.MONGO_URI)
        else:
            self.client = mongodbClient
        self.db = self.client["Chat-App-DB"]
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

