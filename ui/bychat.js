var botui;

$(document).ready(function () {

    botui = new BotUI('my-botui-app');
    botui.message.add({
        content: 'Welcome to Blue Yonder 🙏🏻'
    });

    // Get the input field
    var input = document.getElementById("humanMsgInput");

    $("#humanMsgEnter").click(async () => {
        let inputVal = input.value
        await botui.message.add({
            content: inputVal,
            human: true
        });
        input.value = "";
        let result = await $.ajax({ url: "http://localhost:5000?msg=" + inputVal });
        await botui.message.add({
            content: result,
        });
        var msg = new SpeechSynthesisUtterance(result);
        window.speechSynthesis.speak(msg);
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