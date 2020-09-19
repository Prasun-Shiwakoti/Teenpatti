bidAmount = 10
bidIncreaseLimit = 30

window.onload = function () {
    const username = document.getElementsByClassName("name")[1].innerText;
}

function optionsFunction(elem) {
    if (elem.className.includes("bid")) {
        bidAmount = Number(document.getElementById("bid-amount").innerText);
        if (elem.className == "increase bid") {
            document.getElementById("bid-amount").innerText = bidAmount + 5;
        }
        else if (elem.className == "decrease bid" && bidAmount >= 5) {
            document.getElementById("bid-amount").innerText = bidAmount - 5;
        }
        bidAmount = Number(document.getElementById("bid-amount").innerText);
    }

    else if (elem.innerText.includes("SHOW")) {
        console.log("SHOWN");
        data_to_send = { "class_": "show" }
        socket.send(JSON.stringify(data_to_send))
    }
    else if (elem.innerText.includes("PACK")) {
        console.log("PACKED");
        data_to_send = { "class_": "pack" }
        socket.send(JSON.stringify(data_to_send))
    }
    else if (elem.innerText.includes("PLACE")) {
        console.log("PLACED");
        min = Number(document.getElementsByClassName("min-bid")[0].innerText.split(":")[1]);
        if (bidAmount - min < 0) {
            chatUpdate("Please choose a value greater than minimun bid", "info-chat", "System")
        }
        else if (bidAmount - min > bidIncreaseLimit) {
            chatUpdate(`You can only increase the bid by ${bidIncreaseLimit}`, "info-chat", "System")
        }
        else {
            money_left = Number(document.getElementById("cash-left").innerText);
            if (bidAmount > money_left) {
                chatUpdate("Insufficiant money", "info-chat", "System")
            }
            if (document.getElementsByClassName("turn")[0].innerText == "Turn: " + username) {
                data_to_send = {
                    "class_": "place",
                    "bid_amount": bidAmount,
                }
                socket.send(JSON.stringify(data_to_send));
            }
        }
    }
}

