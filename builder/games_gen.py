# builder/games_gen.py
# Generates comprehensive 2D canvas simulation engines for retro gaming, Telegram, and cloud datacenters

def generate_games_js():
    return """    /* =========================================================================
       2D CANVAS SIMULATION ENGINES (RETRO GAMING, TELEGRAM, & DATACENTER)
       ========================================================================= */

    // Helper for cross-browser safe rounded rectangles
    function safeRoundRect(ctx, x, y, w, h, r) {
      if (typeof ctx.roundRect === 'function') {
        ctx.roundRect(x, y, w, h, r);
      } else {
        ctx.beginPath();
        ctx.moveTo(x + r, y);
        ctx.lineTo(x + w - r, y);
        ctx.quadraticCurveTo(x + w, y, x + w, y + r);
        ctx.lineTo(x + w, y + h - r);
        ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
        ctx.lineTo(x + r, y + h);
        ctx.quadraticCurveTo(x, y + h, x, y + h - r);
        ctx.lineTo(x, y + r);
        ctx.quadraticCurveTo(x, y, x + r, y);
        ctx.closePath();
      }
    }

    /* -------------------------------------------------------------------------
       ENGINE 1: RETRO CRT GAMEPLAY CANVAS (PVZ, TMNT, WOLFTEAM, KERNEL PANIC)
       ------------------------------------------------------------------------- */
    const crtCanvas = document.getElementById('crt-game-canvas');
    const crtCtx = crtCanvas.getContext('2d');
    let crtChannel = 0; // 0 = PvZ, 1 = TMNT, 2 = WolfTeam, 3 = Glitch Crash

    // Simulation Timers & Entities
    let pvzTimer = 0;
    let tmntTimer = 0;
    let wolfTimer = 0;

    // PvZ Projectiles & Suns
    const pvzPeas = [
      { x: 160, y: 168, vx: 5.5 },
      { x: 260, y: 168, vx: 5.5 },
      { x: 200, y: 248, vx: 5.5 }
    ];

    const pvzSuns = [
      { x: 220, y: 80, vy: 0.8, alpha: 1 },
      { x: 380, y: 120, vy: 0.7, alpha: 1 }
    ];

    // Master Render Loop for CRT Screen
    function renderCRTGameplay(time) {
      crtCtx.fillStyle = '#060a12';
      crtCtx.fillRect(0, 0, crtCanvas.width, crtCanvas.height);

      if (crtChannel === 0) {
        renderPvZGame(time);
      } else if (crtChannel === 1) {
        renderTMNTGame(time);
      } else if (crtChannel === 2) {
        renderWolfTeamGame(time);
      } else {
        renderKernelPanicGlitch(time);
      }

      // Authentic CRT Phosphor Scanline Overlay & Curved Tube Vignette
      crtCtx.fillStyle = 'rgba(0, 0, 0, 0.22)';
      for (let y = 0; y < crtCanvas.height; y += 4) {
        crtCtx.fillRect(0, y, crtCanvas.width, 2);
      }

      // Subtle CRT Glass Curvature Vignette
      const tubeGrad = crtCtx.createRadialGradient(
        crtCanvas.width / 2, crtCanvas.height / 2, 180,
        crtCanvas.width / 2, crtCanvas.height / 2, 340
      );
      tubeGrad.addColorStop(0, 'rgba(0,0,0,0)');
      tubeGrad.addColorStop(1, 'rgba(0,0,0,0.65)');
      crtCtx.fillStyle = tubeGrad;
      crtCtx.fillRect(0, 0, crtCanvas.width, crtCanvas.height);
    }

    // 1.A: PLANTS VS. ZOMBIES DETAILED 2D SIMULATION
    function renderPvZGame(time) {
      pvzTimer += 0.035;

      // 5-Row Checkerboard Lawn
      const rows = 5;
      const cols = 9;
      const cellW = 58;
      const cellH = 64;
      const startX = 75;
      const startY = 85;

      for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
          crtCtx.fillStyle = ((r + c) % 2 === 0) ? '#4ade80' : '#22c55e';
          crtCtx.fillRect(startX + c * cellW, startY + r * cellH, cellW, cellH);
        }
      }

      // House boundary & Lawnmowers
      crtCtx.fillStyle = '#78350f';
      crtCtx.fillRect(0, startY, startX - 10, rows * cellH);

      for (let r = 0; r < rows; r++) {
        // Lawnmower Red Body
        crtCtx.fillStyle = '#ef4444';
        crtCtx.fillRect(startX - 28, startY + r * cellH + 16, 22, 28);
        crtCtx.fillStyle = '#0f172a';
        crtCtx.fillRect(startX - 30, startY + r * cellH + 36, 8, 8);
        crtCtx.fillRect(startX - 14, startY + r * cellH + 36, 8, 8);
      }

      // Sunflower at Row 1, Col 1
      const sunBob = Math.sin(pvzTimer * 3) * 3;
      crtCtx.fillStyle = '#854d0e'; // stem
      crtCtx.fillRect(startX + 26, startY + cellH + 28, 6, 28);
      // Petals
      crtCtx.fillStyle = '#facc15';
      crtCtx.beginPath();
      crtCtx.arc(startX + 29, startY + cellH + 24 + sunBob, 18, 0, Math.PI * 2);
      crtCtx.fill();
      // Center face
      crtCtx.fillStyle = '#713f12';
      crtCtx.beginPath();
      crtCtx.arc(startX + 29, startY + cellH + 24 + sunBob, 10, 0, Math.PI * 2);
      crtCtx.fill();

      // Peashooter at Row 0, Col 1
      const peaBob = Math.sin(pvzTimer * 4) * 3;
      crtCtx.fillStyle = '#15803d'; // stem
      crtCtx.fillRect(startX + 26, startY + 28, 6, 28);
      // Head
      crtCtx.fillStyle = '#22c55e';
      crtCtx.beginPath();
      crtCtx.arc(startX + 29, startY + 24 + peaBob, 14, 0, Math.PI * 2);
      crtCtx.fill();
      // Snout
      crtCtx.fillRect(startX + 36, startY + 18 + peaBob, 14, 12);
      // Big cartoon eye
      crtCtx.fillStyle = '#ffffff';
      crtCtx.beginPath();
      crtCtx.arc(startX + 26, startY + 20 + peaBob, 4, 0, Math.PI * 2);
      crtCtx.fill();
      crtCtx.fillStyle = '#000000';
      crtCtx.beginPath();
      crtCtx.arc(startX + 27, startY + 20 + peaBob, 2, 0, Math.PI * 2);
      crtCtx.fill();

      // Peashooter Row 2, Col 2
      crtCtx.fillStyle = '#15803d';
      crtCtx.fillRect(startX + cellW + 26, startY + cellH * 2 + 28, 6, 28);
      crtCtx.fillStyle = '#22c55e';
      crtCtx.beginPath();
      crtCtx.arc(startX + cellW + 29, startY + cellH * 2 + 24 + peaBob, 14, 0, Math.PI * 2);
      crtCtx.fill();
      crtCtx.fillRect(startX + cellW + 36, startY + cellH * 2 + 18 + peaBob, 14, 12);

      // Render & Advance Glowing Peas
      pvzPeas.forEach((pea) => {
        pea.x += pea.vx;
        if (pea.x > 580) pea.x = startX + 50;

        crtCtx.fillStyle = '#86efac';
        crtCtx.beginPath();
        crtCtx.arc(pea.x, pea.y, 6.5, 0, Math.PI * 2);
        crtCtx.fill();
        crtCtx.fillStyle = '#16a34a';
        crtCtx.beginPath();
        crtCtx.arc(pea.x - 2, pea.y - 2, 3, 0, Math.PI * 2);
        crtCtx.fill();
      });

      // Animated Falling Glowing Sun Tokens
      pvzSuns.forEach((sun) => {
        sun.y += sun.vy;
        if (sun.y > 360) sun.y = 70;

        const pulse = 14 + Math.sin(pvzTimer * 5) * 3;
        crtCtx.fillStyle = 'rgba(250, 204, 21, 0.4)';
        crtCtx.beginPath();
        crtCtx.arc(sun.x, sun.y, pulse + 6, 0, Math.PI * 2);
        crtCtx.fill();

        crtCtx.fillStyle = '#facc15';
        crtCtx.beginPath();
        crtCtx.arc(sun.x, sun.y, pulse, 0, Math.PI * 2);
        crtCtx.fill();
      });

      // Animated Walking Zombies
      const zWalkX = 520 - (pvzTimer * 24) % 360;
      // Regular Zombie Row 0
      renderZombieFigure(zWalkX, startY + 12, pvzTimer, 'regular');
      // Conehead Zombie Row 2
      renderZombieFigure(zWalkX + 90, startY + cellH * 2 + 12, pvzTimer + 1, 'conehead');

      // Top Game UI Bar
      crtCtx.fillStyle = 'rgba(15, 23, 42, 0.85)';
      crtCtx.fillRect(20, 14, 320, 48);
      crtCtx.strokeStyle = '#38bdf8';
      crtCtx.lineWidth = 1.5;
      crtCtx.strokeRect(20, 14, 320, 48);

      crtCtx.fillStyle = '#facc15';
      crtCtx.font = 'bold 15px monospace';
      crtCtx.fillText('☀️ SUN: 275', 35, 43);

      crtCtx.fillStyle = '#ef4444';
      crtCtx.fillText('WAVE 1 // BRAINZ!', 160, 43);
    }

    function renderZombieFigure(x, y, t, type) {
      const legSwing = Math.sin(t * 3.5) * 7;
      const headBob = Math.sin(t * 3.5) * 2;

      // Legs
      crtCtx.fillStyle = '#1e3a8a'; // blue trousers
      crtCtx.fillRect(x + 4 + legSwing, y + 36, 5, 18);
      crtCtx.fillRect(x + 12 - legSwing, y + 36, 5, 18);

      // Body (brown coat)
      crtCtx.fillStyle = '#78350f';
      crtCtx.fillRect(x + 2, y + 16, 18, 22);

      // Arm reaching out
      crtCtx.fillStyle = '#4ade80'; // green arm
      crtCtx.fillRect(x - 8, y + 18, 12, 4);

      // Head
      crtCtx.fillStyle = '#4ade80';
      crtCtx.beginPath();
      crtCtx.arc(x + 10, y + 8 + headBob, 8, 0, Math.PI * 2);
      crtCtx.fill();

      // Eye
      crtCtx.fillStyle = '#ffffff';
      crtCtx.beginPath();
      crtCtx.arc(x + 7, y + 6 + headBob, 2.5, 0, Math.PI * 2);
      crtCtx.fill();

      // Conehead Hat
      if (type === 'conehead') {
        crtCtx.fillStyle = '#f97316'; // orange traffic cone
        crtCtx.beginPath();
        crtCtx.moveTo(x + 10, y - 8 + headBob);
        crtCtx.lineTo(x + 3, y + 3 + headBob);
        crtCtx.lineTo(x + 17, y + 3 + headBob);
        crtCtx.closePath();
        crtCtx.fill();
      }
    }

    // 1.B: TMNT ARCADE BEAT 'EM UP SIMULATION
    function renderTMNTGame(time) {
      tmntTimer += 0.045;

      // Parallax City Skyline & Sewer Floor
      crtCtx.fillStyle = '#0f172a';
      crtCtx.fillRect(0, 0, crtCanvas.width, 240);

      // Moon
      crtCtx.fillStyle = '#fef08a';
      crtCtx.beginPath();
      crtCtx.arc(540, 70, 34, 0, Math.PI * 2);
      crtCtx.fill();

      // Brick Wall & Sewer Platform
      crtCtx.fillStyle = '#1e293b';
      crtCtx.fillRect(0, 240, crtCanvas.width, 240);
      crtCtx.fillStyle = '#334155';
      for (let x = 0; x < crtCanvas.width; x += 40) {
        crtCtx.fillRect(x, 240, 2, 240);
      }

      // Leonardo Sprite (Green Body, Blue Bandana, Katanas)
      const jumpY = Math.abs(Math.sin(tmntTimer * 3)) * 40;
      const leoX = 180 + Math.sin(tmntTimer * 1.5) * 30;
      const leoY = 320 - jumpY;

      // Shell (Brown Back)
      crtCtx.fillStyle = '#92400e';
      crtCtx.beginPath();
      crtCtx.ellipse(leoX - 6, leoY + 8, 14, 20, 0, 0, Math.PI * 2);
      crtCtx.fill();

      // Body (Green)
      crtCtx.fillStyle = '#22c55e';
      crtCtx.beginPath();
      crtCtx.ellipse(leoX + 6, leoY + 8, 12, 18, 0, 0, Math.PI * 2);
      crtCtx.fill();

      // Head
      crtCtx.beginPath();
      crtCtx.arc(leoX + 8, leoY - 14, 10, 0, Math.PI * 2);
      crtCtx.fill();

      // Blue Bandana & Tail
      crtCtx.fillStyle = '#3b82f6';
      crtCtx.fillRect(leoX + 2, leoY - 17, 14, 5);
      crtCtx.beginPath();
      crtCtx.moveTo(leoX + 2, leoY - 15);
      crtCtx.lineTo(leoX - 12, leoY - 10 + Math.sin(tmntTimer * 8) * 4);
      crtCtx.stroke();

      // Katana Sword Slash Arc
      const slash = Math.sin(tmntTimer * 5) > 0.1;
      if (slash) {
        crtCtx.strokeStyle = '#38bdf8';
        crtCtx.lineWidth = 4;
        crtCtx.beginPath();
        crtCtx.arc(leoX + 24, leoY, 38, -0.6, 1.2);
        crtCtx.stroke();

        // Hit Text Popup
        crtCtx.fillStyle = '#fbbf24';
        crtCtx.font = 'bold 22px "Space Grotesk", sans-serif';
        crtCtx.fillText('KAPOW!', leoX + 65, leoY - 24);
      }

      // Foot Clan Ninja (Purple Shinobi)
      const ninjaX = 380 + Math.sin(tmntTimer * 2) * 20;
      crtCtx.fillStyle = '#7e22ce';
      crtCtx.fillRect(ninjaX, 310, 16, 32);
      crtCtx.fillStyle = '#0f172a';
      crtCtx.fillRect(ninjaX + 2, 296, 12, 14); // mask
      crtCtx.fillStyle = '#ef4444';
      crtCtx.fillRect(ninjaX + 4, 302, 8, 3); // red headband

      // Top Arcade HUD
      crtCtx.fillStyle = 'rgba(0, 0, 0, 0.7)';
      crtCtx.fillRect(10, 10, crtCanvas.width - 20, 42);
      crtCtx.fillStyle = '#38bdf8';
      crtCtx.font = 'bold 16px monospace';
      crtCtx.fillText('LEONARDO: [============] 100%', 25, 36);
      crtCtx.fillStyle = '#c084fc';
      crtCtx.fillText('FOOT CLAN: [======    ] 48%', 360, 36);
    }

    // 1.C: WOLFTEAM FPS & WEREWOLF TRANSFORMATION SIMULATION
    function renderWolfTeamGame(time) {
      wolfTimer += 0.04;

      // 3D Corridor Perspective
      crtCtx.fillStyle = '#0f172a';
      crtCtx.fillRect(0, 0, crtCanvas.width, crtCanvas.height);

      // Blood Moon Background
      crtCtx.fillStyle = '#991b1b';
      crtCtx.beginPath();
      crtCtx.arc(320, 140, 75, 0, Math.PI * 2);
      crtCtx.fill();

      // FPS Assault Rifle (Bottom Right)
      const recoil = Math.sin(wolfTimer * 12) * 5;
      crtCtx.fillStyle = '#334155';
      crtCtx.fillRect(420, 340 + recoil, 160, 70);
      crtCtx.fillStyle = '#1e293b';
      crtCtx.fillRect(400, 360 + recoil, 80, 24);

      // Muzzle Flash
      if (Math.sin(wolfTimer * 12) > 0.4) {
        crtCtx.fillStyle = '#fbbf24';
        crtCtx.beginPath();
        crtCtx.arc(395, 372 + recoil, 24, 0, Math.PI * 2);
        crtCtx.fill();
        crtCtx.fillStyle = '#ef4444';
        crtCtx.beginPath();
        crtCtx.arc(395, 372 + recoil, 12, 0, Math.PI * 2);
        crtCtx.fill();
      }

      // Wolf Claws Transformation Overlay
      const wolfCycle = Math.sin(wolfTimer * 1.5);
      if (wolfCycle > 0.2) {
        // Red Blood Vignette
        const bloodGrad = crtCtx.createRadialGradient(320, 240, 120, 320, 240, 320);
        bloodGrad.addColorStop(0, 'rgba(239, 68, 68, 0)');
        bloodGrad.addColorStop(1, 'rgba(239, 68, 68, 0.45)');
        crtCtx.fillStyle = bloodGrad;
        crtCtx.fillRect(0, 0, crtCanvas.width, crtCanvas.height);

        // Werewolf Claws
        crtCtx.strokeStyle = '#f8fafc';
        crtCtx.lineWidth = 6;
        for (let i = 0; i < 3; i++) {
          crtCtx.beginPath();
          crtCtx.moveTo(120 + i * 22, 280);
          crtCtx.lineTo(95 + i * 22, 360);
          crtCtx.stroke();
        }

        crtCtx.fillStyle = '#ef4444';
        crtCtx.font = 'bold 24px monospace';
        crtCtx.fillText('TRANSFORMATION // BERSERK WOLF', 140, 220);
      }

      // Tactical Crosshair HUD
      crtCtx.strokeStyle = '#10b981';
      crtCtx.lineWidth = 1.5;
      crtCtx.beginPath();
      crtCtx.arc(320, 240, 22, 0, Math.PI * 2);
      crtCtx.moveTo(320, 210); crtCtx.lineTo(320, 225);
      crtCtx.moveTo(320, 255); crtCtx.lineTo(320, 270);
      crtCtx.moveTo(290, 240); crtCtx.lineTo(305, 240);
      crtCtx.moveTo(335, 240); crtCtx.lineTo(350, 240);
      crtCtx.stroke();

      // Bottom Ammo HUD
      crtCtx.fillStyle = 'rgba(0, 0, 0, 0.75)';
      crtCtx.fillRect(20, crtCanvas.height - 55, 240, 40);
      crtCtx.fillStyle = '#10b981';
      crtCtx.font = 'bold 18px monospace';
      crtCtx.fillText('AMMO: 30 / 120', 35, crtCanvas.height - 30);
    }

    // 1.D: KERNEL PANIC GLITCH & CRT SHATTER SCREEN
    function renderKernelPanicGlitch(time) {
      crtCtx.fillStyle = '#040d21';
      crtCtx.fillRect(0, 0, crtCanvas.width, crtCanvas.height);

      crtCtx.fillStyle = '#38bdf8';
      crtCtx.font = 'bold 22px monospace';
      crtCtx.fillText('*** KERNEL PANIC // SYSTEM HALTED ***', 60, 90);

      crtCtx.font = '13px monospace';
      crtCtx.fillStyle = '#94a3b8';
      crtCtx.fillText('A fatal exception 0x0000007E has occurred at CS:0028.', 60, 130);
      crtCtx.fillText('Physical memory dump: 0xFFFFF80002E8A000 -> 0x0000.', 60, 155);
      crtCtx.fillText('SHATTERING REALITY MATRIX...', 60, 180);

      // Flickering Noise Bars
      crtCtx.fillStyle = 'rgba(56, 189, 248, 0.35)';
      for (let i = 0; i < 6; i++) {
        const ry = (Math.sin(time * 30 + i * 2) * 0.5 + 0.5) * crtCanvas.height;
        crtCtx.fillRect(0, ry, crtCanvas.width, 14);
      }
    }

    /* -------------------------------------------------------------------------
       ENGINE 2: TELEGRAM SMARTPHONE OFFSCREEN CANVAS SIMULATION
       ------------------------------------------------------------------------- */
    const phoneCanvas = document.getElementById('phone-sim-canvas');
    const phoneCtx = phoneCanvas.getContext('2d');

    function renderPhoneTelegram(progress) {
      phoneCtx.fillStyle = '#0f172a';
      phoneCtx.fillRect(0, 0, phoneCanvas.width, phoneCanvas.height);

      // Top Status Bar
      phoneCtx.fillStyle = '#1e293b';
      phoneCtx.fillRect(0, 0, phoneCanvas.width, 90);

      // Back Arrow
      phoneCtx.fillStyle = '#38bdf8';
      phoneCtx.font = 'bold 24px sans-serif';
      phoneCtx.fillText('←', 24, 55);

      // Bot Avatar
      phoneCtx.fillStyle = '#0284c7';
      phoneCtx.beginPath();
      phoneCtx.arc(85, 48, 26, 0, Math.PI * 2);
      phoneCtx.fill();
      phoneCtx.fillStyle = '#ffffff';
      phoneCtx.font = 'bold 20px sans-serif';
      phoneCtx.fillText('AS', 72, 55);

      // Title & Online Status
      phoneCtx.fillStyle = '#f8fafc';
      phoneCtx.font = 'bold 20px "Space Grotesk", sans-serif';
      phoneCtx.fillText('@n0accent (Abdo Saber) ✔', 125, 42);

      phoneCtx.fillStyle = '#38bdf8';
      phoneCtx.font = '14px sans-serif';
      phoneCtx.fillText('bot • 100K active cluster nodes', 125, 68);

      // Date Header
      phoneCtx.fillStyle = '#334155';
      safeRoundRect(phoneCtx, 190, 120, 130, 32, 16);
      phoneCtx.fill();
      phoneCtx.fillStyle = '#94a3b8';
      phoneCtx.font = 'bold 12px monospace';
      phoneCtx.fillText('TODAY 03:14 PM', 205, 141);

      // Message 1: User Request
      phoneCtx.fillStyle = '#0284c7';
      safeRoundRect(phoneCtx, 120, 180, 360, 75, 18);
      phoneCtx.fill();
      phoneCtx.fillStyle = '#ffffff';
      phoneCtx.font = '16px monospace';
      phoneCtx.fillText('/deploy --cluster railway', 140, 215);
      phoneCtx.fillText('--scale 100k --auto-heal', 140, 238);

      // Message 2: Bot Executing
      if (progress > 0.25) {
        phoneCtx.fillStyle = '#1e293b';
        safeRoundRect(phoneCtx, 30, 280, 450, 185, 20);
        phoneCtx.fill();

        phoneCtx.fillStyle = '#38bdf8';
        phoneCtx.font = 'bold 16px monospace';
        phoneCtx.fillText('🚀 Railway Orchestrator Active', 55, 318);

        phoneCtx.fillStyle = '#10b981';
        phoneCtx.font = '15px monospace';
        phoneCtx.fillText('✔ 100,000 Events Handled in 3.4ms', 55, 352);
        phoneCtx.fillText('✔ Microservices: 32 Worker Nodes Healthy', 55, 382);
        phoneCtx.fillText('✔ Zero Dropped Packets // SSL Synced', 55, 412);
        phoneCtx.fillText('✔ Ready for next payload.', 55, 442);
      }

      // Bottom Message Bar
      phoneCtx.fillStyle = '#1e293b';
      phoneCtx.fillRect(0, phoneCanvas.height - 90, phoneCanvas.width, 90);
      phoneCtx.fillStyle = '#334155';
      safeRoundRect(phoneCtx, 20, phoneCanvas.height - 70, phoneCanvas.width - 40, 50, 25);
      phoneCtx.fill();
      phoneCtx.fillStyle = '#94a3b8';
      phoneCtx.font = '16px sans-serif';
      phoneCtx.fillText('Message @n0accent...', 45, phoneCanvas.height - 38);
    }

    /* -------------------------------------------------------------------------
       ENGINE 3: RAILWAY DATACENTER DOCKER STREAM LOG CANVAS
       ------------------------------------------------------------------------- */
    const logCanvas = document.getElementById('railway-log-canvas');
    const logCtx = logCanvas.getContext('2d');

    const sampleLogLines = [
      '[INFO]  worker-01: Listening on unix:///var/run/docker.sock',
      '[INFO]  redis-cluster: 6 nodes synced. Memory: 142MB / 4GB',
      '[POSTGRES] Query executed in 1.2ms: SELECT * FROM telemetry_cache',
      '[DISPATCH] Event id #992817 delivered to Telegram API [200 OK]',
      '[HEALTH] Load balancer: 0.12% CPU, 45.2MB RSS, 0 err/sec',
      '[METRIC] InfluxDB batch written: 12,500 points in 8ms',
      '[AUTOSCALE] Provisioned worker-pod-33 on railway-fra-01',
      '[SUCCESS] Cluster state: 100% HEALTHY'
    ];

    function renderRailwayLogs(time) {
      logCtx.fillStyle = '#020617';
      logCtx.fillRect(0, 0, logCanvas.width, logCanvas.height);

      logCtx.fillStyle = '#38bdf8';
      logCtx.font = 'bold 15px monospace';
      logCtx.fillText('>> RAILWAY CLUSTER DOCKER MONITOR [LIVE]', 20, 35);

      logCtx.strokeStyle = 'rgba(56, 189, 248, 0.3)';
      logCtx.beginPath();
      logCtx.moveTo(20, 48); logCtx.lineTo(logCanvas.width - 20, 48);
      logCtx.stroke();

      const scrollOffset = (time * 25) % 28;
      logCtx.font = '12px monospace';

      sampleLogLines.forEach((line, idx) => {
        const y = 80 + idx * 28 - scrollOffset;
        if (y > 55 && y < 380) {
          if (line.includes('[SUCCESS]')) logCtx.fillStyle = '#10b981';
          else if (line.includes('[POSTGRES]')) logCtx.fillStyle = '#a855f7';
          else if (line.includes('[DISPATCH]')) logCtx.fillStyle = '#fbbf24';
          else logCtx.fillStyle = '#cbd5e1';

          logCtx.fillText(line, 20, y);
        }
      });

      // Live CPU & Network Mini-Graphs at Bottom
      logCtx.fillStyle = 'rgba(15, 23, 42, 0.9)';
      logCtx.fillRect(20, 390, logCanvas.width - 40, 100);
      logCtx.strokeStyle = '#00f2fe';
      logCtx.beginPath();
      for (let x = 0; x < logCanvas.width - 40; x += 10) {
        const gy = 440 + Math.sin(time * 6 + x * 0.1) * 22;
        if (x === 0) logCtx.moveTo(20 + x, gy);
        else logCtx.lineTo(20 + x, gy);
      }
      logCtx.stroke();
      logCtx.fillStyle = '#38bdf8';
      logCtx.fillText('REAL-TIME CLUSTER THROUGHPUT: 18.4 GB/s', 35, 415);
    }

    /* -------------------------------------------------------------------------
       ENGINE 4: PROCEDURAL PLANET TEXTURE CANVASES
       ------------------------------------------------------------------------- */
    function initProceduralPlanetTextures() {
      // 1. Gas Giant Canvas
      const pGasCanvas = document.getElementById('planet-gas-canvas');
      const pgCtx = pGasCanvas.getContext('2d');
      for (let y = 0; y < pGasCanvas.height; y++) {
        const grad = Math.sin(y * 0.08) * 0.5 + 0.5;
        pgCtx.fillStyle = `rgb(${Math.floor(180 * grad + 40)}, ${Math.floor(120 * grad + 60)}, ${Math.floor(240 * grad + 80)})`;
        pgCtx.fillRect(0, y, pGasCanvas.width, 1);
      }

      // 2. Cyber Planet Canvas
      const pCyberCanvas = document.getElementById('planet-cyber-canvas');
      const pcCtx = pCyberCanvas.getContext('2d');
      pcCtx.fillStyle = '#050c1e';
      pcCtx.fillRect(0, 0, pCyberCanvas.width, pCyberCanvas.height);
      pcCtx.strokeStyle = '#00f2fe';
      pcCtx.lineWidth = 2;
      for (let x = 0; x < pCyberCanvas.width; x += 32) {
        pcCtx.beginPath();
        pcCtx.moveTo(x, 0); pcCtx.lineTo(x, pCyberCanvas.height);
        pcCtx.stroke();
      }
      for (let y = 0; y < pCyberCanvas.height; y += 32) {
        pcCtx.beginPath();
        pcCtx.moveTo(0, y); pcCtx.lineTo(pCyberCanvas.width, y);
        pcCtx.stroke();
      }

      // 3. Lava Planet Canvas
      const pLavaCanvas = document.getElementById('planet-lava-canvas');
      const plCtx = pLavaCanvas.getContext('2d');
      for (let y = 0; y < pLavaCanvas.height; y++) {
        const grad = Math.cos(y * 0.05) * 0.5 + 0.5;
        plCtx.fillStyle = `rgb(${Math.floor(255 * grad)}, ${Math.floor(90 * grad)}, ${Math.floor(20 * grad)})`;
        plCtx.fillRect(0, y, pLavaCanvas.width, 1);
      }

      // 4. Cryo Ice Planet Canvas
      const pIceCanvas = document.getElementById('planet-ice-canvas');
      const piCtx = pIceCanvas.getContext('2d');
      for (let y = 0; y < pIceCanvas.height; y++) {
        const grad = Math.sin(y * 0.06) * 0.5 + 0.5;
        piCtx.fillStyle = `rgb(${Math.floor(80 * grad + 150)}, ${Math.floor(180 * grad + 70)}, 255)`;
        piCtx.fillRect(0, y, pIceCanvas.width, 1);
      }
    }
    initProceduralPlanetTextures();
"""

if __name__ == "__main__":
    games = generate_games_js()
    print(f"Generated Games JS: {len(games.splitlines())} lines")
