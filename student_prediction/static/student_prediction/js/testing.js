document.getElementById('predictionForm').addEventListener('submit', function(e) {
                e.preventDefault();
                // Get form data
                const formData = new FormData(this);
                
                // Send AJAX request
                fetch('/predict-cluster/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    // Display result
                    console.log("Prediction Result: ", data);
                    document.getElementById('clusterResult').textContent = `Cluster ${data.cluster}`;
                    document.getElementById('clusterDescription').textContent = getClusterDescription(data.cluster);
                    document.getElementById('predictionResult').style.display = 'block';

                })
                .catch(error => console.error('Error:', error));
            });
        
            document.getElementById('clearButton').addEventListener('click', function() {
                document.getElementById('predictionForm').reset();
                document.getElementById('predictionResult').style.display = 'none';
                document.getElementById('clusterResult').textContent = '';
                document.getElementById('clusterDescription').textContent = '';
            });

            function getClusterDescription(cluster) {
                const descriptions = {
                    0: "High performance - instructors with excellent grades and attendance",
                    1: "Average performance - instructors with moderate grades and attendance",
                    2: "Low performance - instructors needing improvement in grades or attendance"
                };
                return descriptions[cluster] || "Unknown cluster";
            }