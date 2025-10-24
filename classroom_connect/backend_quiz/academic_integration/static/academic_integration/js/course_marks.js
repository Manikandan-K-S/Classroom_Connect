// Course marks visualization chart
function initializeGradeChart(componentData) {
    var ctx = document.getElementById('gradeChart').getContext('2d');
    
    // Create chart
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: componentData.labels,
            datasets: [{
                label: 'Component Scores (%)',
                data: componentData.scores,
                backgroundColor: componentData.backgroundColors,
                borderColor: componentData.borderColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Percentage Score'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Course Components'
                    },
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Course Component Performance',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        bottom: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.raw + '%';
                        }
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    });
}