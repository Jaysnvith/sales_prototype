var root = document.documentElement;
var primaryColor = getComputedStyle(root).getPropertyValue('--bulma-primary');
var linkColor = getComputedStyle(root).getPropertyValue('--bulma-link');
var dangerColor = getComputedStyle(root).getPropertyValue('--bulma-danger');
var successColor = getComputedStyle(root).getPropertyValue('--bulma-success');
var infoColor = getComputedStyle(root).getPropertyValue('--bulma-info');
var warningColor = getComputedStyle(root).getPropertyValue('--bulma-warning');

// Bar Chart
var barChart = new Chart(document.getElementById('barDash'), {
  type: 'bar',
  data: {
    labels: bar_labels,
    datasets: [{
      data: bar_counts,
      backgroundColor: linkColor,
    }]
  },
  options: {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: "This Month Most Sold Products",
      },
      legend: {
        display: false,
      }
    },
  },
});

// Pie Chart
var pieChart = new Chart(document.getElementById('pieDash'), {
  type: 'pie',
  data: {
    labels: pie_labels,
    datasets: [{
      data: pie_counts,
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: "Monthly Sales by Products",
      },
      legend: {
        position: 'bottom',
      },
      tooltip: {
        callbacks: {
          label: function(tooltipItem) {
            return '$' + tooltipItem.raw.toFixed(2); // Add dollar sign and format to 2 decimal places
          }
        }
      }
    },
  },
});

// Line Chart
var lineChart = new Chart(document.getElementById('lineDash'), {
  type: 'line',
  data: {
    labels: ['January', 'February', 'March', 'April', 'Mei', 'June', 'Juli', 'August', 'September', 'October', 'November', 'Desember'],
    datasets: [{
      data: [10, 11, 28, 15, 10, 2, 17, 19, 14, 15, 24, 22], // Adjusted data to be numbers
      borderColor: linkColor,
      fill: false
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: "Annual Sales",
      },
      legend: {
        display: false,
      }
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
          text: 'Month'
        }
      },
      y: {
        title: {
          display: true,
          text: 'Sales'
        },
        ticks: {
          beginAtZero: true,
          callback: function(value) { return '$' + value; }
        }
      }
    }
  }
});