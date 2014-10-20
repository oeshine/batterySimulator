var graphArray = new Array()
var currentId = "graphCurrentId"
var voltageId = "graphVoltageId"
var quantityId = "graphQuantityId"

var graphPropertiesArray = new Array()
var graphDataLengthMax = 256
var graphProperties ={
					title:"",
					drawPoints: true,
					showRoller: false,
					valueRange: [0.0, 1.2],
					labels: ['Time', 'v1'],
					ylabel:"",
					legend:"always"
				  }
graphPropertiesArray[currentId]=Object.create(graphProperties)
graphPropertiesArray[currentId].title = "Current-T"
graphPropertiesArray[currentId].ylabel = "Current"

graphPropertiesArray[voltageId]=Object.create(graphProperties)
graphPropertiesArray[voltageId].title = "Voltage-T"
graphPropertiesArray[voltageId].ylabel = "Voltage"


graphPropertiesArray[quantityId]=Object.create(graphProperties)
graphPropertiesArray[quantityId].title = "quantity-T"
graphPropertiesArray[quantityId].ylabel = "quantity"


function create_graph(ID){
	var data = [];
	var x = 0.0;

	graphArray[ID] = new Dygraph(document.getElementById(ID), data,
					  {
					title:graphPropertiesArray[ID].title ,
					drawPoints: graphPropertiesArray[ID].drawPoints,
					showRoller: graphPropertiesArray[ID].showRoller,
					valueRange: graphPropertiesArray[ID].valueRange,
					labels: graphPropertiesArray[ID].labels,
					ylabel:graphPropertiesArray[ID].ylabel,
					legend:graphPropertiesArray[ID].legend
				  });
	setInterval(function() {
	x=Math.round((x+0.1)*10)/10 // current time
	var y = Math.random()
	data.push([x, y])
	if(data.length> graphDataLengthMax)
	data.shift()
	graphArray[ID].updateOptions( { 'file': data } )
	}, 1000)
	//alert("graphArray inited") 
}
function graphVisibilityChanged(el) {
	graphArray[el.name].setVisibility(el.id, el.checked)
}
function refreshGraph(){
	for(graph in graphArray)
	    if ($("#tab_curves").hasClass('active'))
			graphArray[graph].resize()
}

$(window).load(function(){ 
	create_graph(currentId)
	create_graph(voltageId)
	create_graph(quantityId)
	
	$('#tab_curves').mouseenter(function() {
		refreshGraph()
	});

  
	$.get('/graph_data_length_max', function(data2) {
		if (data2.length > 0) {
		graphDataLengthMax = parseInt(data2);
		}
	})
});