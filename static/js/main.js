document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form'); // Changed from getElementById
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
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.textContent = 'Processing...';
        submitButton.disabled = true;

        try {
            // Send prediction request - removed Content-Type header
            const response = await fetch('/predict', {
                method: 'POST',
                body: new FormData(form) // Just send FormData directly
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            // Display results
            resultText.innerHTML = data.prediction;
            
            // Update risk meter (simplified for binary outcome)
            const isHighRisk = data.prediction.includes('High');
            riskLevels.forEach((level, index) => {
                // For binary risk: index 0=Low, 2=High
                if ((isHighRisk && index === 2) || (!isHighRisk && index === 0)) {
                    level.style.opacity = '1';
                    level.style.fontWeight = 'bold';
                } else {
                    level.style.opacity = '0.3';
                    level.style.fontWeight = 'normal';
                }
            });
            
            resultBox.style.display = 'block';
            
            // Scroll to results
            resultBox.scrollIntoView({ behavior: 'smooth' });
            
        } catch (error) {
            console.error('Prediction error:', error);
            alert('Error: ' + error.message);
        } finally {
            // Reset form button
            submitButton.textContent = originalText;
            submitButton.disabled = false;
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