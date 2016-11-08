function sleep (time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}

// hides all the errors printed on the screen
var remove_error = function(ids){
	var i;
	for(i=0; i<ids.length;i++)
		document.getElementById(ids[i]).innerHTML = null;
}


// checks every input and prints corresponding errors if present and if not present then 
// makes an ajax call with post method to solve the results. If error occurred while registering 
// printed properly on screen else successfully saved printed and redirected to login page 
// after some time (1 s approx)
var register_check = function(){
	remove_error(['error_username','error_email','error_password','error_matching','error_registration']);
	var username_regex = /^[a-zA-Z0-9.\-_$@*!]{3,30}$/;
	var email_regex = /^(([a-z]+)|([A-Z]+)).[a-zA-Z]{2,4}[0-9]{2}@iitp.ac.in$/;
	var password_regex = /^(?=.*[0-9])(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{6,16}$/;

	var register_form = document.getElementById("register");
	var username = register_form.username.value;
	var email = register_form.email.value;
	var password = register_form.password.value;
	var confirm_password = register_form.confirm_password.value;

	user_info = {};
	var error = false;

	if(username_regex.test(username)){
		user_info.username = username;
	}else{
		document.getElementById('error_username').innerHTML = "Username must be <30 chars and contain alphabets, digits, $_-*!"; 
		error = true;
	}

	if(email_regex.test(email)){
		user_info.email = email;
	}else{
		document.getElementById('error_email').innerHTML = 'Email should be valid IITP email';
		error = true;
	}

	if(password_regex.test(password)){
		user_info.password = password;
		if(password == confirm_password){
			user_info.confirm_password = confirm_password;
		}
		else{
			document.getElementById('error_matching').innerHTML = 'Passwords Don\'t Match';
			error = true;	
		}
	}else{
		document.getElementById('error_password').innerHTML = 'password should contain atleast one number and one special character';
		error = true;
	}

	if(!error){
		remove_error(['error_username','error_email','error_password','error_matching','error_registration']);
		user_info.recaptcha = register_form['g-recaptcha-response'].value;
		user_info.csrfmiddlewaretoken = csrfmiddlewaretoken;
		console.log(user_info.recaptcha);
		ajaxPost('/users/register_done', user_info, function(response){
			response = JSON.parse(response);
			console.log(response);
			if(response.status == 200){
				content = response.content;
				
				if(content.error){
					document.getElementById('error_registration').innerHTML = content.error_info;
				}else{
					document.getElementById('successful_registration').innerHTML = 'Successfully Registered';
					if(content.redirect)
						location.href = content.redirect;
				}
			}
		});
	}
	
}

var csrfmiddlewaretoken;

window.onload = function(){
	csrfmiddlewaretoken = document.getElementById('csrf_form').csrfmiddlewaretoken.value;
	document.getElementById('csrf').innerHTML = '';
}	

