// Charts.js - Advanced Chart Implementation for SRMS
// TailAdmin Premium Chart Components

// Chart color schemes
const chartColors = {
    primary: '#3b82f6',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    purple: '#8b5cf6',
    indigo: '#6366f1',
    pink: '#ec4899',
    orange: '#f97316'
};

const gradeColors = {
    'A+': '#10b981',
    'A': '#059669',
    'B+': '#3b82f6',
    'B': '#2563eb',
    'C+': '#f59e0b',
    'C': '#d97706',
    'F': '#ef4444'
};

// Chart default options
const defaultChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom',
            labels: {
                padding: 20,
                usePointStyle: true,
                font: {
                    size: 12
                }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#ffffff',
            bodyColor: '#ffffff',
            cornerRadius: 8,
            padding: 12,
            displayColors: true
        }
    },
    animation: {
        duration: 1000,
        easing: 'easeInOutQuart'
    }
};

// Initialize Dashboard Charts
function initializeDashboardCharts() {
    // Load grade distribution chart
    loadGradeDistributionChart();
    
    // Load monthly results chart
    loadMonthlyResultsChart();
    
    // Load performance trends if available
    loadPerformanceTrends();
}

// Grade Distribution Chart
function loadGradeDistributionChart() {
    const ctx = document.getElementById('gradeChart');
    if (!ctx) return;
    
    fetch('/api/grade-distribution')
        .then(response => response.json())
        .then(data => {
            const labels = Object.keys(data);
            const values = Object.values(data);
            const colors = labels.map(grade => gradeColors[grade] || '#6b7280');
            
            // Filter out zero values
            const filteredData = [];
            const filteredLabels = [];
            const filteredColors = [];
            
            labels.forEach((label, index) => {
                if (values[index] > 0) {
                    filteredLabels.push(label);
                    filteredData.push(values[index]);
                    filteredColors.push(colors[index]);
                }
            });
            
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: filteredLabels,
                    datasets: [{
                        data: filteredData,
                        backgroundColor: filteredColors,
                        borderWidth: 3,
                        borderColor: '#ffffff',
                        hoverBorderWidth: 4
                    }]
                },
                options: {
                    ...defaultChartOptions,
                    cutout: '60%',
                    plugins: {
                        ...defaultChartOptions.plugins,
                        legend: {
                            ...defaultChartOptions.plugins.legend,
                            position: 'right'
                        },
                        tooltip: {
                            ...defaultChartOptions.plugins.tooltip,
                            callbacks: {
                                label: function(context) {
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((context.raw / total) * 100).toFixed(1);
                                    return `${context.label}: ${context.raw} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading grade distribution:', error);
            showChartError(ctx, 'Failed to load grade distribution');
        });
}

// Monthly Results Chart
function loadMonthlyResultsChart() {
    const ctx = document.getElementById('monthlyChart');
    if (!ctx) return;
    
    fetch('/api/monthly-results')
        .then(response => response.json())
        .then(data => {
            const labels = data.map(item => item.month);
            const values = data.map(item => item.count);
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Results Added',
                        data: values,
                        borderColor: chartColors.primary,
                        backgroundColor: `${chartColors.primary}20`,
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: chartColors.primary,
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }]
                },
                options: {
                    ...defaultChartOptions,
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            },
                            ticks: {
                                font: {
                                    size: 12
                                }
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                font: {
                                    size: 12
                                }
                            }
                        }
                    },
                    plugins: {
                        ...defaultChartOptions.plugins,
                        tooltip: {
                            ...defaultChartOptions.plugins.tooltip,
                            callbacks: {
                                label: function(context) {
                                    return `Results: ${context.raw}`;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading monthly results:', error);
            showChartError(ctx, 'Failed to load monthly results');
        });
}

// Performance Trends Chart
function loadPerformanceTrends() {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;
    
    // Sample data for performance trends
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    const avgScores = [78, 82, 75, 88, 85, 90];
    const passRates = [85, 90, 80, 95, 92, 98];
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: months,
            datasets: [
                {
                    label: 'Average Score (%)',
                    data: avgScores,
                    backgroundColor: `${chartColors.success}80`,
                    borderColor: chartColors.success,
                    borderWidth: 2,
                    borderRadius: 6,
                    borderSkipped: false,
                },
                {
                    label: 'Pass Rate (%)',
                    data: passRates,
                    backgroundColor: `${chartColors.primary}80`,
                    borderColor: chartColors.primary,
                    borderWidth: 2,
                    borderRadius: 6,
                    borderSkipped: false,
                }
            ]
        },
        options: {
            ...defaultChartOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                ...defaultChartOptions.plugins,
                tooltip: {
                    ...defaultChartOptions.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw}%`;
                        }
                    }
                }
            }
        }
    });
}

// Subject Performance Radar Chart
function createSubjectPerformanceChart(elementId, data) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    
    const subjects = Object.keys(data);
    const scores = Object.values(data);
    
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: subjects,
            datasets: [{
                label: 'Performance',
                data: scores,
                backgroundColor: `${chartColors.primary}30`,
                borderColor: chartColors.primary,
                borderWidth: 2,
                pointBackgroundColor: chartColors.primary,
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6
            }]
        },
        options: {
            ...defaultChartOptions,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    pointLabels: {
                        font: {
                            size: 12
                        }
                    },
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// Student Progress Chart
function createStudentProgressChart(elementId, studentData) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    
    const dates = studentData.map(item => item.date);
    const scores = studentData.map(item => item.score);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Score Progression',
                data: scores,
                borderColor: chartColors.success,
                backgroundColor: `${chartColors.success}20`,
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: scores.map(score => {
                    if (score >= 90) return gradeColors['A+'];
                    if (score >= 80) return gradeColors['A'];
                    if (score >= 70) return gradeColors['B+'];
                    if (score >= 60) return gradeColors['B'];
                    return gradeColors['F'];
                }),
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6
            }]
        },
        options: {
            ...defaultChartOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Class Performance Comparison Chart
function createClassComparisonChart(elementId, classData) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    
    const subjects = classData.map(item => item.subject);
    const classAvg = classData.map(item => item.classAverage);
    const studentScore = classData.map(item => item.studentScore);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: subjects,
            datasets: [
                {
                    label: 'Class Average',
                    data: classAvg,
                    backgroundColor: `${chartColors.primary}60`,
                    borderColor: chartColors.primary,
                    borderWidth: 1
                },
                {
                    label: 'Your Score',
                    data: studentScore,
                    backgroundColor: `${chartColors.success}60`,
                    borderColor: chartColors.success,
                    borderWidth: 1
                }
            ]
        },
        options: {
            ...defaultChartOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Error handling for charts
function showChartError(ctx, message) {
    const container = ctx.parentElement;
    container.innerHTML = `
        <div class="flex flex-col items-center justify-center h-64 text-gray-500">
            <i class="fas fa-chart-line text-4xl mb-2"></i>
            <p class="text-sm">${message}</p>
            <button onclick="location.reload()" class="mt-2 text-blue-600 hover:text-blue-800 text-sm">
                <i class="fas fa-redo mr-1"></i>Retry
            </button>
        </div>
    `;
}

// Utility function to create animated counters
function animateCounter(elementId, targetValue, duration = 2000) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const startValue = 0;
    const increment = targetValue / (duration / 16);
    let currentValue = startValue;
    
    const timer = setInterval(() => {
        currentValue += increment;
        if (currentValue >= targetValue) {
            currentValue = targetValue;
            clearInterval(timer);
        }
        element.textContent = Math.round(currentValue);
    }, 16);
}

// Initialize chart themes
function initializeChartThemes() {
    // Set Chart.js global defaults
    Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif";
    Chart.defaults.color = '#374151';
    Chart.defaults.borderColor = '#e5e7eb';
    
    // Custom gradient creation
    Chart.register({
        id: 'gradients',
        beforeDraw: (chart) => {
            const { ctx, chartArea: { top, bottom, left, right } } = chart;
            
            chart.data.datasets.forEach((dataset, index) => {
                if (dataset.type === 'line' && dataset.fill) {
                    const gradient = ctx.createLinearGradient(0, top, 0, bottom);
                    gradient.addColorStop(0, `${dataset.borderColor}40`);
                    gradient.addColorStop(1, `${dataset.borderColor}00`);
                    dataset.backgroundColor = gradient;
                }
            });
        }
    });
}

// Initialize responsive chart behavior
function initializeResponsiveCharts() {
    const resizeObserver = new ResizeObserver(entries => {
        for (let entry of entries) {
            const canvas = entry.target.querySelector('canvas');
            if (canvas && canvas.chart) {
                canvas.chart.resize();
            }
        }
    });
    
    // Observe all chart containers
    document.querySelectorAll('[id$="Chart"]').forEach(container => {
        resizeObserver.observe(container.parentElement);
    });
}

// Export functions for global use
window.Charts = {
    initializeDashboardCharts,
    createSubjectPerformanceChart,
    createStudentProgressChart,
    createClassComparisonChart,
    animateCounter,
    gradeColors,
    chartColors
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeChartThemes();
    initializeResponsiveCharts();
});
