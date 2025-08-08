document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('prediction-form');
    const resultBox = document.getElementById('result-box');
    const resultText = document.getElementById('prediction-result');
    const riskLevels = document.querySelectorAll('.risk-level');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validate inputs
        const inputs = form.querySelectorAll('input[required], select[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('error');
                isValid = false;
            } else {
                input.classList.remove('error');
            }
        });
        
        if (!isValid) {
            alert('Please fill in all required fields');
            return;
        }

        // Show loading state
        form.querySelector('button').textContent = 'Processing...';
        form.querySelector('button').disabled = true;

        try {
            // Send prediction request
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams(new FormData(form))
            });

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            // Display results
            resultText.textContent = data.prediction;
            
            // Update risk meter
            const riskValue = data.prediction.includes('High') ? 2 : 
                            data.prediction.includes('Medium') ? 1 : 0;
            
            riskLevels.forEach((level, index) => {
                level.style.opacity = index === riskValue ? '1' : '0.2';
            });
            
            resultBox.style.display = 'block';
            
            // Scroll to results
            resultBox.scrollIntoView({ behavior: 'smooth' });
            
        } catch (error) {
            console.error('Prediction error:', error);
            alert('An error occurred. Please try again.');
        } finally {
            // Reset form button
            form.querySelector('button').textContent = 'Predict Risk';
            form.querySelector('button').disabled = false;
        }
    });

    // Input validation
    form.querySelectorAll('input, select').forEach(input => {
        input.addEventListener('input', function() {
            if (this.value.trim()) {
                this.classList.remove('error');
            }
        });
    });
});