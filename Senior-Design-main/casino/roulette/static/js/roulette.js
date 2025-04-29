document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('roulette-wheel');
    const ctx = canvas.getContext('2d');
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 10;

    const segments = [
        { number: 0, color: 'green' },
        { number: 32, color: 'red' },
        { number: 15, color: 'black' },
        { number: 19, color: 'red' },
        { number: 4, color: 'black' },
        { number: 21, color: 'red' },
        { number: 2, color: 'black' },
        { number: 25, color: 'red' },
        { number: 17, color: 'black' },
        { number: 34, color: 'red' },
        { number: 6, color: 'black' },
        { number: 27, color: 'red' },
        { number: 13, color: 'black' },
        { number: 36, color: 'red' },
        { number: 11, color: 'black' },
        { number: 30, color: 'red' },
        { number: 8, color: 'black' },
        { number: 23, color: 'red' },
        { number: 10, color: 'black' },
        { number: 5, color: 'red' },
        { number: 24, color: 'black' },
        { number: 16, color: 'red' },
        { number: 33, color: 'black' },
        { number: 1, color: 'red' },
        { number: 20, color: 'black' },
        { number: 14, color: 'red' },
        { number: 31, color: 'black' },
        { number: 9, color: 'red' },
        { number: 22, color: 'black' },
        { number: 18, color: 'red' },
        { number: 29, color: 'black' },
        { number: 7, color: 'red' },
        { number: 28, color: 'black' },
        { number: 12, color: 'red' },
        { number: 35, color: 'black' },
        { number: 3, color: 'red' },
        { number: 26, color: 'black' },
    ];

    function drawRouletteWheel() {
        const arc = (2 * Math.PI) / segments.length;

        segments.forEach((segment, index) => {
            const startAngle = index * arc;
            const endAngle = startAngle + arc;

            // Draw segment
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, startAngle, endAngle);
            ctx.lineTo(centerX, centerY);
            ctx.fillStyle = segment.color;
            ctx.fill();
            ctx.stroke();

            // Draw number
            const textAngle = startAngle + arc / 2;
            const textX = centerX + (radius - 30) * Math.cos(textAngle);
            const textY = centerY + (radius - 30) * Math.sin(textAngle);
            ctx.fillStyle = 'white';
            ctx.font = '14px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(segment.number, textX, textY);
        });
    }

    function drawBall(angle) {
        const ballRadius = 10;
        const ballX = centerX + (radius - 15) * Math.cos(angle);
        const ballY = centerY + (radius - 15) * Math.sin(angle);

        ctx.beginPath();
        ctx.arc(ballX, ballY, ballRadius, 0, 2 * Math.PI);
        ctx.fillStyle = 'white';
        ctx.fill();
        ctx.stroke();
    }

    drawRouletteWheel();

    const chips = document.querySelectorAll('.chip');
    const bettingCells = document.querySelectorAll('.betting-cell');
    const selectedAmountDisplay = document.getElementById('selected-amount');
    const betTypeInput = document.getElementById('bet_type');
    const valueInput = document.getElementById('value');
    const amountInput = document.getElementById('amount');
    const placeBetButton = document.getElementById('place-bet-button');
    const resultSection = document.querySelector('.result');
    const lastSpinsTable = document.querySelector('.last-spins tbody');

    let selectedChip = null;

    // Handle chip selection
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            chips.forEach(c => c.classList.remove('selected'));
            chip.classList.add('selected');
            selectedChip = chip.dataset.value;
            selectedAmountDisplay.textContent = `Selected Amount: ${selectedChip} chips`;
        });
    });

    // Handle betting cell clicks
    bettingCells.forEach(cell => {
        cell.addEventListener('click', () => {
            if (!selectedChip) {
                alert('Please select a chip value first!');
                return;
            }

            // Determine the bet type and value based on the cell's attributes
            const betType = cell.dataset.bet;
            const betValue = cell.dataset.value;

            // Set the bet type and value in the hidden inputs
            betTypeInput.value = betType;
            valueInput.value = betValue;
            amountInput.value = selectedChip;

        });
    });

    // Handle placing a bet
    placeBetButton.addEventListener('click', event => {
        event.preventDefault();

        const formData = new FormData();
        formData.append('bet_type', betTypeInput.value);
        formData.append('value', valueInput.value);
        formData.append('amount', amountInput.value);

        fetch('/roulette/roulette/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCsrfToken(), // Include CSRF token
            },
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Spin the wheel
                    spinWheel(data.number);

                    // Update the "Last 5 Spins" table
                    updateLastSpinsTable(data.last_spins);

                    // Update the balance and results dynamically
                    updateResults(data);
                } else {
                    console.log('Error:', data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error.message || error);
                alert(`An error occurred while placing the bet: ${error.message || error}`);
            });
    });

    function spinWheel(spinResult) {
        const segmentIndex = segments.findIndex(segment => segment.number === spinResult);

        if (segmentIndex === -1) {
            console.error('Spin result not found in segments.');
            alert('Error: Spin result not found in segments.');
            return;
        }

        const arc = (2 * Math.PI) / segments.length;
        const targetAngle = segmentIndex * arc + arc / 2; // Center the result in the segment
        const totalSpins = 5; // Number of full spins before stopping
        const finalAngle = totalSpins * 2 * Math.PI + targetAngle;

        let currentAngle = 0;
        let ballAngle = 0;
        const spinSpeed = 0.1;
        const ballSpeed = 0.2;

        function animateSpin() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Draw the wheel
            ctx.save();
            ctx.translate(centerX, centerY);
            ctx.rotate(currentAngle);
            ctx.translate(-centerX, -centerY);
            drawRouletteWheel();
            ctx.restore();

            // Draw the ball
            drawBall(ballAngle);

            if (currentAngle < finalAngle) {
                currentAngle += spinSpeed;
                ballAngle -= ballSpeed; // Ball rotates in the opposite direction
                requestAnimationFrame(animateSpin);
            } else {
                // Ensure the ball stops at the correct position
                ballAngle = targetAngle;
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                drawRouletteWheel();
                drawBall(ballAngle);
            }
        }

        animateSpin();
    }

    function updateLastSpinsTable(lastSpins) {
        lastSpinsTable.innerHTML = ''; // Clear existing rows

        lastSpins.forEach(spin => {
            const row = document.createElement('tr');
            const numberCell = document.createElement('td');
            const colorCell = document.createElement('td');

            numberCell.textContent = spin.number;
            colorCell.textContent = spin.color;

            row.appendChild(numberCell);
            row.appendChild(colorCell);
            lastSpinsTable.appendChild(row);
        });
    }

    function updateResults(data) {
        if (resultSection) {
            resultSection.innerHTML = `
                <h2>🎯 Spin Result:</h2>
                <p><strong>Number:</strong> ${data.number}</p>
                <p><strong>Color:</strong> ${data.spin_color}</p>
                <p><strong>Payout:</strong> ${data.payout} chips</p>
                <p><strong>New Balance:</strong> ${data.new_balance} chips</p>
            `;
        }
    }

    function getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith('csrftoken=')) {
                return cookie.substring('csrftoken='.length, cookie.length);
            }
        }
        return '';
    }
});