from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader

import users_lib as Users
import html


def login_page(request):
    message = request.GET.get('m','')
    template = loader.get_template('login.html.j2')
    return HttpResponse(template.render({'message': message}, request))

def signup_page(request):
    message = request.GET.get('m','')
    template = loader.get_template('signup.html.j2')
    return HttpResponse(template.render({'message': message}, request))

def signup_entry(request):
    if request.method=="POST":
        user_object = Users.Users()
        username = request.POST["username"]
        if user_object.findUser(username):
            return redirect("/users/signup?m=That name is already taken")
        email = request.POST["email"]
        dob = request.POST["dob"]
        user_object.createUser(username, email, request.POST["passwd"], dob)

        print(request.POST)
    return redirect("/users/login/")

def login_entry(request):
    users = Users.Users()
    if (request.method=="POST"):
        username = request.POST["username"]
        result = users.verifyUser(username, request.POST["passwd"])
        if result:
            request.session["user"] = users.findUser(username)[0][:3] + users.findUser(username)[0][4:]
            return redirect("/users/dashboard/")
        else:
            return redirect("/users/login?m=username or password is incorrect")
            return HttpResponse("username or password is incorrect.")

def logout(request):
    request.session.pop("user")
    print(request.session)
    return redirect("/users/login/")

def dashboard(request):
    if "user" in request.session:
        return render(request, 'dashboard.html.j2', locals())
    else:
        return redirect("/users/login")
        #return HttpResponse("Please log in first!")
    
def users_page(request):
    users = Users.Users()
    usersList = users.fetchAllUsers()
    if "user" in request.session:
        template = loader.get_template('users.html.j2')
        context = {
            "usersList" : usersList,
            "currentUser": request.session["user"][1]
        }
        return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template('users.loginfirst.html.j2')
        return HttpResponse(template.render({}, request))
