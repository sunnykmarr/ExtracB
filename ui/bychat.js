var botui;

$(document).ready(function () {

    botui = new BotUI('my-botui-app');
    addSystemMessage = async msg => {
        await botui.message.add({
            content: msg
        });
        let speech = new SpeechSynthesisUtterance(msg);
        window.speechSynthesis.speak(speech);
    }

    isJsonString = str => {
        try {
            JSON.parse(str);
        } catch (e) {
            return false;
        }
        return true;
    }

    addSystemMessage('Welcome to Blue Yonder 🙏🏻')

    // Get the input field
    let input = document.getElementById("humanMsgInput");

    send = async inputVal => {
        let result;
        try {
            result = await $.ajax({ url: "http://localhost:5000?msg=" + inputVal });
            resultAction(result)
        } catch (err) {
            result = "Oops"
            addSystemMessage(result)
        }
    }

    resultAction = async result => {
        if (result.startsWith("{") && isJsonString(result)) {
            console.log(result)
            resultObj = JSON.parse(result)
            if (resultObj.type === "array") {
                for (message of resultObj.value) {
                    await addSystemMessage(message)
                }
            } else if (resultObj.type === "question") {
                await addSystemMessage(resultObj.value)
                botui.action.button({
                    action: [
                        {
                            text: 'Yes',
                            value: 'yes'
                        }, {
                            text: 'No',
                            value: 'no'
                        }
                    ]
                }).then(function (res) {
                    send(res.value)
                });
            }
        } else {
            addSystemMessage(result)
        }
    }

    $("#humanMsgEnter").click(async () => {
        botui.action.hide();
        let inputVal = input.value
        await botui.message.add({
            content: inputVal,
            human: true
        });
        input.value = "";
        send(inputVal)
    });

    // Execute a function when the user releases a key on the keyboard
    input.addEventListener("keyup", function (event) {
        // Number 13 is the "Enter" key on the keyboard
        if (event.keyCode === 13) {
            // Cancel the default action, if needed
            event.preventDefault();
            // Trigger the button element with a click
            document.getElementById("humanMsgEnter").click();
        }
    });



});