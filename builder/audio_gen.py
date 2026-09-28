# builder/audio_gen.py
# Generates comprehensive procedural Web Audio API engine for the 10,000-line Scrollytelling Experience

def generate_audio_js():
    return """    /* =========================================================================
       AUDIO SYNTHESIS ENGINE (PROCEDURAL ZERO-ASSET WEB AUDIO API)
       ========================================================================= */
    let audioCtx = null;
    let masterGain = null;
    let subBassOsc = null;
    let subBassGain = null;
    let shepardOscs = [];
    let shepardGains = [];
    let isAudioMuted = false;
    let isAudioInitialized = false;

    // Initialize Web Audio Context ONLY after a real user gesture
    // (click, keydown, touchend) — browsers block autoplay otherwise.
    function initAudioEngine() {
      if (isAudioInitialized) return;
      isAudioInitialized = true; // set immediately to prevent double-init
      try {
        const AudioCtor = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtor) return;

        audioCtx = new AudioCtor();
        masterGain = audioCtx.createGain();
        masterGain.gain.setValueAtTime(0.55, audioCtx.currentTime);
        masterGain.connect(audioCtx.destination);

        // resume() must resolve before any nodes can produce sound
        const resumePromise = audioCtx.state === 'suspended'
          ? audioCtx.resume()
          : Promise.resolve();

        resumePromise.then(() => {
          startSubBassDrone();
          setupShepardTones();
          initSolarWindBuffer();
          console.log('[CosmicAudio] Audio engine running. State:', audioCtx.state);
        }).catch((err) => {
          console.warn('[CosmicAudio] resume() failed:', err);
        });

      } catch (err) {
        isAudioInitialized = false; // allow retry
        console.warn('[CosmicAudio] Audio init failed:', err);
      }
    }

    // Toggle Master Audio Mute/Unmute
    window.toggleCosmicAudio = function() {
      initAudioEngine();
      if (!audioCtx || !masterGain) return;

      isAudioMuted = !isAudioMuted;
      const btnIcon = document.getElementById('audio-btn-icon');
      const btnLabel = document.getElementById('audio-btn-label');
      const toggleBtn = document.getElementById('audio-toggle-btn');

      if (isAudioMuted) {
        masterGain.gain.setTargetAtTime(0.0, audioCtx.currentTime, 0.05);
        if (btnIcon) btnIcon.textContent = '🔇';
        if (btnLabel) btnLabel.textContent = 'AUDIO: MUTED';
        if (toggleBtn) toggleBtn.classList.remove('active');
      } else {
        masterGain.gain.setTargetAtTime(0.65, audioCtx.currentTime, 0.05);
        if (btnIcon) btnIcon.textContent = '🔊';
        if (btnLabel) btnLabel.textContent = 'AUDIO: ACTIVE';
        if (toggleBtn) toggleBtn.classList.add('active');
        playRadarSonarPing();
      }
    };

    // Sub-Bass Continuous Drone (55Hz Cinematic Deep Rumble)
    function startSubBassDrone() {
      if (!audioCtx || !masterGain) return;
      try {
        subBassOsc = audioCtx.createOscillator();
        subBassGain = audioCtx.createGain();

        subBassOsc.type = 'sine';
        subBassOsc.frequency.setValueAtTime(55, audioCtx.currentTime);

        const lowpass = audioCtx.createBiquadFilter();
        lowpass.type = 'lowpass';
        lowpass.frequency.setValueAtTime(140, audioCtx.currentTime);
        lowpass.Q.setValueAtTime(2.5, audioCtx.currentTime);

        subBassGain.gain.setValueAtTime(0.18, audioCtx.currentTime);

        subBassOsc.connect(lowpass);
        lowpass.connect(subBassGain);
        subBassGain.connect(masterGain);

        subBassOsc.start();
      } catch (e) {
        console.warn('Sub-bass drone init error:', e);
      }
    }

    // Shepard Tone Continuous Pitch Illusion on Scroll
    function setupShepardTones() {
      if (!audioCtx || !masterGain) return;
      try {
        const baseFreqs = [55, 110, 220, 440, 880];
        shepardOscs = [];
        shepardGains = [];

        baseFreqs.forEach((freq) => {
          const osc = audioCtx.createOscillator();
          const gain = audioCtx.createGain();

          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, audioCtx.currentTime);

          gain.gain.setValueAtTime(0.02, audioCtx.currentTime);

          osc.connect(gain);
          gain.connect(masterGain);
          osc.start();

          shepardOscs.push({ osc, baseFreq: freq, currentFreq: freq });
          shepardGains.push(gain);
        });
      } catch (e) {
        console.warn('Shepard tones init error:', e);
      }
    }

    // Update Shepard Tone Pitch with Scroll Velocity
    function updateShepardScroll(delta) {
      if (!audioCtx || shepardOscs.length === 0 || isAudioMuted) return;
      try {
        const now = audioCtx.currentTime;
        const shiftFactor = Math.abs(delta) * 0.05;

        shepardOscs.forEach((item, idx) => {
          let newFreq = item.currentFreq + delta * 0.12;
          if (newFreq < 40) newFreq = 440;
          if (newFreq > 880) newFreq = 55;
          item.currentFreq = newFreq;

          item.osc.frequency.setTargetAtTime(newFreq, now, 0.08);

          // Bell-shaped volume envelope to mask boundary jumps
          const logNorm = (Math.log2(newFreq / 55)) / 4.0;
          const env = Math.sin(Math.max(0, Math.min(logNorm, 1)) * Math.PI);
          shepardGains[idx].gain.setTargetAtTime(env * 0.045, now, 0.08);
        });
      } catch (e) {
        // Silently catch audio buffer hiccups
      }
    }

    // Procedural Solar Wind & White Noise Ambient Generator
    let solarWindSource = null;
    let solarWindFilter = null;
    let solarWindGain = null;

    function initSolarWindBuffer() {
      if (!audioCtx || !masterGain) return;
      try {
        const bufferSize = audioCtx.sampleRate * 2;
        const noiseBuffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
        const output = noiseBuffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
          output[i] = Math.random() * 2 - 1;
        }

        solarWindSource = audioCtx.createBufferSource();
        solarWindSource.buffer = noiseBuffer;
        solarWindSource.loop = true;

        solarWindFilter = audioCtx.createBiquadFilter();
        solarWindFilter.type = 'bandpass';
        solarWindFilter.frequency.setValueAtTime(320, audioCtx.currentTime);
        solarWindFilter.Q.setValueAtTime(3.0, audioCtx.currentTime);

        solarWindGain = audioCtx.createGain();
        solarWindGain.gain.setValueAtTime(0.04, audioCtx.currentTime);

        solarWindSource.connect(solarWindFilter);
        solarWindFilter.connect(solarWindGain);
        solarWindGain.connect(masterGain);

        solarWindSource.start();
      } catch (e) {
        console.warn('Solar wind noise init error:', e);
      }
    }

    // Procedural Sound Effect Synthesizer
    function playCinematicFX(freq, type = 'sine', duration = 0.3, vol = 0.25) {
      if (!audioCtx || !masterGain || isAudioMuted) return;
      try {
        const now = audioCtx.currentTime;
        const osc = audioCtx.createOscillator();
        const g = audioCtx.createGain();

        osc.type = type;
        osc.frequency.setValueAtTime(freq, now);
        osc.frequency.exponentialRampToValueAtTime(freq * 0.5, now + duration);

        g.gain.setValueAtTime(vol, now);
        g.gain.exponentialRampToValueAtTime(0.001, now + duration);

        osc.connect(g);
        g.connect(masterGain);

        osc.start(now);
        osc.stop(now + duration);
      } catch (e) {}
    }

    // Telegram Multi-Tone Harmonic Delivery Chime
    function playTelegramChime() {
      if (!audioCtx || !masterGain || isAudioMuted) return;
      try {
        const now = audioCtx.currentTime;
        const notes = [659.25, 830.61, 1046.50]; // E5, G#5, C6
        notes.forEach((freq, idx) => {
          const osc = audioCtx.createOscillator();
          const g = audioCtx.createGain();
          const noteStart = now + (idx * 0.07);

          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, noteStart);

          g.gain.setValueAtTime(0, noteStart);
          g.gain.linearRampToValueAtTime(0.2, noteStart + 0.02);
          g.gain.exponentialRampToValueAtTime(0.001, noteStart + 0.35);

          osc.connect(g);
          g.connect(masterGain);

          osc.start(noteStart);
          osc.stop(noteStart + 0.4);
        });
      } catch (e) {}
    }

    // Radar Sonar Ping (Sci-Fi Navigation Beacon)
    function playRadarSonarPing() {
      if (!audioCtx || !masterGain || isAudioMuted) return;
      try {
        const now = audioCtx.currentTime;
        const osc = audioCtx.createOscillator();
        const g = audioCtx.createGain();

        osc.type = 'sine';
        osc.frequency.setValueAtTime(1450, now);
        osc.frequency.exponentialRampToValueAtTime(1100, now + 0.45);

        g.gain.setValueAtTime(0.25, now);
        g.gain.exponentialRampToValueAtTime(0.001, now + 0.5);

        osc.connect(g);
        g.connect(masterGain);

        osc.start(now);
        osc.stop(now + 0.52);
      } catch (e) {}
    }

    // Warp Jump Sonic Boom
    function playWarpJumpSound() {
      if (!audioCtx || !masterGain || isAudioMuted) return;
      try {
        const now = audioCtx.currentTime;
        const osc = audioCtx.createOscillator();
        const g = audioCtx.createGain();

        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(120, now);
        osc.frequency.exponentialRampToValueAtTime(880, now + 0.3);
        osc.frequency.exponentialRampToValueAtTime(40, now + 0.8);

        g.gain.setValueAtTime(0.35, now);
        g.gain.exponentialRampToValueAtTime(0.001, now + 0.85);

        osc.connect(g);
        g.connect(masterGain);

        osc.start(now);
        osc.stop(now + 0.9);
      } catch (e) {}
    }

    // Retro 8-bit Sound FX
    function playRetroJump() {
      playCinematicFX(320, 'square', 0.15, 0.2);
    }

    function playRetroLaser() {
      playCinematicFX(880, 'sawtooth', 0.12, 0.18);
    }

    function playRetroExplosion() {
      playCinematicFX(90, 'triangle', 0.4, 0.35);
    }

    function playRetroCoin() {
      if (!audioCtx || !masterGain || isAudioMuted) return;
      try {
        const now = audioCtx.currentTime;
        const osc = audioCtx.createOscillator();
        const g = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(987.77, now);
        osc.frequency.setValueAtTime(1318.51, now + 0.08);

        g.gain.setValueAtTime(0.2, now);
        g.gain.exponentialRampToValueAtTime(0.001, now + 0.35);

        osc.connect(g);
        g.connect(masterGain);

        osc.start(now);
        osc.stop(now + 0.38);
      } catch (e) {}
    }

    // Terminal Mechanical Keystroke Click
    function playTerminalKeystroke() {
      if (!audioCtx || !masterGain || isAudioMuted) return;
      try {
        const now = audioCtx.currentTime;
        const osc = audioCtx.createOscillator();
        const g = audioCtx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(1200 + Math.random() * 300, now);

        g.gain.setValueAtTime(0.04, now);
        g.gain.exponentialRampToValueAtTime(0.0001, now + 0.035);

        osc.connect(g);
        g.connect(masterGain);

        osc.start(now);
        osc.stop(now + 0.04);
      } catch (e) {}
    }
"""

if __name__ == "__main__":
    audio = generate_audio_js()
    print(f"Generated Audio JS: {len(audio.splitlines())} lines")
