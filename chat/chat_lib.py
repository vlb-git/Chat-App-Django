import sqlite3
from datetime import datetime
import users_lib as Users

#MongoDB Version
from pymongo import MongoClient
from bson import ObjectId
import os
import dotenv
import threading

update_lock = threading.Lock()

class Chat:
    client = None
    def __init__(self, chatType, chatName = "", currentUser="", otherUser="", mongodbClient = None):
        if not mongodbClient:
            dotenv.load_dotenv()
            self.MONGO_URI = os.environ["MONGO_URI"]
            self.client = MongoClient(self.MONGO_URI)
        else:
            self.client = mongodbClient
        self.db = self.client["Chat-App-DB"]
        self.chat = self.db["dms"]
        self.chatrooms = self.db["chatrooms"]
        self.chatgroups = self.db["chatgroups"]

        self.chatType = chatType
        self.chatName = chatName
        self.currentUser = currentUser
        self.otherUser = otherUser

        self.users_table=""

        if chatType=="chatroom":
            self.chat = self.db["chatrooms"]
            self.createChatTable(chatName+"_chatroom", type="chatroom")
            self.message_table=chatName+"_chatroom"
        elif chatType=="chatgroup":
            self.chat = self.db["chatgroups"]
            self.createChatTable(chatName+"_chatgroup_messages", type="chatgroup")

            self.message_table=chatName+"_chatgroup_messages"
            self.users_table=chatName+"_chatgroup_users"

        elif chatType=="dm":
            self.chat = self.db["dms"]
            self.createChatTable(self.generateDMName(currentUser, otherUser), type="dm")
            self.message_table=self.generateDMName(currentUser, otherUser)

    def generateDMName(self, user1, user2):
        users = Users.Users()
        user_1 = users.findUser(user1)["username"]
        user_2 = users.findUser(user2)["username"]
        if user_1>user_2:
            return f"dm_{user_1}_{user_2}"
        else:
            return f"dm_{user_2}_{user_1}"

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
    def createChatTable(self, tableName, type=""):
        document={
                "name": f"{tableName}", 
                "messages": [],
                "message_count":0
            }
        if type=="chatgroup":
            document["users"] = []
        if not self.chat.find_one({"name":f"{tableName}"}):
            self.chat.insert_one(document)
    
    def recordMessage(self, text, replying_to="root", attachment="", date="", time=""):
        '''self.executeSQL(f"""INSERT INTO {self.message_table} (username, message_text, replying_to, attachments, date, time) 
                        VALUES (?, ?, ?, ?, ?, ?);""", 
                        extraValues=(self.currentUser, text, replying_to, attachment, 
                                     datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%I:%M %p")))
        '''
        
        chat = self.chat.find_one({"name": self.message_table})
        if not chat:
            print(f"{self.message_table} Chat not found")
            return
        chat["message_count"]+=1

        message = {
            "message_id": chat["message_count"],
            "username": self.currentUser,
            "message_text": text,
            "replying_to": replying_to,
            "attachments": attachment,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%I:%M %p")
        }

        self.chat.update_one(
            {"name": self.message_table}, 
            {"$push": {"messages": message}}
        )
        self.chat.update_one(
            {"name": self.message_table},
            {"$set": {"message_count": chat["message_count"]}}
        )
        
    def deleteMessage(self, message_id):
        #self.execute(f"DELETE FROM {self.message_table} WHERE message_id = ?", extraValues=(message_id,))

        self.chat.update_one(
            {"name": self.message_table}, 
            {"$pull": {"messages": {"message_id": message_id}}}
        )

    def fetchAllMessages(self):
        #return self.executeSQL(f"SELECT * FROM {self.message_table}", fetch=True)
        document = self.chat.find_one({"name": self.message_table})

        return_messages = []

        if document and "messages" in document:
            for i in range(len(document["messages"])):
                message = []
                #message.append(str(document["messages"][i]['_id']))
                message.append(document["messages"][i]['message_id'])
                message.append(document["messages"][i]['username'])
                message.append(document["messages"][i]['message_text'])
                message.append(document["messages"][i]['replying_to'])
                message.append(document["messages"][i]['attachments'])
                message.append(document["messages"][i]['date'])
                message.append(document["messages"][i]['time'])
                return_messages.append(message)
        return return_messages
    
    def fetchMessageUpdates(self, Final):
        #return self.executeSQL(f"SELECT * FROM {self.message_table} WHERE message_id >= ?", extraValues=(Final,), fetch=True)
        with update_lock:
            messages = self.fetchAllMessages()
            return_messages = []
            
            for m in messages:
                if m[0]>=Final:
                    return_messages.append(m)
            return return_messages

    '''def addUser(self, username, status=""):
        self.executeSQL(f"""INSERT INTO {self.user_table} (username, status) 
                        VALUES (?, ?);""", extraValues=(username, status))'''
    
    '''def removeUser(self, username):
        self.execute(f"DELETE FROM {self.users_table} WHERE username = ?", extraValues=(username,))'''
    
    '''def fetchAllUsers(self):
        return self.executeSQL(f"SELECT * FROM {self.users_table}", fetch=True)'''
    
    def getDMName(self):
        return self.generateDMName(self.currentUser, self.otherUser)