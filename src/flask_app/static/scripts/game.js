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

    // Handle round completion
    if (currentThrow === 3 && !isCountdownActive) {
        console.log(currentThrow)
        const lastRoundSum = roundSum; // Store the actual calculated sum

        // Start countdown
        if (isCountdownActive) return; // Prevent multiple countdowns
        isCountdownActive = true;

        // Disable all dart board buttons during countdown
        const dartButtons = document.querySelectorAll('.dart-board button');
        dartButtons.forEach(btn => btn.disabled = true);
        
        // Create and show countdown element
        const countdown = document.createElement('div');
        countdown.id = 'countdown';
        countdown.classList.add('countdown-overlay');
        document.body.appendChild(countdown);
        
        // Start 5 second countdown
        let timeLeft = 5;
        const countdownInterval = setInterval(() => {
            countdown.textContent = `Next player in ${timeLeft} seconds...`;
            // Keep showing the last throws during countdown - not working
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
                currentThrow = 0;
                console.log(currentThrow)
                currentPlayer = (currentPlayer + 1) % 2;
                updatePlayerTurn();
                isCountdownActive = false;
            }
        }, 1000);
    } else     
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
    // Change the condition to check if currentThrow is less than 3
    if (currentThrow <= 3) {
        // Increment currentThrow before making the throw
        currentThrow++;
        console.log(currentThrow)        
        // Send data to server
        fetch('/throw?' + new URLSearchParams({
            throwNumber: currentThrow,
            score: score,
            multiplier: multiplier
        }))
        // receive response from server with updated data
        .then(response => response.json())
        .then(data => {
            updateDisplay(data);
            console.log(data);
            if (data.isRoundComplete === false) {
                lastThrows.push(data.currentThrows);
            } else {
                lastThrows = [];
            }
            console.log(lastThrows);
            // Reset multiplier
            multiplier = 1;
            document.getElementById('double').style.backgroundColor = '';
            document.getElementById('triple').style.backgroundColor = '';
        });
    } else {
        alert('You have already made three throws. Please click Next.');
    }
}

// Initialize the game
document.addEventListener('DOMContentLoaded', function() {
    updatePlayerTurn();
});

// Update total scores for both players with undo functionality
// TODO: should be moved into updateDisplay
// function updateTotals(totals) {
    
//     document.getElementById('playerA_score').textContent = totals[0];
//     document.getElementById('playerB_score').textContent = totals[1];
// }