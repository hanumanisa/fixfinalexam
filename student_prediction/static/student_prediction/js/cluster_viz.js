document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/instructor_clusters/')
        .then(response => response.json())
        .then(data => {
            document.getElementById('statusBox').textContent = 'Visualization of K Means Clustering Results on Data Instructor';
            renderScatterPlot(data);
        })
        .catch(error => {
            console.error('Error fetching cluster data:', error);
            document.getElementById('statusBox').textContent = 'Failed to load cluster data';
        });

    function renderScatterPlot(data) {
        const ctx = document.getElementById('scatterChart').getContext('2d');

        const allPoints = [...data.cluster_0_points, ...data.cluster_1_points, ...data.cluster_2_points];
        const grades = allPoints.map(p => p.x);
        const attendances = allPoints.map(p => p.y);
        const gradeMin = Math.min(...grades) - 2;
        const gradeMax = Math.max(...grades) + 2;
        const attendanceMin = Math.min(...attendances) - 2;
        const attendanceMax = Math.max(...attendances) + 2;

        new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [
                    {
                        label: 'Cluster 0 (High Performance)',
                        data: data.cluster_0_points,
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1,
                        pointRadius: 8,
                        pointHoverRadius: 10
                    },
                    {
                        label: 'Cluster 1 (Medium Performance)',
                        data: data.cluster_1_points,
                        backgroundColor: 'rgba(75, 192, 192, 0.7)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1,
                        pointRadius: 8,
                        pointHoverRadius: 10
                    },
                    {
                        label: 'Cluster 2 (Low Performance)',
                        data: data.cluster_2_points,
                        backgroundColor: 'rgba(255, 99, 132, 0.7)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1,
                        pointRadius: 10,
                        pointHoverRadius: 12
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Instructor Performance Cluster Visualization',
                        font: { 
                            size: 18,
                            weight: 'bold'
                        },
                        padding: {
                            top: 10,
                            bottom: 20
                        }
                    },
                    legend: {
                        position: 'top',
                        labels: {
                            font: {
                                size: 12
                            },
                            padding: 20
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const point = context.raw;
                                return [
                                    `Instructor: ${point.instructor}`,
                                    `Grade: ${point.x.toFixed(2)}`,
                                    `Attendance: ${point.y.toFixed(2)}%`,
                                    `Difficulty: ${point.difficulty || 'N/A'}`,  // Tambahan label difficulty level
                                    `Semester: ${point.semester || 'N/A'}`,
                                    `Total Student: ${point.total_student || 'NA'}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Average Grade',
                            font: { 
                                weight: 'bold',
                                size: 14
                            }
                        },
                        min: gradeMin,
                        max: gradeMax,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Average Attendance (%)',
                            font: { 
                                weight: 'bold',
                                size: 14
                            }
                        },
                        min: attendanceMin,
                        max: attendanceMax,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                },
                elements: {
                    point: {
                        hoverBorderWidth: 2
                    }
                }
            }
        });
    }
});
