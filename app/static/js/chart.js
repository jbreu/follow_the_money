function initializeChart(labels, values) {
    const ctx = document.getElementById('spendingChart').getContext('2d');
    const data = {
        labels: labels,
        datasets: [{
            label: 'Spending Amount (€)',
            data: values,
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        }]
    };
    
    new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        callback: function (value) {
                            if (value >= 1e9) return (value / 1e9).toFixed(1) + 'B €';
                            if (value >= 1e6) return (value / 1e6).toFixed(1) + 'M €';
                            if (value >= 1e3) return (value / 1e3).toFixed(1) + 'K €';
                            return value + ' €';
                        }
                    }
                }
            }
        }
    });
}
