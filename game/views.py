from django.shortcuts import render, redirect
from django.http import HttpResponse

import random

card_classes = ["S", "C", "H", "D"]
cards = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

all_user_objects = []
curr_id = 0

user_object = {
    "name": str,
    "money": int,
    "cards": list,
    "thread": object
}


names = ["Prasun", "Prachi", "Achyut", "Shanta", "Ram", "Shyam", "hari"]

usernames = []


def home(request):
    if request.method == "POST":
        print("POST")
        print(request.POST["csrfmiddlewaretoken"])
        username = request.POST["username"]
        if username in usernames:
            return redirect("/")
        else:
            usernames.append(username)
            user_object['name'] = username
            user_object["money"] = 100
            all_user_objects.append(user_object.copy())
            return render(request, "index.html", context={"user_object": user_object})

    elif request.method == "GET":
        print("GET")
        return render(request, "websoc.html")


def get_user_cards():
    user_cards = []
    for _ in range(3):
        card = random.choice(card_classes) + random.choice(cards)
        user_cards.append(card)
    return user_cards


def validate_usernames(request):
    if request.method == "POST":
        username = request.POST["username"]
        if username in usernames:
            return HttpResponse(False)
        else:
            usernames.append(request.POST["username"])
            return HttpResponse(False)

    else:
        redirect("")
