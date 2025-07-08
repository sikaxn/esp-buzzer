const qmarks = Array.from(document.querySelectorAll('.qmark'));
const winnerText = document.getElementById('winnerDisplay');
const awaitingText = document.getElementById('awaitingText');
const winnerButton = document.getElementById('winnerButton');

// Audio sources
const preludeTracks = [
  "/static/sounds/prelude_1.mp3", "/static/sounds/prelude_2.mp3",
  "/static/sounds/prelude_3.mp3", "/static/sounds/prelude_4.mp3",
  "/static/sounds/prelude_5.mp3", "/static/sounds/prelude_6.mp3"
];

const loopTracks = [
  "/static/sounds/loop_1.mp3", "/static/sounds/loop_2.mp3", "/static/sounds/loop_3.mp3",
  "/static/sounds/loop_4.mp3", "/static/sounds/loop_5.mp3", "/static/sounds/loop_6.mp3"
];

const winnerTracks = [
  "/static/sounds/winner_1.mp3", "/static/sounds/winner_2.mp3", "/static/sounds/winner_3.mp3",
  "/static/sounds/winner_4.mp3", "/static/sounds/winner_5.mp3", "/static/sounds/winner_6.mp3",
  "/static/sounds/winner_7.mp3"
];

// Audio handles
let preludeSound = null;
let loopSound = null;
let winnerSound = null;
let pendingWinnerData = null; // for deferred winner trigger

function pickRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function stopAllAudio() {
  [preludeSound, loopSound, winnerSound].forEach(sound => {
    if (sound && sound.playing()) sound.stop();
  });
  pendingWinnerData = null;
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
  qmarks.forEach((q, i) => {
    q.classList.remove('visible'); // reset first
    setTimeout(() => q.classList.add('visible'), i * 200);
  });
}

function showGetReady() {
  awaitingText.textContent = 'Get Ready';
  awaitingText.classList.add('visible');
}

function showGo() {
  awaitingText.textContent = 'GO';
  awaitingText.classList.remove('visible');
  void awaitingText.offsetWidth; // force reflow
  awaitingText.classList.add('visible');
}

// Play winner audio + visuals
function showWinner(data) {
  clearVisuals();
  stopAllAudio();

  winnerText.textContent = `Winner: ${data.name}`;
  winnerText.classList.add('visible');

  winnerButton.textContent = `Button ${data.button}`;
  winnerButton.classList.add('visible');

  const winnerPath = pickRandom(winnerTracks);
  winnerSound = new Howl({ src: [winnerPath], volume: 1.0 });
  winnerSound.play();
}

// Preload dummy sound on first click
document.addEventListener('click', () => {
  new Howl({ src: [pickRandom(preludeTracks)] }).play().stop();
}, { once: true });

// Socket event handling
socket.on('projector_state', data => {
  if (data.state === 'clear') {
    stopAllAudio();
    clearVisuals();

  } else if (data.state === 'awaiting') {
    stopAllAudio();
    clearVisuals();
    showGetReady(); // show "Get Ready"

    const preludePath = pickRandom(preludeTracks);
    const loopPath = pickRandom(loopTracks);

    preludeSound = new Howl({ src: [preludePath], volume: 1.0 });
    loopSound = new Howl({ src: [loopPath], volume: 0.0, loop: true });

    preludeSound.play();

    preludeSound.once('end', () => {
      if (pendingWinnerData) {
        showWinner(pendingWinnerData);
      } else {
        showGo();
        loopSound.play();
        loopSound.fade(0.0, 1.0, 1000); // fade in loop
        animateQuestionMarks();
      }
    });

  } else if (data.state === 'winner') {
    // If prelude is still playing, defer winner logic
    if (preludeSound && preludeSound.playing()) {
      pendingWinnerData = data;
    } else {
      showWinner(data);
    }
  }
});
