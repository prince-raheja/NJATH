function open_question(opened_count, redirect_url, opened){
	if(opened){
		location.href = redirect_url;
	}
	else if(opened_count < 6){
		var r = confirm('Are you sure you want to open');
		if(r){
			location.href = redirect_url;
		}
	}else{
		var r = confirm('Are you sure you want to open bonus question\nWithout answering it\
			 and proceeding to next level will result in a huge penalty');
		if(r){
			location.href = redirect_url;
		}
	}
}



function next_level(opened_count, redirect_url,current_level){
	if(opened_count > 6){
		var r = confirm('Are you sure you want to proceed to Next Level. You cannot come back...');
		if(r){
			location.href = redirect_url;
		}
	}else{
		var r = confirm('You have opened a bonus question. Proceeding to next level will \
			result in a HIGH PENALTY of ' + current_level*10 + ' POINTS' );
		if(r){
			location.href = redirect_url;
		}
	}
}