# builder/loop_gen.py
# Generates comprehensive 60 FPS animation loop, camera flythrough controller, radar sync, and multi-input handlers

def generate_loop_js():
    return """    /* =========================================================================
       ANIMATION LOOP, FLIGHT CAMERA CONTROLLER & MULTI-INPUT LISTENERS
       ========================================================================= */
    const subBoxes = [
      document.getElementById('sub-1'),
      document.getElementById('sub-2'),
      document.getElementById('sub-3'),
      document.getElementById('sub-4'),
      document.getElementById('sub-5'),
      document.getElementById('sub-6'),
      document.getElementById('sub-7'),
      document.getElementById('sub-8'),
      document.getElementById('sub-9'),
      document.getElementById('sub-10'),
      document.getElementById('sub-11'),
      document.getElementById('sub-12')
    ];

    const timelineProgress = document.getElementById('timeline-progress');
    const scrollPrompt = document.getElementById('scroll-prompt');
    const glitchBurst = document.getElementById('glitch-burst');
    const scanlinesLayer = document.getElementById('scanlines-layer');
    const spaceHud = document.getElementById('space-hud');
    const fpsBadge = document.getElementById('telemetry-fps-text');
    const subtitlesViewport = document.getElementById('subtitles-viewport');

    // targetScroll & currentScroll are declared globally above — do NOT redeclare here.
    let activeSubIndex = 0;
    // Start at 0 (matching sub-1 which is visible by default on load)
    let prevSubIndex = 0;

    let mouseNormX = 0;
    let mouseNormY = 0;

    // Mouse Movement Tracking
    window.addEventListener('mousemove', (e) => {
      mouseNormX = (e.clientX / window.innerWidth - 0.5) * 2;
      mouseNormY = (e.clientY / window.innerHeight - 0.5) * 2;
      if (customParticleMat && customParticleMat.uniforms.uMouse) {
        customParticleMat.uniforms.uMouse.value.set(mouseNormX, -mouseNormY);
      }
    }, { passive: true });

    // Sync Window Scroll with Internal Progress
    function syncWindowScroll() {
      const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
      if (maxScroll > 0) {
        window.scrollTo({
          top: targetScroll * maxScroll,
          behavior: 'auto'
        });
      }
    }

    // Step Experience Controller (Smooth gradual jump per step)
    window.stepExperience = function(dir) {
      initAudioEngine();
      targetScroll = Math.max(0, Math.min(targetScroll + dir * 0.035, 1));
      syncWindowScroll();
      updateShepardScroll(dir * 25);
    };

    // Warp Directly to Cosmic Stage
    window.warpToCosmicStage = function(targetVal) {
      initAudioEngine();
      playWarpJumpSound();
      targetScroll = Math.max(0, Math.min(targetVal, 1));
      syncWindowScroll();
    };

    // Rewind Simulation to Genesis
    window.rewindCosmicSimulation = function() {
      initAudioEngine();
      targetScroll = 0;
      syncWindowScroll();
      playCinematicFX(550, 'sawtooth', 0.5, 0.2);
    };

    // ────────────────────────────────────────────────────────────
    // AUDIO UNLOCK — only on genuine user gestures (click / key / touchend)
    // Browsers only allow AudioContext after these events, NOT scroll/wheel.
    // ────────────────────────────────────────────────────────────
    function audioUnlockOnce() {
      initAudioEngine();
      document.removeEventListener('click',    audioUnlockOnce);
      document.removeEventListener('keydown',  audioUnlockOnce);
      document.removeEventListener('touchend', audioUnlockOnce);
    }
    document.addEventListener('click',    audioUnlockOnce, { once: true, passive: true });
    document.addEventListener('keydown',  audioUnlockOnce, { once: true, passive: true });
    document.addEventListener('touchend', audioUnlockOnce, { once: true, passive: true });

    // 1. Native Window Scroll Listener — NO audio init here
    window.addEventListener('scroll', () => {
      const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
      if (maxScroll > 0) {
        targetScroll = Math.max(0, Math.min(window.scrollY / maxScroll, 1));
      }
    }, { passive: true });

    // 2. Direct Wheel Scroll with Momentum — Balanced cinematic speed (not hyper-fast)
    window.addEventListener('wheel', (e) => {
      targetScroll += e.deltaY * 0.000075;
      targetScroll = Math.max(0, Math.min(targetScroll, 1));
      syncWindowScroll();
      updateShepardScroll(e.deltaY * 0.4);
    }, { passive: true });

    // 3. Mobile Touch Swipe Listeners — Smooth controllable drag
    let touchStartY = 0;
    window.addEventListener('touchstart', (e) => {
      touchStartY = e.touches[0].clientY;
    }, { passive: true });

    window.addEventListener('touchmove', (e) => {
      const deltaY = touchStartY - e.touches[0].clientY;
      touchStartY = e.touches[0].clientY;
      targetScroll += deltaY * 0.00035;
      targetScroll = Math.max(0, Math.min(targetScroll, 1));
      syncWindowScroll();
      updateShepardScroll(deltaY * 0.5);
    }, { passive: true });

    // 4. Keyboard Navigation — Gradual controlled steps
    window.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowDown' || e.key === 'PageDown' || e.key === ' ') {
        targetScroll = Math.min(targetScroll + 0.015, 1);
        syncWindowScroll();
        updateShepardScroll(15);
      } else if (e.key === 'ArrowUp' || e.key === 'PageUp') {
        targetScroll = Math.max(targetScroll - 0.015, 0);
        syncWindowScroll();
        updateShepardScroll(-15);
      } else if (e.key === 'Home') {
        targetScroll = 0;
        syncWindowScroll();
      } else if (e.key === 'End') {
        targetScroll = 1;
        syncWindowScroll();
      }
    });

    // 5. Window Resize Handler
    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
      if (composer) composer.setSize(window.innerWidth, window.innerHeight);
      if (bloomPass) bloomPass.setSize(window.innerWidth, window.innerHeight);
    });

    // FPS Meter Variables
    let lastFrameTime = performance.now();
    let frameCount = 0;
    let currentFps = 60;

    // Total Camera Fly-Through Z Distance (+48 down to -2940)
    const totalZTravel = 48 - (-2940);

    /* -------------------------------------------------------------------------
       UNIFIED MASTER 60 FPS ANIMATION LOOP
       ------------------------------------------------------------------------- */
    function animateEngineFrame() {
      const timeNow = performance.now() * 0.001;

      // FPS Calculation
      frameCount++;
      if (performance.now() - lastFrameTime >= 1000) {
        currentFps = frameCount;
        frameCount = 0;
        lastFrameTime = performance.now();
        if (fpsBadge) fpsBadge.textContent = currentFps;
      }

      // Smooth progress lerp (silky, controlled cinematic inertia)
      currentScroll += (targetScroll - currentScroll) * 0.045;
      if (timelineProgress) timelineProgress.style.width = (currentScroll * 100) + '%';

      if (currentScroll > 0.02) {
        if (scrollPrompt) scrollPrompt.style.opacity = '0';
      } else {
        if (scrollPrompt) scrollPrompt.style.opacity = '1';
      }

      // 1. Update 100K Particle Shaders
      const gpgpuProgress = currentScroll * 5.0;
      customParticleMat.uniforms.uProgress.value = gpgpuProgress;
      customParticleMat.uniforms.uTime.value = timeNow;

      // 2. Camera Fly-Through Z Calculation (Smooth cinematic glide)
      const targetCamZ = 48 - (currentScroll * totalZTravel);
      camera.position.z = THREE.MathUtils.lerp(camera.position.z, targetCamZ, 0.045);

      // Vertigo Dolly Zoom on CRT Glitch Transition
      if (currentScroll >= 0.05 && currentScroll <= 0.11) {
        const vertigoProgress = (currentScroll - 0.05) / 0.06;
        camera.fov = 60 + Math.sin(vertigoProgress * Math.PI) * 26;
        camera.updateProjectionMatrix();
      } else {
        camera.fov = 60;
        camera.updateProjectionMatrix();
      }

      // Gentle mouse parallax look-around
      camera.position.x = THREE.MathUtils.lerp(camera.position.x, mouseNormX * 5.0, 0.035);
      camera.position.y = THREE.MathUtils.lerp(camera.position.y, -mouseNormY * 4.5, 0.035);
      camera.lookAt(0, 0, camera.position.z - 35);

      // 3. Stage 1: CRT Gameplay Channels
      if (currentScroll < 0.02) crtChannel = 0;
      else if (currentScroll < 0.04) crtChannel = 1;
      else if (currentScroll < 0.065) crtChannel = 2;
      else crtChannel = 3;

      if (currentScroll < 0.11) {
        renderCRTGameplay(timeNow);
        crtTexture.needsUpdate = true;
        crtGroup.rotation.y = mouseNormX * 0.2;
        crtGroup.rotation.x = -mouseNormY * 0.15;
        if (scanlinesLayer) scanlinesLayer.style.opacity = '0.35';
      } else {
        if (scanlinesLayer) scanlinesLayer.style.opacity = '0.04';
      }

      // CRT Glitch & 3D Glass Shatter
      if (currentScroll >= 0.065 && currentScroll < 0.11) {
        crtGroup.position.x = (Math.random() - 0.5) * 2.5;
        crtGroup.position.y = (Math.random() - 0.5) * 2.5;
        shardsGroup.visible = true;
        shards.forEach(s => {
          s.mesh.position.x += s.vx;
          s.mesh.position.y += s.vy;
          s.mesh.position.z += s.vz;
        });
        if (Math.random() > 0.8) {
          if (glitchBurst) glitchBurst.style.opacity = '0.45';
          if (cinematicPass) {
            cinematicPass.uniforms.uGlitch.value = 0.55;
            cinematicPass.uniforms.uAberration.value = 0.018;
          }
          setTimeout(() => {
            if (glitchBurst) glitchBurst.style.opacity = '0';
            if (cinematicPass) {
              cinematicPass.uniforms.uGlitch.value = 0.0;
              cinematicPass.uniforms.uAberration.value = 0.001;
            }
          }, 60);
        }
      } else {
        crtGroup.position.set(0, 0, 0);
        shardsGroup.visible = false;
      }

      // 4. Stage 4: 3D Smartphone & Datacenter
      if (currentScroll >= 0.18 && currentScroll <= 0.32) {
        const phoneProgress = (currentScroll - 0.18) / 0.14;
        renderPhoneTelegram(phoneProgress);
        phoneTexture.needsUpdate = true;

        renderRailwayLogs(timeNow);
        logTexture.needsUpdate = true;

        phoneGroup.rotation.y = Math.sin(timeNow * 1.5) * 0.15 + (mouseNormX * 0.15);
        phoneGroup.rotation.x = -mouseNormY * 0.1;
      }

      // 5. STAGE 5: PROLONGED INTERSTELLAR ODYSSEY (10 CELESTIAL BODIES)
      if (currentScroll >= 0.28 && currentScroll <= 0.89) {
        if (spaceHud) spaceHud.classList.add('active');

        // Continuous planetary axial rotations
        planet1.rotation.y = timeNow * 0.25;
        planet2.rotation.y = timeNow * 0.3;
        moon1.rotation.y = timeNow * 1.2;
        planet3.rotation.y = timeNow * 0.2;
        planet4.rotation.y = timeNow * 0.28;
        planet5.rotation.y = timeNow * 0.35;
        sunPulsar.rotation.y = timeNow * 0.15;
        blackHoleCore.rotation.y = timeNow * 0.4;
        accretionDisk.rotation.z = timeNow * 0.6;

        // Tumbling Asteroids
        asteroids.forEach(a => {
          a.mesh.rotation.x += a.rotSpeedX;
          a.mesh.rotation.y += a.rotSpeedY;
        });

        // 2D Radar & Cockpit Telemetry Updates
        renderRadarDisplay(camera.position.z);
        updateCockpitTelemetry(camera.position.z, currentScroll);

        // Animate Waveform Bars in HUD
        const bars = document.querySelectorAll('.waveform-bar');
        bars.forEach((b, idx) => {
          const h = 20 + Math.sin(timeNow * 8 + idx) * 18 + Math.random() * 10;
          b.style.height = `${h}%`;
        });
      } else {
        if (spaceHud) spaceHud.classList.remove('active');
      }

      // 6. Subtitles Stage Mapping — WIDER thresholds for natural slow pacing
      // Total scroll = 0..1 mapped across 3500vh. Each stage gets ample room.
      if      (currentScroll < 0.07)  activeSubIndex = 0;   // Stage 01: Retro CRT 2009
      else if (currentScroll < 0.13)  activeSubIndex = 1;   // Stage 02: Glitch & Crash
      else if (currentScroll < 0.20)  activeSubIndex = 2;   // Stage 03: Code Void
      else if (currentScroll < 0.28)  activeSubIndex = 3;   // Stage 04: AI Neural Genesis
      else if (currentScroll < 0.36)  activeSubIndex = 4;   // Stage 05: Telegram Cloud
      else if (currentScroll < 0.44)  activeSubIndex = 5;   // Stage 06: Cosmic Launch
      else if (currentScroll < 0.53)  activeSubIndex = 6;   // Sector: AURA-9
      else if (currentScroll < 0.62)  activeSubIndex = 7;   // Sector: GLACIES
      else if (currentScroll < 0.71)  activeSubIndex = 8;   // Sector: NEXUS-01
      else if (currentScroll < 0.79)  activeSubIndex = 9;   // Sector: PYRO-X
      else if (currentScroll < 0.88)  activeSubIndex = 10;  // Sector: Sol-Prime
      else                            activeSubIndex = 11;  // Stage 07: Z-PACT Homeworld

      if (activeSubIndex !== prevSubIndex) {
        const oldIndex = prevSubIndex;
        prevSubIndex = activeSubIndex;

        // Cinematic card transition: exit old → enter new smoothly
        function switchSubCard(oldIdx, newIdx) {
          subBoxes.forEach((box, idx) => {
            if (!box) return;
            if (idx === newIdx) {
              box.removeAttribute('style');
              box.classList.remove('exit');
              box.classList.add('active');
            } else if (idx === oldIdx) {
              box.removeAttribute('style');
              box.classList.remove('active');
              box.classList.add('exit');
              setTimeout(() => {
                if (idx !== activeSubIndex) box.classList.remove('exit');
              }, 400);
            } else {
              box.removeAttribute('style');
              box.classList.remove('active', 'exit');
            }
          });
        }

        switchSubCard(oldIndex, activeSubIndex);

        switch (activeSubIndex) {
          case 0: playCinematicFX(440, 'triangle', 0.25, 0.12); break;
          case 1: playCinematicFX(180, 'sawtooth', 0.3, 0.18); break;
          case 2: playCinematicFX(280, 'sawtooth', 0.4, 0.16); break;
          case 3: playCinematicFX(660, 'sine', 0.35, 0.15); break;
          case 4: playTelegramChime(); break;
          case 5: playWarpJumpSound(); break;
          case 6: playRadarSonarPing(); break;
          case 7: playCinematicFX(520, 'sine', 0.5, 0.18); break;
          case 8: playCinematicFX(750, 'triangle', 0.4, 0.15); break;
          case 9: playCinematicFX(220, 'sawtooth', 0.5, 0.2); break;
          case 10: playWarpJumpSound(); break;
          case 11: playCinematicFX(1046, 'sine', 0.6, 0.25); break;
        }
      }

      if (subtitlesViewport) {
        if (currentScroll >= 0.89) {
          subtitlesViewport.style.opacity = '0';
          subtitlesViewport.style.pointerEvents = 'none';
        } else {
          subtitlesViewport.style.opacity = '1';
          subtitlesViewport.style.pointerEvents = 'auto';
        }
      }

      if (cinematicPass) cinematicPass.uniforms.uTime.value = timeNow;

      // 7. Post-Processing Render with WebGL Direct Fallback
      if (composer) {
        try {
          composer.render();
        } catch (e) {
          renderer.render(scene, camera);
        }
      } else {
        renderer.render(scene, camera);
      }

      requestAnimationFrame(animateEngineFrame);
    }

    // ── KICK START THE 60 FPS MASTER ANIMATION LOOP ──────────────────────────
    requestAnimationFrame(animateEngineFrame);

    /* =========================================================================
       FLUID SCROLL-REVEAL — IntersectionObserver for final climax section
       Watches .reveal and .reveal-stagger elements, adds .visible when
       they enter the viewport. Purely CSS-transition driven — no jank.
       ========================================================================= */
    (function initScrollReveal() {
      const revealEls = document.querySelectorAll('.reveal, .reveal-stagger');
      if (!revealEls.length) return;

      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add('visible');
              // Stop watching once revealed — no "un-reveal" on scroll back
              observer.unobserve(entry.target);
            }
          });
        },
        {
          root: null,          // viewport
          rootMargin: '0px 0px -8% 0px',  // trigger when 8% above bottom edge
          threshold: 0.06      // just a sliver needs to be visible
        }
      );

      revealEls.forEach((el) => observer.observe(el));
    })();
"""

if __name__ == "__main__":
    loop = generate_loop_js()
    print(f"Generated Loop JS: {len(loop.splitlines())} lines")
