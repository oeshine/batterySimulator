
var gcode_coordinate_offset = undefined;

function reset_offset() {
  $("#offset_area").hide();
  $('#offset_area').css({'opacity':0.0, left:0, top:0});
  gcode_coordinate_offset = undefined;
	$("#cutting_area").css('border', '1px dashed #ff0000');
	$("#offset_area").css('border', '1px dashed #aaaaaa');
  send_gcode('G54\n', "Offset reset.", false);
  $('#coordinates_info').text('');
}

  
$(document).ready(function(){

  var isDragging = false;
  
  function assemble_and_send_gcode(x,y) {
    	var g0_or_g1 = 'G0';
      var air_assist_on = '';
      var air_assist_off = '';
    	if($('#feed_btn').hasClass("active")){
    		g0_or_g1 = 'G1';
        air_assist_on = 'M80\n';
        air_assist_off = 'M81\n';
    	}
    	var feedrate = mapConstrainFeedrate($("#feedrate_field" ).val());
    	var intensity =  mapConstrainIntesity($( "#intensity_field" ).val());
    	var gcode = 'G90\n'+air_assist_on+'S'+ intensity + '\n' + g0_or_g1 + ' X' + 2*x + 'Y' + 2*y + 'F' + feedrate + '\nS0\n'+air_assist_off;	
      // $().uxmessage('notice', gcode);
    	send_gcode(gcode, "Motion request sent.", false);    
  }
  
  function assemble_info_text(x,y) {
    var coords_text;
  	var move_or_cut = 'move';
  	if($('#feed_btn').hasClass("active")){
  		move_or_cut = 'cut';
  	}
  	var feedrate = mapConstrainFeedrate($( "#feedrate_field" ).val());
  	var intensity =  mapConstrainIntesity($( "#intensity_field" ).val());
  	var coords_text;
  	if (move_or_cut == 'cut') {
  	  coords_text = move_or_cut + ' to (' + 2*x + ', '+ 2*y + ') at ' + feedrate + 'mm/min and ' + Math.round(intensity/2.55) + '% intensity';
  	} else {
  	  coords_text = move_or_cut + ' to (' + 2*x + ', '+ 2*y + ') at ' + feedrate + 'mm/min'
  	}
  	return coords_text;
  }
  
  
  
  $("#offset_area").click(function(e) { 
    if(!e.shiftKey) {
    	var offset = $(this).offset();
    	var x = (e.pageX - offset.left);
    	var y = (e.pageY - offset.top);     
      assemble_and_send_gcode(x,y);
      return false
    }
  });

  $("#offset_area").hover(
    function () {
    },
    function () {
  		$('#offset_info').text('');		
    }
  );
  
  $("#offset_area").mousemove(function (e) {
    if(!e.shiftKey) {
    	var offset = $(this).offset();
    	var x = (e.pageX - offset.left);
    	var y = (e.pageY - offset.top);
      $('#offset_info').text(assemble_info_text(x,y));
    } else {
      $('#offset_info').text('');
    }
  });
  
  // function moveto (x, y) {
  //  $('#y_cart').animate({  
  //    top: y - 8.5 - 6
  //  });   
  //  
  //  $('#x_cart').animate({  
  //    left: x - 6,  
  //    top: y - 6 
  //  });
  // };
  
  //// motion parameters
  $( "#intensity_field" ).val('0');
  $( "#feedrate_field" ).val(app_settings.max_seek_speed);
  
  $("#seek_btn").click(function(e) {
    $( "#intensity_field" ).hide();
    $( "#intensity_field_disabled" ).show();
  });  
  $("#feed_btn").click(function(e) {
    $( "#intensity_field_disabled" ).hide();
    $( "#intensity_field" ).show();
  });   
  
  $("#feedrate_btn_slow").click(function(e) {
    $( "#feedrate_field" ).val("600");
  });  
  $("#feedrate_btn_medium").click(function(e) {
    $( "#feedrate_field" ).val("2000");
  });  
  $("#feedrate_btn_fast").click(function(e) {
    $( "#feedrate_field" ).val(app_settings.max_seek_speed);
  });  
  $("#feedrate_field").focus(function(e) {
    $("#feedrate_btn_slow").removeClass('active');
    $("#feedrate_btn_medium").removeClass('active');
    $("#feedrate_btn_fast").removeClass('active');
  });
  
  if ($("#feedrate_field" ).val() != app_settings.max_seek_speed) {
    $("#feedrate_btn_slow").removeClass('active');
    $("#feedrate_btn_medium").removeClass('active');
    $("#feedrate_btn_fast").removeClass('active');    
  }
  
  //// jog buttons
  $("#jog_up_btn").click(function(e) {
    var gcode = 'G91\nG0Y-10F6000\nG90\n';
    send_gcode(gcode, "Moving Up ...", false)	
  });   
  $("#jog_left_btn").click(function(e) {
    var gcode = 'G91\nG0X-10F6000\nG90\n';
    send_gcode(gcode, "Moving Left ...", false)	
  });   
  $("#jog_right_btn").click(function(e) {
    var gcode = 'G91\nG0X10F6000\nG90\n';
    send_gcode(gcode, "Moving Right ...", false)	
  });
  $("#jog_down_btn").click(function(e) {
    var gcode = 'G91\nG0Y10F6000\nG90\n';
    send_gcode(gcode, "Moving Down ...", false)	
  });

  //// air assist buttons
  $("#air_on_btn").click(function(e) {
    var gcode = 'M80\n';
    send_gcode(gcode, "Air assist on ...", false) 
  });  
  $("#air_off_btn").click(function(e) {
    var gcode = 'M81\n';
    send_gcode(gcode, "Air assist off ...", false) 
  });  
      
});  // ready
