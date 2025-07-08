const qmarks = Array.from(document.querySelectorAll('.qmark'));
const winnerText = document.getElementById('winnerDisplay');
const awaitingText = document.getElementById('awaitingText');
const winnerButton = document.getElementById('winnerButton');

// Audio setup
const preludeAudio = new Audio("/static/sounds/prelude.mp3");
const loopAudio = new Audio("/static/sounds/loop.mp3");
const winnerAudio = new Audio("/static/sounds/winner.mp3");
loopAudio.loop = true;

function stopAllAudio() {
  [preludeAudio, loopAudio, winnerAudio].forEach(audio => {
    audio.pause();
    audio.currentTime = 0;
  });
}

function clearVisuals() {
  qmarks.forEach(q => q.classList.remove('visible'));
  winnerText.classList.remove('visible');
  awaitingText.classList.remove('visible');
  winnerText.textContent = '';
  winnerButton.classList.remove('visible');
  winnerButton.textContent = '';
}

function animateQuestionMarks() {
  clearVisuals();
  awaitingText.classList.add('visible');
  qmarks.forEach((q, i) => {
    setTimeout(() => q.classList.add('visible'), i * 200);
  });
}

// Pre-authorize audio on first interaction
document.addEventListener('click', () => {
  [preludeAudio, loopAudio, winnerAudio].forEach(a => {
    a.play().catch(() => {});
    a.pause();
  });
}, { once: true });

// Handle socket events
socket.on('projector_state', data => {
  if (data.state === 'clear') {
    clearVisuals();
    stopAllAudio();
  } else if (data.state === 'awaiting') {
    clearVisuals();
    stopAllAudio();
    animateQuestionMarks();

    preludeAudio.play().then(() => {
      preludeAudio.onended = () => {
        loopAudio.play().catch(err => console.warn("Loop play failed:", err));
      };
    }).catch(err => {
      console.warn("Prelude play failed:", err);
      loopAudio.play();
    });

  } else if (data.state === 'winner') {
    clearVisuals();
    stopAllAudio();
    winnerText.textContent = `Winner: ${data.name}`;
    winnerText.classList.add('visible');
    winnerButton.textContent = `Button ${data.button}`;
    winnerButton.classList.add('visible');
    winnerAudio.play();
  }
});
