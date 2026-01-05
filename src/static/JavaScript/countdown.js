// 3 min countdown in secs
let timeLeft = 180; 
        
const countdownEl = document.getElementById("countdown");

// Declare mins and secs    
function updateTimer() {
    const mins = String(Math.floor(timeLeft / 60)).padStart(2, '0');
    const secs = String(timeLeft % 60).padStart(2, '0');
    countdownEl.textContent = `${mins}:${secs}`;
}
        
updateTimer();

// Continue countdown or clear
const timer = setInterval(() => {
    timeLeft--;

    if (timeLeft < 0) {
        clearInterval(timer);
        window.location.href = "/";
        
    } else {
        updateTimer();
    }

// Updates every 1000 millisecs
}, 1000);