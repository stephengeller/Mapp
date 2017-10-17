var view = "";

var setChannelView = function() {
	document.getElementById("page").innerHTML =
		languageList + messageList + messageForm;
	view = "channel";

	$("#setLanguage").click(function(event) {
		changeLanguage();
		event.preventDefault();
	});

	$("#send").click(function(event) {
		message = document.getElementById("messageForm").value;
		console.log(message);
		if (message != "") {
			params = { message: message, channel: channel };
			$.post("/chat/message", params).done(function(response) {
				if (response.code === 0) {
					document.getElementById("messageForm").value = "";
					displayError("");
				}
			});
		}
		event.preventDefault();
	});

	$("#logout").click(function(event) {
		clearSession();
		setLogInView();
		updateChannelName("");
	});

	$("#addChannel").click(function(event) {
		name = document.getElementById("channelForm").value;
		console.log("adding channel: " + name);
		createChannel(name);
		getChannelList();
		document.getElementById("channelForm").value = "";
		event.preventDefault();
	});

	$("#deleteChannel").click(function(event) {
		deleteChannel(channel);
		event.preventDefault();
	});

	refreshTargetLanguage(targetLanguage);
	updateLoop();
};

var setLogInView = function() {
	document.getElementById("page").innerHTML = loginForm;
	view = "login";

	$("#login").click(function(event) {
		var username = document.getElementById("usernameForm").value;
		if (username.length === 0) {
			displayError("Username can not be empty");
		} else {
		    params = {username: username, language: "en"}
			postRequest("/session/login", params, function(response){
			    setChannelView();
				joinChannel("global");
			})

		}
		event.preventDefault();
	});
};