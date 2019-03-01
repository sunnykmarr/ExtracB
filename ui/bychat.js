var botui;

$(document).ready(function () {

    botui = new BotUI('my-botui-app');
    addSystemMessage = msg => {
        botui.message.add({
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
    var input = document.getElementById("humanMsgInput");

    $("#humanMsgEnter").click(async () => {
        let inputVal = input.value
        await botui.message.add({
            content: inputVal,
            human: true
        });
        input.value = "";
        let result;
        try {
            result = await $.ajax({ url: "http://localhost:5000?msg=" + inputVal });
            if (isJsonString(result)) {
                resultObj = JSON.parse(result)
                if (resultObj.type === "array") {
                    for (message of resultObj.value) {
                        addSystemMessage(message)
                    }
                }
            } else {
                addSystemMessage(result)
            }
        } catch (err) {
            result = "Oops"
            addSystemMessage(result)
        }
        
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