function insertAtCaret(areaId,text) {var txtarea = document.getElementById(areaId);var scrollPos = txtarea.scrollTop;var strPos = 0;var br = ((txtarea.selectionStart || txtarea.selectionStart == '0') ? "ff" : (document.selection ? "ie" : false ) );if (br == "ie") {txtarea.focus();var range = document.selection.createRange();range.moveStart ('character', -txtarea.value.length);strPos = range.text.length;} else if (br == "ff") strPos = txtarea.selectionStart;var front = (txtarea.value).substring(0,strPos);var back = (txtarea.value).substring(strPos,txtarea.value.length);txtarea.value=front+text+back;strPos = strPos + text.length;if (br == "ie") {txtarea.focus();var range = document.selection.createRange();range.moveStart ('character', -txtarea.value.length);range.moveStart ('character', strPos);range.moveEnd ('character', 0);range.select();} else if (br == "ff") {txtarea.selectionStart = strPos;txtarea.selectionEnd = strPos;txtarea.focus();}txtarea.scrollTop = scrollPos;} 
$(function() {
  $('#command_program').live('keydown', function(e) {
                     var keyCode = e.keyCode || e.which;
                     
                     if (keyCode == 9) {
                     e.preventDefault();
                     // replace tab to 4 space
                     insertAtCaret('command_program', '    ')
                     } 
                     });
  }

);
$(document).ready(function(){
 
  // populate queue from queue directory
  $.getJSON("/queue/list", function(data) {
    $.each(data, function(index, name) {
      add_to_job_queue(name);
    });
  });
    
  // populate library from library directory
  $.getJSON("/library/list", function(data) {
    if (typeof(data.sort) == 'function') {
      data.sort();
    }
    $.each(data, function(index, name) {
      $('#command_list_library').prepend('<li><a href="#">'+ name +'</a></li>');
    });
  	$('#command_list_library li a').click(function(){
  	  var name = $(this).text();
      $.get("/library/get/" + name, function(gdata) {
        load_into_command_widget(gdata, name);
      });
  	});  	
  });
  // .success(function() { alert("second success"); })
  // .error(function() { alert("error"); })
  // .complete(function() { alert("complete"); });
 
  


  $("#progressbar").hide();  
  $("#command_list_submit").click(function(e) {
  	// send gcode string to server via POST
  	var commands = $('#command_program').val();
    send_gcode(commands, "Python Code sent to backend.", true);
  	return false;
  });


  $('#gcode_bbox_submit').tooltip();
  $("#gcode_bbox_submit").click(function(e) {
    var gcodedata = $('#command_program').val();
    Commandreader.parse(gcodedata, 1);
    var gcode_bbox = Commandreader.getBboxGcode();
    var header = "G90\nG0F"+app_settings.max_seek_speed+"\n"
    var footer = "G00X0Y0F"+app_settings.max_seek_speed+"\n"
    // save_and_add_to_job_queue($('#command_list_name').val() + 'BBOX', header + gcode_bbox + footer);  // for debugging
    send_gcode(header + gcode_bbox + footer, "BBox G-Code sent to backend", true);
    return false;
  });

  $('#command_list_save_to_queue').tooltip();
  $("#command_list_save_to_queue").click(function(e) {
    save_and_add_to_job_queue($.trim($('#command_list_name').val()), $('#command_program').val());
    return false;
  });

});  // ready
