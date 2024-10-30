var root = document.documentElement;
var linkColor = getComputedStyle(root).getPropertyValue('--bulma-link');
var primaryColor = getComputedStyle(root).getPropertyValue('--bulma-primary');
var dangerColor = getComputedStyle(root).getPropertyValue('--bulma-danger');
var successColor = getComputedStyle(root).getPropertyValue('--bulma-success');
var infoColor = getComputedStyle(root).getPropertyValue('--bulma-info');
var warningColor = getComputedStyle(root).getPropertyValue('--bulma-warning');
var textColor = getComputedStyle(root).getPropertyValue('--bulma-grey');
var colors = [primaryColor, dangerColor, successColor, infoColor, warningColor];

Chart.defaults.borderColor = textColor;
Chart.defaults.color = textColor;

document.addEventListener('DOMContentLoaded', function() {
  // Set data monthly/yearly
  function setupChartUpdate(buttonId, chart, data, labels, titlePrefix) {
    document.getElementById(buttonId).addEventListener('click', function() {
      chart.data.datasets[0].data = data;
      chart.data.labels = labels;
      chart.options.plugins.title.text = titlePrefix + (chart === productOrders ? month_name : current_year);
      chart.update();
    });
  }

  // Set product orders
  setupChartUpdate('updateProdM', productOrders, prod_orders_monthly_counts,prod_orders_monthly_labels, "Products Sold in ");
  setupChartUpdate('updateProdY', productOrders, prod_orders_yearly_counts, prod_orders_yearly_labels, "Products Sold in ");

  // Set customer orders
  setupChartUpdate('updateCustM', customerOrders, cust_orders_monthly_counts, cust_orders_monthly_labels, "Customer Orders in ");
  setupChartUpdate('updateCustY', customerOrders, cust_orders_yearly_counts, cust_orders_yearly_labels, "Customer Orders in ");
});

console.log(annual_sales_counts); 

// Monthly sales chart
var monthlySales = new Chart(document.getElementById('monthlySales'), {
  type: 'line',
  data: {
    labels: [...annual_sales_labels, ...forecast_sales_labels],
    datasets: [
      {
        label: "Records",
        data: annual_sales_counts,
        borderColor: primaryColor,
      },
      {
        label: "Forecast",
        data: [...Array(annual_sales_counts.length).fill(null), ...forecast_sales_counts],
        borderColor: infoColor,
      }
    ]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: "Monthly Revenue " + current_year,
        font: {
          size: 16,
          weight: 'bold',
        },
        padding: {
          bottom: 25,
        }
      },
    },
    animations: {
      tension: {
        easing: 'linear',
        from: 0.5,
        to: -0.25,
        loop: true
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Month',
          font: {
            size: 14,
          }
        },
        grid: {
          display: false
        },
      },
      y: {
        title: {
          display: true,
          text: 'Sales',
          font: {
            size: 14, // Increase font size
          }
        },
        ticks: {
          stepSize: 200000,
          callback: function(value) { return '$' + value.toLocaleString(); }, // Format y-axis ticks
        },
      }
    }
  }
});


// Product orders chart
var productOrders = new Chart(document.getElementById('productOrders'), {
  type: 'bar',
  data: {
    labels: prod_orders_monthly_labels,
    datasets: [{
      data: prod_orders_monthly_counts,
      backgroundColor: colors,
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: "Products Sold in "+ month_name,
        font: {
          size: 16,
          weight: 'bold',
        },
        padding: {
          bottom: 25,
        },
      },
      legend: {
        display: false,
      }
    },
    scales: {
      y: {
        ticks: {
          stepSize: 1,
        },
      },
      x: {
        grid: {
          display: false,
        },
      }
    },
  },
});

// Stock level chart
var stockLevel = new Chart(document.getElementById('stockLevel'), {
  type: 'bar',
  data: {
    labels: stock_level_labels,
    datasets: [{
      data: stock_level_counts,
      backgroundColor: function(context) {
        const value = context.raw;  // Access the value of the data point
        return value < 20 ? dangerColor : successColor;  // Change the color based on the value
      },
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: "Stock Level",
        font: {
          size: 16,
          weight: 'bold',
        },
        padding: {
          bottom: 25,
        },
      },
      legend: {
        display: false,
      }
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
      },
    },
  },
});

// Customer orders chart
var customerOrders = new Chart(document.getElementById('customerOrders'), {
  type: 'bar',
  data: {
    labels: cust_orders_monthly_labels,
    datasets: [{
      data: cust_orders_monthly_counts,
      backgroundColor: colors,
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: "Customer Orders " + month_name,
        font: {
          size: 16,
          weight: 'bold',
        },
        padding: {
          bottom: 25,
        },
      },
      legend: {
        display: false,
      }
    },
    scales: {
      y: {
        ticks: {
          stepSize: 1,
        },
      },
      x: {
        grid: {
          display: false,
        },
      },
    },
  },
});

// Region Comparison chart
var regionCompare = new Chart(document.getElementById('regionCompare'), {
  type: 'pie',
  data: {
    labels: region_compare_labels,
    datasets: [{
      data: region_compare_counts,
      backgroundColor: colors,
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'left',  // Position the legend to the left
      },
    },
  },
});
