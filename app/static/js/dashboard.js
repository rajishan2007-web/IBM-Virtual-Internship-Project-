// JavaScript Helper for Student & Faculty Dashboards (Chart.js setup)

function renderStudentCharts(labels, marksData, attData) {
    // Marks Chart
    const marksCtx = document.getElementById('studentMarksChart');
    if (marksCtx) {
        new Chart(marksCtx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Subject Percentage (%)',
                    data: marksData,
                    backgroundColor: 'rgba(37, 99, 235, 0.7)',
                    borderColor: 'rgba(37, 99, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    // Attendance Chart
    const attCtx = document.getElementById('studentAttChart');
    if (attCtx) {
        new Chart(attCtx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Attendance Percentage (%)',
                    data: attData,
                    backgroundColor: 'rgba(16, 185, 129, 0.7)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
}

function renderAnalyticsCharts(subjectNames, marksData, attData, performanceCounts) {
    // Subject Comparison Chart
    const subjCtx = document.getElementById('subjectComparisonChart');
    if (subjCtx) {
        new Chart(subjCtx, {
            type: 'bar',
            data: {
                labels: subjectNames,
                datasets: [
                    {
                        label: 'Average Marks (%)',
                        data: marksData,
                        backgroundColor: 'rgba(59, 130, 246, 0.7)',
                        borderColor: 'rgba(59, 130, 246, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Average Attendance (%)',
                        data: attData,
                        backgroundColor: 'rgba(16, 185, 129, 0.7)',
                        borderColor: 'rgba(16, 185, 129, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    // Performance Breakdown Doughnut Chart
    const perfCtx = document.getElementById('performancePieChart');
    if (perfCtx) {
        new Chart(perfCtx, {
            type: 'doughnut',
            data: {
                labels: ['Good Performance', 'Average Performance', 'Needs Attention'],
                datasets: [{
                    data: performanceCounts,
                    backgroundColor: [
                        'rgba(22, 163, 74, 0.8)',
                        'rgba(202, 138, 4, 0.8)',
                        'rgba(220, 38, 38, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true
            }
        });
    }
}
