document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/instructor_clusters/')
        .then(response => response.json())
        .then(data => {
            document.getElementById('statusBox').textContent = 'Visualization of K-Means Clustering Results on Data Instructor (after PCA)';
            renderScatterPlot(data);
        })
        .catch(error => {
            console.error('Error fetching cluster data:', error);
            document.getElementById('statusBox').textContent = 'Failed to load cluster data';
        });

    
    fetch('/api/silhouette_data/')
        .then(response => response.json())
        .then(data => {
            renderSilhouetteChart(data.ks, data.silhouette_scores);
        })
        .catch(error => {
            console.error('Error fetching silhouette data:', error);
        });

    function renderScatterPlot(data) {
        const ctx = document.getElementById('scatterChart').getContext('2d');

        const allPoints = [...data.cluster_0_points, ...data.cluster_1_points, ...data.cluster_2_points, ...data.cluster_3_points];
        const backgroundColorPlugin = {
            id: 'custom_canvas_background_color',
            beforeDraw: (chart) => {
                const ctx = chart.ctx;
                ctx.save();
                ctx.globalCompositeOperation = 'destination-over';
                ctx.fillStyle = '#f0f0f0'; 
                ctx.fillRect(0, 0, chart.width, chart.height);
                ctx.restore();
            }
        };
        

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
                        label: 'Cluster 1 (Medium to High Performance)',
                        data: data.cluster_1_points,
                        backgroundColor: 'rgba(75, 192, 192, 0.7)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1,
                        pointRadius: 8,
                        pointHoverRadius: 10
                    },
                    {
                        label: 'Cluster 2 (Medium to Low Performance)',
                        data: data.cluster_2_points,
                        backgroundColor: 'rgba(192, 137, 75, 0.7)',
                        borderColor: 'rgba(192, 137, 75, 1)',
                        borderWidth: 1,
                        pointRadius: 8,
                        pointHoverRadius: 10
                    },
                    {
                        label: 'Cluster 3 (Low Performance)',
                        data: data.cluster_3_points,
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
                        text: 'Instructor Clustering Visualization (PCA-Transformed Data)',
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
                                    `Grade: ${point.avg_grade.toFixed(2)}`,
                                    `Attendance: ${point.avg_attendance.toFixed(2)}%`,
                                    `Difficulty: ${point.difficulty || 'N/A'}`,  
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
                            text: 'Principal Component 1',
                            font: { 
                                weight: 'bold',
                                size: 14
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Principal Component 2',
                            font: { 
                                weight: 'bold',
                                size: 14
                            }
                        },
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
            },
            plugins: [backgroundColorPlugin]
        });
    }
// Fungsi render silhouette line chart
    function renderSilhouetteChart(ks, scores) {
        const canvas = document.getElementById('silhouetteChart');
        if (!canvas) {
            console.error("Canvas dengan id 'silhouetteChart' tidak ditemukan!");
            return;
        }

        const ctxLine = canvas.getContext('2d');
        const backgroundColorPlugin = {
            id: 'custom_canvas_background_color',
            beforeDraw: (chart) => {
                const ctx = chart.ctx;
                ctx.save();
                ctx.globalCompositeOperation = 'destination-over';
                ctx.fillStyle = '#f0f0f0'; 
                ctx.fillRect(0, 0, chart.width, chart.height);
                ctx.restore();
            }
        };

        new Chart(ctxLine, {
            type: 'line',
            data: {
                labels: ks,
                datasets: [{
                    label: 'Silhouette Score',
                    data: scores,
                    fill: false,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.3,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: false,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Silhouette Score vs. Number of Clusters',
                        font: {
                            size: 18,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        display: true
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Number of Clusters (k)',
                            font: {
                                weight: 'bold'
                            }
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Silhouette Score',
                            font: {
                                weight: 'bold'
                            }
                        }
                    }
                }
            },
            plugins: [backgroundColorPlugin]
        });
    }
});