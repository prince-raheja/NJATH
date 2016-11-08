function remove_error(){
	var i;
	var ids = ['error_current_password','error_matching','error_new_password','error_password']
	for(i=0; i<ids.length;i++){
		console.log(i);
		document.getElementById(ids[i]).innerHTML = '';
	}
}

function password_check() {
	// remove_error();
	var password_regex = /^(?=.*[0-9])(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{6,16}$/;
	var current_password;
	var password_form = document.getElementById("register");
	var csrfmiddlewaretoken = password_form.csrfmiddlewaretoken.value;
	var new_password = password_form.new_password.value;
	var new_confirm_password = password_form.new_confirm_password.value;
	var error = false;

	if(password_form.current_password)
		current_password = password_form.current_password.value;
	else
		current_password = null;
	

	if(current_password){
		if(password_regex.test(current_password)){
			password_info.current_password = current_password;
			if(current_password == new_password){
				error = true;
				document.getElementById('error_current_password').innerHTML = 'Your current_password and new password are same'
			}
		}
		else{
			error = true;
			document.getElementById('error_current_password').innerHTML = 'Your current_password might be wrong'
		}

	}
	if(password_regex.test(new_password)){
		password_info.new_password = new_password;
		if(new_password == new_confirm_password){
			password_info.new_confirm_password = new_confirm_password;
		}
		else{
			error = true;
			document.getElementById('errro_matching').innerHTML = 'Passwords Don\'t Match';
		}
	}
	else{
		error = true;
		document.getElementById('error_new_password').innerHTML = 'password should contain atleast one number and one special character';
	}

	if(!error){
		password_info.recaptcha = password_form['g-recaptcha-response'].value;
		console.log(password_info);
		ajaxPost('/users/update_password',password_info , function(response){
			response = JSON.parse(response);
			console.log(response);
			if(response.status == 200){
				content = response.content;
				if(content.error){
					document.getElementById('error_password').innerHTML = content.error_info;
				}
				else{
					if(content.redirect){
						document.getElementById('successful_changed_password').innerHTML = 'Successfully Updated Password'
						location.href = content.redirect;
					}
				}
			}
		});
	}
}

var password_info = {};

window.onload = function(){
	var url = window.location.href ;
	var key_index = url.indexOf('key');
	if(key_index != -1){
		password_info.key = url.substring(key_index+4);
	}
	password_info.username = document.getElementById('username').innerHTML;
}
