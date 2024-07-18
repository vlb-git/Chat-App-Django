import sqlite3
from datetime import datetime
import users_lib as Users

class Chat:
    def __init__(self, chatType, chatName = "", currentUser="", otherUser=""):
        self.chatType = chatType
        self.chatName = chatName
        self.currentUser = currentUser
        self.otherUser = otherUser

        self.users_table=""

        if chatType=="chatroom":
            self.createChatTable(chatName+"_chatroom")
            self.message_table=chatName+"_chatroom"
        elif chatType=="chatgroup":
            self.createChatTable(chatName+"_chatgroup_messages")
            self.createUserTable(chatName+"_chatgroup_users")

            self.message_table=chatName+"_chatgroup_messages"
            self.users_table=chatName+"_chatgroup_users"

        elif chatType=="dm":
            self.createChatTable(self.generateDMName(currentUser, otherUser))
            self.message_table=self.generateDMName(currentUser, otherUser)

    def generateDMName(self, user1, user2):
        users = Users.Users()
        user_1 = users.findUser(user1)[0][0]
        user_2 = users.findUser(user2)[0][0]
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
    def createChatTable(self, tableName):
        self.executeSQL(f"""CREATE TABLE IF NOT EXISTS {tableName} (
                        message_id INTEGER NOT NULL PRIMARY KEY,
                        username TEXT NOT NULL,
                        message_text TEXT,
                        replying_to TEXT,
                        attachments TEXT,
                        date TEXT,
                        time TEXT
                        );""")
    
    def createUserTable(self, tableName):
        self.executeSQL(f"""CREATE TABLE IF NOT EXISTS {tableName} (
                        username PRIMARY KEY,
                        status TEXT
                        );""")
    
    def recordMessage(self, text, replying_to="root", attachment="", date="", time=""):
        self.executeSQL(f"""INSERT INTO {self.message_table} (username, message_text, replying_to, attachments, date, time) 
                        VALUES (?, ?, ?, ?, ?, ?);""", 
                        extraValues=(self.currentUser, text, replying_to, attachment, 
                                     datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%I:%M %p")))
        
    def deleteMessage(self, message_id):
        self.execute(f"DELETE FROM {self.message_table} WHERE message_id = ?", extraValues=(message_id,))
    
    def fetchAllMessages(self):
        return self.executeSQL(f"SELECT * FROM {self.message_table}", fetch=True)
    
    def fetchMessageUpdates(self, Final):
        return self.executeSQL(f"SELECT * FROM {self.message_table} WHERE message_id >= ?", extraValues=(Final,), fetch=True)

    def addUser(self, username, status=""):
        self.executeSQL(f"""INSERT INTO {self.user_table} (username, status) 
                        VALUES (?, ?);""", extraValues=(username, status))
        
    def removeUser(self, username):
        self.execute(f"DELETE FROM {self.users_table} WHERE username = ?", extraValues=(username,))
    
    def fetchAllUsers(self):
        return self.executeSQL(f"SELECT * FROM {self.users_table}", fetch=True)
    
    def getDMName(self):
        return self.generateDMName(self.currentUser, self.otherUser)
    