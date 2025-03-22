from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader

import json

import users_lib as Users
from . import chat_lib as Chat

def index(request, test_str):
    chat = Chat.Chat("dm", currentUser=request.session["user"][1], otherUser= test_str)

    messages = chat.fetchMessageUpdates(24)
    return HttpResponse(str([list(m) for m in messages]).replace("\'", "\""))

def chatwith_page(request, username):
    users = Users.Users()
    if "user" not in request.session:
        return HttpResponse("please log in first!")
    if not users.findUser(username):
        return HttpResponse("There is no user with this name! :(")
    chat = Chat.Chat("dm", currentUser=request.session["user"][1], otherUser=username)
    template = loader.get_template('direct_message_chat.html.j2')
    messages = chat.fetchAllMessages(),
    if len(messages[0])>0:
        finalMessage = messages[0][-1][0]
        print(messages[0][-1])
    else:
        finalMessage = 0
    context = {
            "otherUser" : username,
            "currentUser" : request.session["user"][1],
            "messages" : messages,
            "finalMessage" : finalMessage,
        }
    return HttpResponse(template.render(context, request))
    return HttpResponse("chat With")

def chat_with_send(request, username):
    users = Users.Users()
    print("sent")
    print(request.body)
    if not users.findUser(username):
        return HttpResponse("There is no user with this name! :(")
    if request.method=="POST":
        print("POST Request Content:")
        print(request.POST)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponse("invalid data received")
        chat = Chat.Chat("dm", currentUser=request.session["user"][1], otherUser=username)

        #recordDict = json.loads(request.body)["message"]

        recordDict = data["message"]
        chat.recordMessage(recordDict)
        print(data)
        return redirect(f"/chat/chatwith/{username}/")
    return HttpResponse(f"chatwith {username}")

def chat_with_update(request, username):
    users = Users.Users()
    if not users.findUser(username):
        return HttpResponse("Failed to locate user with that name")
    if request.method=="POST":
        chat = Chat.Chat("dm", currentUser=request.session["user"][1], otherUser=username)
        
        messages = chat.fetchMessageUpdates(int(json.loads(request.body)["final"]))
        return HttpResponse(str([list(m) for m in messages]).replace("\'", "\""))
    return HttpResponse(f"chatwith update {username} failed!")

def chatroom_page(request, chatroom_name):
    return HttpResponse(f"chatroom {chatroom_name}")

def chatgroup_page(request, chatgroup_name):
    return HttpResponse(f"chatgroup {chatgroup_name}")
