var currentBarChart
var updateBarCharts
$(function () {
      var cat = []
	  var barData = []
      for(i=0;i<NumberOfCells;i++){
          for(j=0;j<NumberOfStacks;j++){  
                cat[j*NumberOfCells + i] =j.toString()  + ',' + i.toString()
				barData[j*NumberOfCells + i] =0
          }
      }
        $('#BarChartcontainer').highcharts({
            chart: {
                type: 'bar'
            },
            title: {
                text: ''
            },
            subtitle: {
                text: ''
            },
            xAxis: {
                categories: cat,
                title: {
                    text: null
                }
            },
            yAxis: {
                min: 0,
                title: {
                    text: '',
                    align: 'high'
                },
                labels: {
                    overflow: 'justify'
                }
            },
            tooltip: {
                valueSuffix: ' '
            },
            plotOptions: {
                bar: {
                    dataLabels: {
                        enabled: true
                    }
                }
            },
            legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'top',
                x: -100,
                y: 100,
                floating: true,
                borderWidth: 1,
                backgroundColor: '#FFFFFF',
                shadow: true
            },
            credits: {
                enabled: false
            },
            series: [{
                name: '',
                data: barData
            }]
        },
        function(chart){
            currentBarChart = chart
        }
                                                  
        );

  function update(data){
    //alert(data)
    //alert(currentBarChart.series[0].data[0])
	if($('#bar_select_voltage_btn').hasClass("active")){
    currentBarChart.series[0].setData(data.voltageList);
	}
	else if($('#bar_select_quantity_btn').hasClass("active")){
    currentBarChart.series[0].setData(data.quantityList);
	}
	else if($('#bar_select_soc_btn').hasClass("active")){
    currentBarChart.series[0].setData(data.socList);
	}
	else if($('#bar_select_cycles_btn').hasClass("active")){
    currentBarChart.series[0].setData(data.cyclesList);
	}
	currentBarChart.redraw();	
  }
  updateBarCharts = update
  
  }
  
  );
    
