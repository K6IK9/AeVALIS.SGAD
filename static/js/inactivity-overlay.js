
let inactivityTimer;

const INACTIVITY_TIME = 60 * 1000; // 1 minuto em milissegundos

function showOverlay() {
    const overlay = document.getElementById('inactivity-overlay');
    if (overlay) {
        overlay.style.display = 'block';
    }
}

function hideOverlay() {
    const overlay = document.getElementById('inactivity-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
    resetTimer();
}

function resetTimer() {
    clearTimeout(inactivityTimer);
    inactivityTimer = setTimeout(showOverlay, INACTIVITY_TIME);
}

// Eventos que resetam o temporizador
window.onload = resetTimer;
document.onmousemove = resetTimer;
document.onmousedown = resetTimer;
document.ontouchstart = resetTimer;
document.onclick = resetTimer;
document.onkeydown = resetTimer;
document.addEventListener('scroll', resetTimer, true);

// Evento para esconder o overlay
document.addEventListener('DOMContentLoaded', () => {
    const overlay = document.getElementById('inactivity-overlay');
    if (overlay) {
        overlay.addEventListener('click', hideOverlay);
    }
});
