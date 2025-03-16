let currentThrow = 1;
let multiplier = 1;
let currentPlayer = 0; // 0 for Player A, 1 for Player B
let isCountdownActive = false; // Track if countdown is active

// Update the UI to show current player's turn
function updatePlayerTurn() {
    document.querySelectorAll('.player-box').forEach((box, index) => {
        if (index === currentPlayer) {
            box.classList.add('active');
        } else {
            box.classList.remove('active');
        }
    });
}

// Update scores and throws display
function updateDisplay(data) {
    // Update scores
    document.getElementById("playerA_score").textContent = data.scoreA;
    document.getElementById("playerB_score").textContent = data.scoreB;
    
    // Update throws and calculate sum
    let roundSum = 0;
    for (let i = 0; i < 3; i++) {
        const throwValue = data.currentThrows[i];
        document.getElementById('throw' + (i + 1)).textContent = throwValue || '-';
        
        // Add to sum if it's a valid throw
        if (throwValue && throwValue !== '-' && throwValue !== 'BUST') {
            // For multiplied scores (e.g., "2×20")
            if (throwValue.includes('×')) {
                const [multiplier, score] = throwValue.split('×');
                roundSum += parseInt(multiplier) * parseInt(score);
            } else {
                // For regular scores
                roundSum += parseInt(throwValue) || 0;
            }
        }
    }
    
    // Update round sum
    document.getElementById('round-sum').textContent = roundSum || 0;
    
    // Handle round completion
    if (currentThrow === 3 && !isCountdownActive) {
        // Store the current values before starting countdown
        const lastThrows = [];
        for (let i = 1; i <= 3; i++) {
            lastThrows[i-1] = document.getElementById('throw' + i).textContent;
        }
        const lastRoundSum = document.getElementById('round-sum').textContent;

        // Start countdown
        if (isCountdownActive) return; // Prevent multiple countdowns
        isCountdownActive = true;

        // Disable all dart board buttons during countdown
        const dartButtons = document.querySelectorAll('.dart-board button');
        dartButtons.forEach(btn => btn.disabled = true);
        
        // Create and show countdown element
        const countdown = document.createElement('div');
        countdown.id = 'countdown';
        countdown.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: rgba(54, 52, 52, 0.8);
            color: white;
            padding: 20px 40px;
            border-radius: 10px;
            font-size: 24px;
            z-index: 1000;
        `;
        document.body.appendChild(countdown);
        
        // Start 10 second countdown
        let timeLeft = 10;
        const countdownInterval = setInterval(() => {
            countdown.textContent = `Next player in ${timeLeft} seconds...`;
            // Keep showing the last throws during countdown - not working
            for (let i = 1; i <= 3; i++) {
                document.getElementById('throw' + i).textContent = lastThrows[i-1];
            }
            document.getElementById('round-sum').textContent = lastRoundSum;
            
            timeLeft--;
            
            if (timeLeft < 0) {
                clearInterval(countdownInterval);
                document.body.removeChild(countdown);
                dartButtons.forEach(btn => btn.disabled = false);
                
                // Reset throws and round total only after countdown - not working
                document.getElementById('round-sum').textContent = "0";
                for (let i = 1; i <= 3; i++) {
                    document.getElementById('throw' + i).textContent = "-";
                }
                
                // Switch to next player
                currentThrow = 1;
                currentPlayer = (currentPlayer + 1) % 2;
                updatePlayerTurn();
                isCountdownActive = false;
            }
        }, 1000);
    } else if (!isCountdownActive) {
        // Normal throw increment
        currentThrow++;
    }
    
    // Handle win condition
    if (data.justWon) {
        const winner = data.winderIndex === 0 ? 'Player A' : 'Player B';
        alert(winner + ' has won the game!');
        // Disable throw buttons
        document.querySelectorAll('.dart-board button').forEach(btn => {
            btn.disabled = true;
        });
    }
}

function selectField(type, button) {
    if (type === 'Undo') {
        fetch('/undo')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (currentThrow > 1) currentThrow--;
                    // Reset multiplier
                    multiplier = 1;
                    document.getElementById('double').style.backgroundColor = '';
                    document.getElementById('triple').style.backgroundColor = '';
                }
            });
        return;
    }
    
    if (type === 'Next') {
        if (currentThrow < 3) {
            alert('Please complete your three throws first!');
            return;
        }
        // The countdown will start automatically after the third throw
        return;
    }
    
    // Reset all button styles
    document.getElementById('double').style.backgroundColor = '';
    document.getElementById('triple').style.backgroundColor = '';
    
    if (type === 'Double') {
        multiplier = button.style.backgroundColor ? 1 : 2;
        button.style.backgroundColor = multiplier === 2 ? '#ff7a18' : '';
    } else if (type === 'Triple') {
        multiplier = button.style.backgroundColor ? 1 : 3;
        button.style.backgroundColor = multiplier === 3 ? '#ff7a18' : '';
    }
}

function handleScore(score) {
    if (currentThrow <= 3) {
        fetch('/throw?' + new URLSearchParams({
            throwNumber: currentThrow,
            score: score,
            multiplier: multiplier
        }))
        .then(response => response.json())
        .then(data => {
            updateDisplay(data);
            
            // Reset multiplier
            multiplier = 1;
            document.getElementById('double').style.backgroundColor = '';
            document.getElementById('triple').style.backgroundColor = '';
        });
    }
}

// Initialize the game
document.addEventListener('DOMContentLoaded', function() {
    updatePlayerTurn();
});