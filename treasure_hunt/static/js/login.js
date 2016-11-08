var remove_errors = function(){
	document.getElementById('error_login').innerHTML = '';
};

var get_variables = function(){
	// source - http://stackoverflow.com/questions/979975/how-to-get-the-value-from-the-get-parameters
	var query_string = {};
	var query = window.location.search.substring(1);
	var vars = query.split("&");
	for(var i=0;i<vars.length; i++){
		var pair = vars[i].split("=");
		if (typeof query_string[pair[0]] === "undefined") {
	     	query_string[pair[0]] = decodeURIComponent(pair[1]);
	        // If second entry with this name
	    } else if (typeof query_string[pair[0]] === "string") {
	    	var arr = [ query_string[pair[0]],decodeURIComponent(pair[1]) ];
	    	query_string[pair[0]] = arr;
	        // If third or later entry with this name
	    } else {
	    	query_string[pair[0]].push(decodeURIComponent(pair[1]));
	    }
	} 
	return query_string;
}

var login_check = function(){
	var login_form = document.getElementById("login_form");
	
	var username = login_form.username.value;
	var password = login_form.password.value;

	if(password == '' || username == ''){
		document.getElementById('error_login').innerHTML = 'Username or password cannot be empty';	
	}else{
		var user_info = get_variables();
		user_info.username = username;
		user_info.password = password;
		user_info.recaptcha = login_form['g-recaptcha-response'].value;
		// console.log(user_info.recaptcha);
		user_info.csrfmiddlewaretoken = csrfmiddlewaretoken;
		ajaxPost(login_check_url, user_info, function(response){
			response = JSON.parse(response);
			content = response.content;
			console.log(response);
			if(content.error){
				document.getElementById('error_login').innerHTML = content.error_info;
			}else{
				if(content.redirect)
					location.href = content.redirect;
			}
		})
	}
};


var forgot_password = function(){
	var login_form = document.getElementById("login_form");
	var username = login_form.username.value;
	if(username == ''){
		document.getElementById('error_login').innerHTML = 'Username cannot be empty';
	}else{
		user_info = {};
		user_info.username = username;
		user_info.recaptcha = login_form['g-recaptcha-response'].value;
		user_info.csrfmiddlewaretoken = csrfmiddlewaretoken;
		ajaxPost(forgot_password_url, user_info, function(response){
			response = JSON.parse(response);
			content = response.content;
			if(content.error){
				document.getElementById('error_login').innerHTML = content.error_info;
			}else{
				if(content.redirect)
					location.href = content.redirect;
			}
		});
	}

}


var content, csrfmiddlewaretoken, login_check_url, forgot_password_url;

window.onload = function(){
	var info_form = document.getElementById('info_form');
	csrfmiddlewaretoken = info_form.csrfmiddlewaretoken.value;
	login_check_url = info_form.login_check_url.value;
	forgot_password_url = info_form.forgot_password_url.value;
	console.log(forgot_password_url);
	document.getElementById('info').innerHTML = '';
}	

// copied from previous code  refer js/g.js for info
function init_1(){
	$("p").hide();
	alert("hidden");
}

function show_head(){
	var op=$("div.nav").css("opacity");
	op=parseFloat(op);
	if(op<1)
	{op=op+0.1;}
	$("div.login").css("opacity",op);
	$("div.nav").css("opacity",op);
	var TIMER=setTimeout(show_head,50);
}

function hide_head(){
	var op=$("div.nav").css("opacity");
	op=parseFloat(op);
	if(op>0.1)
	{op=op-0.1;}
	$("div.nav").css("opacity",op);
	var TIMER=setTimeout(hide_head,50);
}
