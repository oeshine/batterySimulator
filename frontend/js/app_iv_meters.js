var iVChart
var updateIvChart //will be point to update(I,V)
$(function () {
	$('#IVcontainer').highcharts({
	
	    chart: {
	        type: 'gauge',
	        plotBorderWidth: 1,
	        plotBackgroundColor: {
	        	linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
	        	stops: [
	        		[0, '#FFF4C6'],
	        		[0.3, '#FFFFFF'],
	        		[1, '#FFF4C6']
	        	]
	        },
	        plotBackgroundImage: null,
	        height: 200
	    },
	
	    title: {
	        text: 'Total Voltage & Current'
	    },
	    
	    pane: [{
	        startAngle: -45,
	        endAngle: 45,
	        background: null,
	        center: ['25%', '145%'],
	        size: 300
	    }, {
	    	startAngle: -45,
	    	endAngle: 45,
	    	background: null,
	        center: ['75%', '145%'],
	        size: 300
	    }],	    		        
	
	    yAxis: [{
	        min: 0,
	        max: 500,
	        minorTickPosition: 'outside',
	        tickPosition: 'outside',
	        labels: {
	        	rotation: 'auto',
	        	distance: 20
	        },

	        pane: 0,
	        title: {
	        	text: 'Total Voltage<br/><span style="font-size:8px">V</span>',
	        	y: -40
	        }
	    }, {
	        min: -5,
	        max: 20,
	        minorTickPosition: 'outside',
	        tickPosition: 'outside',
	        labels: {
	        	rotation: 'auto',
	        	distance: 20
	        },
	        plotBands: [{
	        	from: 15,
	        	to: 20,
	        	color: '#C02316',
	        	innerRadius: '100%',
	        	outerRadius: '105%'
	        }],
	        pane: 1,
	        title: {
	        	text: 'Total Current<br/><span style="font-size:8px">A</span>',
	        	y: -40
	        }
	    }],
	    
	    plotOptions: {
	    	gauge: {
	    		dataLabels: {
	    			enabled: false
	    		},
	    		dial: {
	    			radius: '100%'
	    		}
	    	}
	    },
	    	
	
	    series: [{
	        data: [-20],
	        yAxis: 0
	    }, {
	        data: [-20],
	        yAxis: 1
	    }]
	
	},
	
	// Let the music play
	function(chart) {
        iVChart = chart
	});
  function update(I,V){
  //console.log(I)
  //console.log(V)
  var left = iVChart.series[0].points[0],
  right = iVChart.series[1].points[0]
  left.update(V, false);
  right.update(I, false);
  iVChart.redraw();
  //alert(iVChart)
  }
  updateIvChart = update //point to update
}
);

