function check_answer(question_slug, url){
	question_slug = question_slug.trim();
	url = url.trim()
	console.log(question_slug);
	console.log(url);
	var answer_form = document.getElementById("answer_form");

	var answer = answer_form.answer.value;
	if(answer == '' || answer == ' '){
		document.getElementById('error_answer').innerHTML = 'Answer cannot be blank';
	}else{
		var answer_obj = {};
		answer_obj.answer = answer;
		answer_obj.question_slug = question_slug;
		// ajaxPost(url, answer_obj, function(response){
		ajaxPost(url, answer_obj, function(response){
			console.log(response);
			response = JSON.parse(response);
			content = response.content;
			if(content.error){
				document.getElementById('error_answer').innerHTML = content.error_info;
			}else{
				if(content.redirect)
					location.href = content.redirect;
			}
		});
	}
}



console.log('hi');