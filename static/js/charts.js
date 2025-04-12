/**
 * Charts.js - Chart creation functions for Career Advisor
 */

/**
 * Creates a radar chart for skills assessment
 * @param {string} elementId - Canvas element ID
 * @param {Array} technicalLabels - Labels for technical skills
 * @param {Array} technicalData - Data values for technical skills
 * @param {Array} softLabels - Labels for soft skills
 * @param {Array} softData - Data values for soft skills
 */
function createSkillsRadarChart(elementId, technicalLabels, technicalData, softLabels, softData) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Combine all labels and datasets
    const labels = [...technicalLabels, ...softLabels];
    
    // Create the chart
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Technical Skills',
                    data: [...technicalData, ...Array(softLabels.length).fill(0)],
                    backgroundColor: 'rgba(13, 110, 253, 0.2)',
                    borderColor: 'rgba(13, 110, 253, 1)',
                    pointBackgroundColor: 'rgba(13, 110, 253, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(13, 110, 253, 1)'
                },
                {
                    label: 'Soft Skills',
                    data: [...Array(technicalLabels.length).fill(0), ...softData],
                    backgroundColor: 'rgba(111, 66, 193, 0.2)',
                    borderColor: 'rgba(111, 66, 193, 1)',
                    pointBackgroundColor: 'rgba(111, 66, 193, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(111, 66, 193, 1)'
                }
            ]
        },
        options: {
            scales: {
                r: {
                    angleLines: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    pointLabels: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        font: {
                            size: 12
                        }
                    },
                    ticks: {
                        backdropColor: 'transparent',
                        color: 'rgba(255, 255, 255, 0.7)',
                        z: 100
                    },
                    min: 0,
                    max: 5,
                    beginAtZero: true
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return context[0].label;
                        },
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw}/5`;
                        }
                    }
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        boxWidth: 15,
                        padding: 15
                    }
                }
            },
            maintainAspectRatio: false
        }
    });
}

/**
 * Creates a bar chart for skills data
 * @param {string} elementId - Canvas element ID
 * @param {Array} labels - Chart labels
 * @param {Array} data - Chart data values
 * @param {string} title - Chart title
 */
function createBarChart(elementId, labels, data, title) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Format the labels to be title case
    const formattedLabels = labels.map(label => {
        return label.split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    });
    
    // Create the chart
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: formattedLabels,
            datasets: [{
                label: title,
                data: data,
                backgroundColor: 'rgba(13, 110, 253, 0.7)',
                borderColor: 'rgba(13, 110, 253, 1)',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    max: 5,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Score: ${context.raw}/5`;
                        }
                    }
                }
            },
            maintainAspectRatio: false
        }
    });
}

/**
 * Creates a doughnut chart for resume score
 * @param {string} elementId - Canvas element ID
 * @param {number} score - Resume score value (0-10)
 */
function createResumeScoreChart(elementId, score) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Determine color based on score
    let color;
    if (score >= 8) {
        color = 'rgba(25, 135, 84, 0.8)'; // Success/Green
    } else if (score >= 5) {
        color = 'rgba(255, 193, 7, 0.8)'; // Warning/Yellow
    } else {
        color = 'rgba(220, 53, 69, 0.8)'; // Danger/Red
    }
    
    // Create the chart
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Score', 'Remaining'],
            datasets: [{
                data: [score, 10 - score],
                backgroundColor: [
                    color,
                    'rgba(255, 255, 255, 0.1)'
                ],
                borderWidth: 0
            }]
        },
        options: {
            cutout: '75%',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            },
            maintainAspectRatio: true,
            rotation: -90,
            circumference: 180,
            responsive: true
        }
    });
}

/**
 * Creates a pie chart for interest categories
 * @param {string} elementId - Canvas element ID
 * @param {Object} interestsData - Interest categories data
 */
function createInterestsPieChart(elementId, interestsData) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Prepare data from interests
    const labels = Object.keys(interestsData).map(key => {
        return key.replace('interest_', '').charAt(0).toUpperCase() + key.replace('interest_', '').slice(1);
    });
    const data = Object.values(interestsData);
    
    // Colors for different interest categories
    const backgroundColors = [
        'rgba(13, 110, 253, 0.7)',  // Primary/Blue
        'rgba(111, 66, 193, 0.7)',   // Purple
        'rgba(32, 201, 151, 0.7)',   // Teal
        'rgba(253, 126, 20, 0.7)',   // Orange
        'rgba(13, 202, 240, 0.7)'    // Info/Light blue
    ];
    
    // Create the chart
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: backgroundColors,
                borderColor: 'rgba(33, 37, 41, 0.2)',
                borderWidth: 1
            }]
        },
        options: {
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        boxWidth: 15,
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Interest Level: ${context.raw}/5`;
                        }
                    }
                }
            },
            maintainAspectRatio: false
        }
    });
}
