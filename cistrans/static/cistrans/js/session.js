//This function gets cookie with a given name
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

/*
The functions below will create a header with csrftoken
*/

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function addQTL(){
	var qtl_info = d3.select("#this_experiment").text()+" "+d3.select("#probe").text()+" "+d3.select("#transcript").text()+" "+d3.select("#marker").text()+" "+d3.select("#lod_si").text();
	$("#QTL").val(qtl_info)
}


$('#post-form').on('submit', function(event){
    event.preventDefault();
    console.log("form submitted!")
    create_session();
});

function create_session(){
    console.log("create session is working!") // sanity check
    $.ajax({
        url : "", // the endpoint
        type : "POST", // http method
        data : {QTL:$('#QTL').val() }, // data sent with the post request
        cache: false,
        // handle a successful response
        success : function(json) {
        	$('#task').html('');
        	for(var i=0;i<json.length;i++){
      			$('#task').append("<div class='task_ins'><p><input type='checkbox' name='QTL_list' class='selected_qtl' />QTL_id:"+json[i][0]+" experiment:"+json[i][1]+" probe:"+json[i][2]+" marker:"+json[i][3]+"<input type='button' class='delete_btn' /></p></div>");
        	}
        	$('#task').append('<button id = "qtl_analysis"  class = "btn_analysis">run QTL analysis</button>');
        	$('.task_ins').each(function() {
        		   var html_ins = $(this).find("p").text();
        		   var ind_1 = html_ins.indexOf(":")+1;
        		   var ind_2 = html_ins.indexOf(" ");
        		   var id_ins = html_ins.slice(ind_1,ind_2);
        		   //console.log(id_ins);
        		   var task_pre = "task-";
        		   $(this).attr('id', id_ins);
        		   var del_btn_pre = "del-btn-";
        		   $(this).find(".delete_btn").attr('id',del_btn_pre+id_ins);
        		   $(this).find(".selected_qtl").attr('value',id_ins);
        	});
        	
            console.log(json); // log the returned json to the console
            console.log("success"); // another sanity check
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
};
$(function() {
    $(document).on('click', '.delete_btn', function () {	
    console.log("prepare to delete task");
    var task_id = $(this).attr('id').slice(8);
    $.ajax({
        url : "", // the endpoint
        type : "POST", // http method
        data : {del_task:task_id }, // data sent with the post request
        cache: false,
        // handle a successful response
        success : function(json) {
        	$('#task').html('');
        	for(var i=0;i<json.length;i++){
      			$('#task').append("<div class='task_ins'><p><input type='checkbox' name='QTL_list'  class='selected_qtl' />QTL_id:"+json[i][0]+" experiment:"+json[i][1]+" probe:"+json[i][2]+" marker:"+json[i][3]+"<input type='button' class='delete_btn' /></p></div>");
        	}
        	$('#task').append('<button id = "qtl_analysis"  class = "btn_analysis">run QTL analysis</button>');
        	$('.task_ins').each(function() {
     		   var html_ins = $(this).find("p").text();
     		   var ind_1 = html_ins.indexOf(":")+1;
     		   var ind_2 = html_ins.indexOf(" ");
     		   var id_ins = html_ins.slice(ind_1,ind_2);
     		   //console.log(id_ins);
     		   var task_pre = "task-";
     		   $(this).attr('id', id_ins);
     		   var del_btn_pre = "del-btn-";
     		   $(this).find(".delete_btn").attr('id',del_btn_pre+id_ins);
     		   $(this).find(".selected_qtl").attr('value',id_ins);
     	});
            console.log(json); // log the returned json to the console
            console.log("success"); // another sanity check
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
    });
});

