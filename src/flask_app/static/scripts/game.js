let currentThrow = 0; // 0 for no throws, 1-3 for current throw number
let multiplier = 1; // 1 for single, 2 for double, 3 for triple
let currentPlayer = 0; // 0 for Player A, 1 for Player B
let isCountdownActive = false; // Track if countdown is active
let action = '';
let lastThrows = [];

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
    const playerAScore = document.getElementById("playerA_score");
    const playerBScore = document.getElementById("playerB_score");
    
    if (!playerAScore || !playerBScore) {
        console.error("Score elements not found in DOM:", {
            playerAExists: !!playerAScore,
            playerBExists: !!playerBScore
        });
    }
    
    if (playerAScore) playerAScore.textContent = data.scoreA;
    if (playerBScore) playerBScore.textContent = data.scoreB;
    
    // Update throws and calculate sum
    let roundSum = 0;
    for (let i = 0; i < 3; i++) {
        const throwValue = data.currentThrows[i];
        document.getElementById('throw' + (i + 1)).textContent = throwValue || '-';
        console.log("throwValue:", throwValue);
        
        // Add to sum if it's a valid throw
        if (throwValue && throwValue !== '-' && throwValue !== 'BUST') {
            // Handle prefixed scores (S5, D20, T20)
            if (throwValue.startsWith('S')) {
                roundSum += parseInt(throwValue.substring(1));
            } else if (throwValue.startsWith('D')) {
                roundSum += parseInt(throwValue.substring(1)) * 2;
            } else if (throwValue.startsWith('T')) {
                roundSum += parseInt(throwValue.substring(1)) * 3;
            } else {
                // For regular scores without prefix
                roundSum += parseInt(throwValue);
            }
        }
    }

    // Update round sum
    const roundSumElement = document.getElementById('round-sum');
    if (roundSumElement) {
        roundSumElement.textContent = roundSum;
    }
  
    // Handle win condition
    if (data.justWon) {
        const winner = data.winnerIndex === 0 ? 'Player A' : 'Player B';
        alert(winner + ' has won the game!');
        // Redirect to homepage after alert is closed
        window.location.href = '/';
    }
}


function selectField(type, button) {
    if (type === 'Undo') {
        fetch('/undo_throw', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            console.log("Data Undo:", data);
            if (data.success) {
                currentThrow--;
                console.log(currentThrow);
                // Update the displays
                updateDisplay(data);
                // updateTotals(data.totals);
            } else {
                console.error(data.error);
            }
        })
        .catch(error => console.error('Error:', error));
        return;
    }
    
    // Reset all button styles
    document.getElementById('double').style.backgroundColor = '';
    document.getElementById('triple').style.backgroundColor = '';
    // Re-enable bull button
    document.getElementById('bull-button').disabled = false;
    
    if (type === 'Double') {
        multiplier = button.style.backgroundColor ? 1 : 2;
        button.style.backgroundColor = multiplier === 2 ? '#ff7a18' : '';
    } else if (type === 'Triple') {
        multiplier = button.style.backgroundColor ? 1 : 3;
        button.style.backgroundColor = multiplier === 3 ? '#ff7a18' : '';
        // Disable bull button when triple is selected
        document.getElementById('bull-button').disabled = multiplier === 3;
    }
}

function handleScore(score) {
    if (currentThrow <= 3) {
        currentThrow++;
        
        fetch('/throw?' + new URLSearchParams({
            throwNumber: currentThrow,
            score: score,
            multiplier: multiplier
        }))
        .then(response => response.json())
        .then(data => {
            updateDisplay(data);
            console.log(data);

            // Check for BUST and show popup
            if (data.isBust) {
                alert('BUST! Player score reverted. Next player\'s turn.');
            }
            
            // Check if round is complete (3 throws or BUST)
            if (data.isRoundComplete) {
                // Only switch players if we have 3 throws OR a BUST occurred
                if (currentThrow === 3 || data.isBust) {
                    currentThrow = 0;  // Reset throw counter
                    currentPlayer = (currentPlayer + 1) % 2;  // Switch player
                    updatePlayerTurn();
                    lastThrows = [];
                }
            }
            
            // Reset multiplier
            multiplier = 1;
            document.getElementById('double').style.backgroundColor = '';
            document.getElementById('triple').style.backgroundColor = '';
            document.getElementById('bull-button').disabled = false;  // Re-enable bull button when resetting
        });
    } else {
        alert('You have already made three throws. Please click Next.');
    }
}

// Initialize the game
document.addEventListener('DOMContentLoaded', function() {
    updatePlayerTurn();
});