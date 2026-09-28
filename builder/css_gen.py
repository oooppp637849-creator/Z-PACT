# builder/css_gen.py
# Generates comprehensive, ultra-high-end CSS for the 10,000-line Scrollytelling Experience

def generate_css():
    return """    /* =========================================================================
       1. ULTRA-PREMIUM CYBERNETIC DESIGN SYSTEM & DESIGN TOKENS
       ========================================================================= */
    :root {
      --font-display: 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      --font-arabic: 'Cairo', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      --font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;

      --neon-cyan: #00f2fe;
      --neon-blue: #38bdf8;
      --neon-indigo: #6366f1;
      --neon-purple: #a855f7;
      --neon-emerald: #10b981;
      --neon-gold: #f59e0b;
      --neon-amber: #fbbf24;
      --neon-rose: #f43f5e;
      --neon-crimson: #ef4444;

      --bg-void: #02040a;
      --bg-dark-obsidian: #050814;
      --bg-glass-card: rgba(8, 14, 28, 0.88);
      --bg-glass-card-hover: rgba(15, 23, 42, 0.95);
      --border-glass: rgba(56, 189, 248, 0.25);
      --border-glass-bright: rgba(0, 242, 254, 0.6);
      --border-glass-gold: rgba(245, 158, 11, 0.5);

      --shadow-cyan-glow: 0 0 25px rgba(0, 242, 254, 0.35);
      --shadow-purple-glow: 0 0 25px rgba(168, 85, 247, 0.35);
      --shadow-gold-glow: 0 0 30px rgba(245, 158, 11, 0.4);
      --shadow-deep-card: 0 20px 45px rgba(0, 0, 0, 0.8), 0 0 2px rgba(255, 255, 255, 0.1);

      --transition-smooth: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
      --transition-bounce: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
    }

    *, *::before, *::after {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      -webkit-tap-highlight-color: transparent;
    }

    html, body {
      width: 100%;
      min-height: 100%;
      background-color: var(--bg-void);
      color: #f8fafc;
      font-family: var(--font-display);
      overflow-x: hidden;
      overflow-y: auto;
      scroll-behavior: auto;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }

    /* Custom high-tech scrollbar */
    ::-webkit-scrollbar {
      width: 6px;
    }
    ::-webkit-scrollbar-track {
      background: #02040a;
    }
    ::-webkit-scrollbar-thumb {
      background: linear-gradient(180deg, #38bdf8, #a855f7, #f59e0b);
      border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #00f2fe;
    }

    /* =========================================================================
       2. THREE.JS MASTER CANVAS & SCROLL TRACK CONTAINER
       ========================================================================= */
    #ue-canvas-container {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: 1;
      pointer-events: none;
      overflow: hidden;
    }

    #ue-canvas {
      width: 100%;
      height: 100%;
      display: block;
      pointer-events: auto;
    }

    /* Native unfreezable scroll track spacer (3500vh for long interstellar odyssey) */
    #scroll-track {
      width: 100%;
      height: 3500vh;
      position: relative;
      pointer-events: none;
    }

    /* Offscreen canvases for procedural animated textures */
    .hidden-sim-canvas {
      position: absolute;
      top: -9999px;
      left: -9999px;
      visibility: hidden;
      pointer-events: none;
    }

    /* =========================================================================
       3. CINEMATIC OVERLAYS & POST-PROCESS SCANLINES
       ========================================================================= */
    #scanlines-layer {
      position: fixed;
      inset: 0;
      z-index: 8;
      pointer-events: none;
      background: linear-gradient(
        rgba(18, 16, 16, 0) 50%,
        rgba(0, 0, 0, 0.45) 50%
      ),
      linear-gradient(
        90deg,
        rgba(255, 0, 0, 0.03),
        rgba(0, 255, 0, 0.01),
        rgba(0, 0, 255, 0.03)
      );
      background-size: 100% 3px, 6px 100%;
      opacity: 0.28;
      transition: opacity 0.5s ease;
    }

    #vignette-overlay {
      position: fixed;
      inset: 0;
      z-index: 9;
      pointer-events: none;
      background: radial-gradient(
        circle at 50% 50%,
        transparent 55%,
        rgba(2, 4, 10, 0.75) 85%,
        rgba(2, 4, 10, 0.98) 100%
      );
    }

    #glitch-burst {
      position: fixed;
      inset: 0;
      z-index: 10;
      pointer-events: none;
      background: rgba(0, 242, 254, 0.15);
      mix-blend-mode: screen;
      opacity: 0;
      transition: opacity 0.08s ease-out;
    }

    /* =========================================================================
       4. TOP FLIGHT HUD & REAL-TIME TELEMETRY BAR
       ========================================================================= */
    #top-nav-bar {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 64px;
      padding: 0 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      z-index: 100;
      background: linear-gradient(180deg, rgba(2, 4, 10, 0.92) 0%, rgba(2, 4, 10, 0.4) 75%, transparent 100%);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border-bottom: 1px solid rgba(56, 189, 248, 0.15);
      pointer-events: auto;
    }

    .hud-brand-group {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .hud-logo-icon {
      width: 38px;
      height: 38px;
      border-radius: 10px;
      background: linear-gradient(135deg, #00f2fe, #6366f1);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.15rem;
      font-weight: 800;
      color: #02040a;
      box-shadow: 0 0 16px rgba(0, 242, 254, 0.5);
    }

    .hud-title-col {
      display: flex;
      flex-direction: column;
    }

    .hud-main-title {
      font-size: 0.95rem;
      font-weight: 700;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      background: linear-gradient(90deg, #f8fafc, #38bdf8);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .hud-sub-role {
      font-size: 0.72rem;
      font-family: var(--font-arabic);
      color: #94a3b8;
      font-weight: 600;
      letter-spacing: 0.05em;
    }

    .hud-telemetry-badges {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .telemetry-chip {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 12px;
      border-radius: 20px;
      background: rgba(15, 23, 42, 0.65);
      border: 1px solid rgba(56, 189, 248, 0.2);
      font-size: 0.74rem;
      font-family: var(--font-mono);
      letter-spacing: 0.05em;
      color: #e2e8f0;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
    }

    .telemetry-chip .chip-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #10b981;
      box-shadow: 0 0 8px #10b981;
      animation: pulseGlow 1.8s infinite;
    }

    .telemetry-chip.warp .chip-dot {
      background: #38bdf8;
      box-shadow: 0 0 8px #38bdf8;
    }

    .telemetry-chip.fps .chip-dot {
      background: #f59e0b;
      box-shadow: 0 0 8px #f59e0b;
    }

    .hud-actions-group {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .hud-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      border-radius: 12px;
      background: rgba(15, 23, 42, 0.75);
      border: 1px solid rgba(56, 189, 248, 0.3);
      color: #f8fafc;
      font-family: var(--font-mono);
      font-size: 0.78rem;
      font-weight: 600;
      cursor: pointer;
      transition: var(--transition-smooth);
      outline: none;
    }

    .hud-btn:hover {
      background: rgba(56, 189, 248, 0.2);
      border-color: #00f2fe;
      box-shadow: 0 0 16px rgba(0, 242, 254, 0.35);
      transform: translateY(-1px);
    }

    .hud-btn.active {
      background: linear-gradient(135deg, rgba(0, 242, 254, 0.25), rgba(99, 102, 241, 0.25));
      border-color: #00f2fe;
      color: #00f2fe;
    }

    /* Top Timeline Scrubber Bar */
    #timeline-scrubber {
      position: fixed;
      top: 64px;
      left: 0;
      width: 100%;
      height: 3px;
      background: rgba(15, 23, 42, 0.85);
      z-index: 99;
      pointer-events: none;
    }

    #timeline-progress {
      width: 0%;
      height: 100%;
      background: linear-gradient(90deg, #00f2fe, #38bdf8, #a855f7, #fbbf24, #10b981);
      box-shadow: 0 0 10px #00f2fe;
      transition: width 0.08s linear;
    }

    /* =========================================================================
       5. 2D ORBITAL RADAR MINIMAP (TOP RIGHT)
       ========================================================================= */
    #space-radar-panel {
      position: fixed;
      top: 80px;
      right: 24px;
      width: 160px;
      height: 160px;
      border-radius: 50%;
      background: rgba(2, 6, 18, 0.82);
      border: 1px solid rgba(56, 189, 248, 0.35);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.7), inset 0 0 24px rgba(0, 242, 254, 0.15);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      z-index: 50;
      pointer-events: auto;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      transition: var(--transition-smooth);
    }

    #space-radar-panel:hover {
      border-color: #00f2fe;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.8), 0 0 20px rgba(0, 242, 254, 0.3);
    }

    #radar-canvas {
      width: 100%;
      height: 100%;
      display: block;
    }

    .radar-tag {
      position: absolute;
      bottom: 8px;
      font-size: 0.62rem;
      font-family: var(--font-mono);
      color: #38bdf8;
      letter-spacing: 0.1em;
      background: rgba(2, 6, 18, 0.75);
      padding: 2px 6px;
      border-radius: 4px;
      border: 1px solid rgba(56, 189, 248, 0.25);
    }

    /* =========================================================================
       6. SPACE EXPLORATION TELEMETRY HUD (LEFT COCKPIT)
       ========================================================================= */
    #space-hud {
      position: fixed;
      top: 88px;
      left: 24px;
      z-index: 50;
      display: flex;
      flex-direction: column;
      gap: 12px;
      pointer-events: none;
      transition: opacity 0.5s ease, transform 0.5s ease;
      opacity: 0;
      transform: translateX(-30px);
    }

    #space-hud.active {
      opacity: 1;
      transform: translateX(0);
      pointer-events: auto;
    }

    .hud-panel-card {
      background: var(--bg-glass-card);
      border: 1px solid var(--border-glass);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border-radius: 16px;
      padding: 16px 20px;
      box-shadow: var(--shadow-deep-card);
      min-width: 290px;
      max-width: 340px;
    }

    .hud-panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid rgba(56, 189, 248, 0.15);
      padding-bottom: 8px;
      margin-bottom: 12px;
    }

    .hud-panel-title {
      font-size: 0.75rem;
      font-family: var(--font-mono);
      font-weight: 700;
      letter-spacing: 0.12em;
      color: var(--neon-cyan);
      text-transform: uppercase;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .hud-panel-title::before {
      content: '';
      display: inline-block;
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--neon-cyan);
      box-shadow: 0 0 8px var(--neon-cyan);
    }

    .hud-data-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
      font-size: 0.74rem;
      font-family: var(--font-mono);
    }

    .hud-data-label {
      color: #94a3b8;
    }

    .hud-data-val {
      color: #f1f5f9;
      font-weight: 600;
    }

    .hud-data-val.accent {
      color: var(--neon-cyan);
    }

    .hud-data-val.gold {
      color: var(--neon-gold);
    }

    .hud-data-val.emerald {
      color: var(--neon-emerald);
    }

    /* Waveform visualizer */
    .hud-waveform {
      display: flex;
      align-items: flex-end;
      gap: 3px;
      height: 24px;
      margin-top: 10px;
      padding-top: 4px;
      border-top: 1px solid rgba(56, 189, 248, 0.1);
    }

    .waveform-bar {
      flex: 1;
      background: linear-gradient(180deg, var(--neon-cyan), var(--neon-indigo));
      border-radius: 2px;
      min-height: 3px;
      transition: height 0.1s ease;
    }

    /* =========================================================================
       7. HIGH-READABILITY ELEVATED SUBTITLE CARDS (CENTER-ELEVATED)
       ========================================================================= */
    /* =========================================================================
       CINEMATIC SUBTITLE SYSTEM — Fully Fixed, No Overflow, Mobile-First
       ========================================================================= */

    /* The viewport is a centered floating HUD strip.
       Positioned with safe clearance so text is NEVER cut off on mobile or desktop. */
    #subtitles-viewport {
      position: fixed;
      bottom: 24px;
      left: 0;
      width: 100%;
      z-index: 60;
      pointer-events: none;
      display: flex;
      justify-content: center;
      align-items: flex-end;
      padding: 0 16px;
      padding-bottom: max(env(safe-area-inset-bottom, 0px), 12px);
      transition: opacity 0.5s ease, transform 0.5s ease;
    }

    /* Floating cinematic subtitle card with smooth, natural transitions */
    .subtitle-glass-card {
      display: none;
      width: 100%;
      max-width: 680px;
      margin: 0 auto;
      background: rgba(5, 10, 22, 0.90);
      border: 1px solid rgba(56, 189, 248, 0.32);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      box-shadow:
        0 12px 40px rgba(0, 0, 0, 0.75),
        0 0 20px rgba(0, 242, 254, 0.12),
        inset 0 1px 0 rgba(255, 255, 255, 0.08);
      border-radius: 20px;
      padding: 16px 24px 14px;
      text-align: center;
      pointer-events: auto;
      opacity: 0;
      transform: translateY(12px) scale(0.98);
      will-change: transform, opacity;
      transition: opacity 0.45s cubic-bezier(0.16, 1, 0.3, 1), transform 0.45s cubic-bezier(0.16, 1, 0.3, 1);
    }

    /* ACTIVE state: gentle float up & fade in */
    .subtitle-glass-card.active {
      display: block;
      opacity: 1;
      transform: translateY(0) scale(1);
    }

    /* EXIT state: soft float up & fade out */
    .subtitle-glass-card.exit {
      display: block;
      opacity: 0;
      transform: translateY(-8px) scale(0.98);
    }

    /* Scanning neon line at the top of the active card */
    .subtitle-glass-card.active::before {
      content: '';
      position: absolute;
      top: 0;
      left: 10%;
      width: 80%;
      height: 1px;
      background: linear-gradient(90deg, transparent, #00f2fe 40%, #a855f7 60%, transparent);
      animation: scanPulse 2.5s ease-in-out infinite;
    }

    @keyframes scanPulse {
      0%,100% { opacity: 0.5; }
      50%      { opacity: 1;   }
    }

    /* Phase badge — compact, never wraps */
    .sub-phase-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 3px 12px;
      border-radius: 10px;
      background: rgba(56, 189, 248, 0.12);
      border: 1px solid rgba(56, 189, 248, 0.32);
      font-size: clamp(0.58rem, 1.8vw, 0.7rem);
      font-family: var(--font-mono);
      font-weight: 700;
      letter-spacing: 0.1em;
      color: #38bdf8;
      text-transform: uppercase;
      margin-bottom: 8px;
      white-space: nowrap;
    }

    .sub-phase-badge.gold   { background: rgba(245,158,11,0.12); border-color: rgba(245,158,11,0.38); color: #fbbf24; }
    .sub-phase-badge.purple { background: rgba(168,85,247,0.12);  border-color: rgba(168,85,247,0.38); color: #c084fc; }
    .sub-phase-badge.emerald{ background: rgba(16,185,129,0.12);  border-color: rgba(16,185,129,0.38); color: #34d399; }

    /* Arabic headline — responsive, never overflow, hard max 2 lines */
    .sub-arabic-headline {
      font-family: var(--font-arabic);
      font-size: clamp(1.05rem, 3.5vw, 1.75rem);
      font-weight: 800;
      line-height: 1.3;
      color: #ffffff;
      text-shadow:
        0 2px 10px rgba(0,0,0,0.95),
        0 0 18px rgba(56,189,248,0.3);
      margin-bottom: 4px;
      direction: rtl;
      /* Prevent overflow on tiny screens */
      overflow: hidden;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
    }

    /* English subtext — one line, truncated if needed */
    .sub-english-subtext {
      font-family: var(--font-display);
      font-size: clamp(0.65rem, 1.6vw, 0.9rem);
      font-weight: 600;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: #64748b;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    /* Interactive hint — hidden on very small screens */
    .sub-interactive-hint {
      margin-top: 8px;
      font-size: clamp(0.6rem, 1.5vw, 0.72rem);
      font-family: var(--font-mono);
      color: #38bdf8;
      opacity: 0.75;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 5px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    /* On very small phones (< 380px) hide the hint to save space */
    @media (max-width: 380px) {
      .sub-interactive-hint { display: none; }
      .sub-arabic-headline { font-size: 0.98rem; }
    }

    /* Tablet tweak */
    @media (min-width: 768px) {
      .subtitle-glass-card {
        border-radius: 20px;
        margin-bottom: 16px;
        padding: 18px 30px 14px;
      }
    }

    /* =========================================================================
       8. QUICK STEP CONTROLS & TIMELINE SCRUBBERS (BOTTOM LEFT)
       ========================================================================= */
    #quick-controls {
      position: fixed;
      bottom: 140px;   /* Sits above the subtitle card strip */
      left: 16px;
      z-index: 70;
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
      pointer-events: auto;
      max-width: calc(100vw - 32px);
    }

    /* On tablet+ push to left and use larger gap */
    @media (min-width: 640px) {
      #quick-controls {
        bottom: 150px;
        left: 24px;
        gap: 10px;
      }
    }

    .ctrl-pill {
      background: rgba(8, 14, 28, 0.85);
      border: 1px solid rgba(56, 189, 248, 0.3);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border-radius: 14px;
      padding: 8px 14px;
      color: #e2e8f0;
      font-family: var(--font-mono);
      font-size: 0.78rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      transition: var(--transition-smooth);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.6);
      outline: none;
    }

    .ctrl-pill:hover {
      background: rgba(56, 189, 248, 0.2);
      border-color: #00f2fe;
      color: #00f2fe;
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(0, 242, 254, 0.3);
    }

    /* Scroll Prompt (Bottom Center) — sits above subtitle card */
    #scroll-prompt {
      position: fixed;
      bottom: 145px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 65;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      pointer-events: none;
      transition: opacity 0.5s ease;
    }

    .scroll-arrow-anim {
      width: 20px;
      height: 32px;
      border: 2px solid rgba(56, 189, 248, 0.6);
      border-radius: 12px;
      display: flex;
      justify-content: center;
      padding-top: 6px;
    }

    .scroll-arrow-anim::before {
      content: '';
      width: 4px;
      height: 8px;
      background: #00f2fe;
      border-radius: 2px;
      animation: mouseWheelAnim 1.6s infinite ease-in-out;
    }

    .scroll-prompt-text {
      font-size: 0.72rem;
      font-family: var(--font-mono);
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: #94a3b8;
    }

    /* =========================================================================
       9. INTERACTIVE COSMIC TERMINAL DRAWER (RIGHT SLIDE-OUT)
       ========================================================================= */
    #cosmic-terminal {
      position: fixed;
      top: 0;
      right: 0;
      width: 520px;
      max-width: 90vw;
      height: 100vh;
      background: rgba(4, 7, 16, 0.95);
      border-left: 1px solid rgba(56, 189, 248, 0.3);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      box-shadow: -10px 0 50px rgba(0, 0, 0, 0.9), -2px 0 20px rgba(0, 242, 254, 0.15);
      z-index: 200;
      display: flex;
      flex-direction: column;
      transform: translateX(100%);
      transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
      pointer-events: auto;
    }

    #cosmic-terminal.open {
      transform: translateX(0);
    }

    .term-header {
      padding: 16px 20px;
      background: rgba(10, 16, 32, 0.85);
      border-bottom: 1px solid rgba(56, 189, 248, 0.2);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .term-title {
      font-family: var(--font-mono);
      font-size: 0.82rem;
      font-weight: 700;
      letter-spacing: 0.1em;
      color: var(--neon-cyan);
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .term-dots {
      display: flex;
      gap: 6px;
    }

    .term-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }
    .term-dot.red { background: #ef4444; }
    .term-dot.yellow { background: #f59e0b; }
    .term-dot.green { background: #10b981; }

    .term-close-btn {
      background: transparent;
      border: none;
      color: #94a3b8;
      font-size: 1.2rem;
      cursor: pointer;
      transition: color 0.2s;
    }
    .term-close-btn:hover {
      color: #f8fafc;
    }

    .term-tabs {
      display: flex;
      background: rgba(6, 10, 22, 0.7);
      border-bottom: 1px solid rgba(56, 189, 248, 0.15);
      overflow-x: auto;
    }

    .term-tab {
      padding: 10px 16px;
      font-family: var(--font-mono);
      font-size: 0.74rem;
      color: #94a3b8;
      cursor: pointer;
      border-right: 1px solid rgba(56, 189, 248, 0.1);
      transition: var(--transition-smooth);
      white-space: nowrap;
    }

    .term-tab:hover, .term-tab.active {
      color: var(--neon-cyan);
      background: rgba(56, 189, 248, 0.12);
    }

    .term-body {
      flex: 1;
      padding: 16px 20px;
      overflow-y: auto;
      font-family: var(--font-mono);
      font-size: 0.82rem;
      line-height: 1.6;
      color: #cbd5e1;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .term-body::-webkit-scrollbar {
      width: 4px;
    }
    .term-body::-webkit-scrollbar-thumb {
      background: rgba(56, 189, 248, 0.3);
      border-radius: 2px;
    }

    .term-input-row {
      padding: 14px 20px;
      background: rgba(10, 16, 32, 0.9);
      border-top: 1px solid rgba(56, 189, 248, 0.2);
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .term-prompt-symbol {
      color: var(--neon-cyan);
      font-family: var(--font-mono);
      font-weight: 700;
    }

    #term-cli-input {
      flex: 1;
      background: transparent;
      border: none;
      color: #f8fafc;
      font-family: var(--font-mono);
      font-size: 0.84rem;
      outline: none;
    }

    /* Terminal Quick Action Buttons */
    .term-quick-btns {
      padding: 10px 20px;
      background: rgba(6, 10, 22, 0.85);
      border-top: 1px solid rgba(56, 189, 248, 0.12);
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .term-q-btn {
      padding: 4px 10px;
      border-radius: 6px;
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid rgba(56, 189, 248, 0.2);
      color: #38bdf8;
      font-family: var(--font-mono);
      font-size: 0.72rem;
      cursor: pointer;
      transition: var(--transition-smooth);
    }

    .term-q-btn:hover {
      background: rgba(56, 189, 248, 0.25);
      color: #00f2fe;
    }

    /* =========================================================================
       10. STAGE 6: FINAL Z-PACT HOMEWORLD CLIMAX SHOWCASE
       ========================================================================= */
    #final-climax-stage {
      position: absolute;
      top: 3100vh;
      left: 0;
      width: 100%;
      min-height: 400vh;
      z-index: 80;
      pointer-events: auto;
      background: linear-gradient(180deg, transparent 0%, rgba(2, 4, 10, 0.92) 15%, #02040a 100%);
      padding: 80px 24px 140px 24px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    /* ─── FLUID SCROLL-REVEAL SYSTEM ────────────────────────────────────────────
       Elements start invisible and gently float up naturally with scroll.
       Driven by IntersectionObserver — fluid, organic, non-explosive motion.
    ─────────────────────────────────────────────────────────────────────────── */
    .reveal {
      opacity: 0;
      transform: translateY(18px);
      transition:
        opacity 0.85s cubic-bezier(0.16, 1, 0.3, 1),
        transform 0.85s cubic-bezier(0.16, 1, 0.3, 1);
      will-change: opacity, transform;
    }

    .reveal.visible {
      opacity: 1;
      transform: translateY(0);
    }

    /* Stagger delays for child elements (used on grids) */
    .reveal-stagger > * {
      opacity: 0;
      transform: translateY(16px);
      transition:
        opacity 0.75s cubic-bezier(0.16, 1, 0.3, 1),
        transform 0.75s cubic-bezier(0.16, 1, 0.3, 1);
      will-change: opacity, transform;
    }

    .reveal-stagger.visible > *:nth-child(1) { opacity:1; transform:translateY(0); transition-delay: 0.00s; }
    .reveal-stagger.visible > *:nth-child(2) { opacity:1; transform:translateY(0); transition-delay: 0.08s; }
    .reveal-stagger.visible > *:nth-child(3) { opacity:1; transform:translateY(0); transition-delay: 0.16s; }
    .reveal-stagger.visible > *:nth-child(4) { opacity:1; transform:translateY(0); transition-delay: 0.24s; }
    .reveal-stagger.visible > *:nth-child(5) { opacity:1; transform:translateY(0); transition-delay: 0.32s; }
    .reveal-stagger.visible > *:nth-child(6) { opacity:1; transform:translateY(0); transition-delay: 0.40s; }

    .climax-container {
      max-width: 1200px;
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 60px;
    }

    /* Creator Hero Header */
    .creator-hero-card {
      background: var(--bg-glass-card);
      border: 1px solid var(--border-glass);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border-radius: 28px;
      padding: 48px;
      box-shadow: var(--shadow-deep-card);
      display: grid;
      grid-template-columns: 240px 1fr;
      gap: 40px;
      align-items: center;
      position: relative;
      overflow: hidden;
    }

    .creator-hero-card::before {
      content: '';
      position: absolute;
      top: -100px;
      right: -100px;
      width: 300px;
      height: 300px;
      background: radial-gradient(circle, rgba(0, 242, 254, 0.2), transparent 70%);
      pointer-events: none;
    }

    .creator-avatar-wrap {
      width: 220px;
      height: 220px;
      border-radius: 24px;
      overflow: hidden;
      border: 2px solid rgba(56, 189, 248, 0.5);
      box-shadow: 0 0 35px rgba(0, 242, 254, 0.35);
      position: relative;
      background: #02040a;
    }

    .creator-avatar-img,
    .creator-avatar-video {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transition: transform 0.6s ease;
    }

    .creator-avatar-wrap:hover .creator-avatar-img,
    .creator-avatar-wrap:hover .creator-avatar-video {
      transform: scale(1.05);
    }

    .creator-bio-content {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .creator-badge-row {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }

    .creator-hero-name {
      font-family: var(--font-arabic);
      font-size: clamp(2rem, 4vw, 3.2rem);
      font-weight: 900;
      color: #ffffff;
      line-height: 1.2;
    }

    .creator-hero-title {
      font-family: var(--font-display);
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: 0.1em;
      background: linear-gradient(90deg, #38bdf8, #a855f7);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      text-transform: uppercase;
    }

    .creator-hero-desc {
      font-family: var(--font-arabic);
      font-size: 1.05rem;
      line-height: 1.75;
      color: #94a3b8;
      direction: rtl;
      text-align: right;
    }

    /* KPI Metrics Grid */
    .kpi-metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 24px;
    }

    .kpi-card {
      background: var(--bg-glass-card);
      border: 1px solid var(--border-glass);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-radius: 20px;
      padding: 28px 24px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      box-shadow: var(--shadow-deep-card);
      transition: var(--transition-smooth);
      position: relative;
      overflow: hidden;
    }

    .kpi-card:hover {
      border-color: #00f2fe;
      transform: translateY(-4px);
      box-shadow: 0 16px 36px rgba(0, 242, 254, 0.25);
    }

    .kpi-number {
      font-family: var(--font-mono);
      font-size: 2.8rem;
      font-weight: 900;
      background: linear-gradient(90deg, #00f2fe, #38bdf8);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .kpi-label {
      font-family: var(--font-arabic);
      font-size: 1.05rem;
      font-weight: 700;
      color: #ffffff;
      direction: rtl;
      text-align: right;
    }

    .kpi-sub {
      font-size: 0.78rem;
      font-family: var(--font-mono);
      color: #64748b;
      letter-spacing: 0.05em;
    }

    /* Production Systems Portfolio Grid */
    .portfolio-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
      gap: 28px;
    }

    .project-card {
      background: var(--bg-glass-card);
      border: 1px solid var(--border-glass);
      border-radius: 22px;
      padding: 32px 28px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      box-shadow: var(--shadow-deep-card);
      transition: var(--transition-smooth);
    }

    .project-card:hover {
      border-color: #38bdf8;
      transform: translateY(-5px);
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.8), 0 0 25px rgba(56, 189, 248, 0.25);
    }

    .project-badge {
      align-self: flex-start;
      padding: 4px 12px;
      border-radius: 8px;
      background: rgba(56, 189, 248, 0.15);
      border: 1px solid rgba(56, 189, 248, 0.3);
      font-family: var(--font-mono);
      font-size: 0.72rem;
      color: #38bdf8;
    }

    .project-title {
      font-family: var(--font-display);
      font-size: 1.35rem;
      font-weight: 800;
      color: #ffffff;
    }

    .project-desc {
      font-family: var(--font-arabic);
      font-size: 0.95rem;
      line-height: 1.65;
      color: #94a3b8;
      direction: rtl;
      text-align: right;
    }

    .project-tech-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .tech-tag {
      padding: 4px 10px;
      border-radius: 6px;
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid rgba(255, 255, 255, 0.1);
      font-family: var(--font-mono);
      font-size: 0.7rem;
      color: #cbd5e1;
    }

    /* Climax Action CTAs */
    .climax-cta-row {
      display: flex;
      justify-content: center;
      gap: 20px;
      flex-wrap: wrap;
      margin-top: 20px;
    }

    .cta-btn {
      display: inline-flex;
      align-items: center;
      gap: 12px;
      padding: 16px 36px;
      border-radius: 16px;
      font-family: var(--font-arabic);
      font-size: 1.1rem;
      font-weight: 700;
      text-decoration: none;
      cursor: pointer;
      transition: var(--transition-bounce);
    }

    .cta-btn.primary {
      background: linear-gradient(135deg, #00f2fe, #6366f1);
      color: #02040a;
      box-shadow: 0 0 30px rgba(0, 242, 254, 0.45);
      border: none;
    }

    .cta-btn.primary:hover {
      transform: translateY(-3px) scale(1.02);
      box-shadow: 0 0 45px rgba(0, 242, 254, 0.7);
    }

    .cta-btn.secondary {
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(56, 189, 248, 0.35);
      color: #f8fafc;
    }

    .cta-btn.secondary:hover {
      background: rgba(56, 189, 248, 0.2);
      border-color: #00f2fe;
      transform: translateY(-3px);
      box-shadow: 0 0 25px rgba(0, 242, 254, 0.3);
    }

    /* =========================================================================
       11. KEYFRAME ANIMATIONS & RESPONSIVE BREAKPOINTS
       ========================================================================= */
    @keyframes pulseGlow {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(0.85); }
    }

    @keyframes mouseWheelAnim {
      0% { opacity: 1; transform: translateY(0); }
      100% { opacity: 0; transform: translateY(12px); }
    }

    @keyframes radarSweep {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    @media (max-width: 1024px) {
      .creator-hero-card {
        grid-template-columns: 1fr;
        text-align: center;
        padding: 32px;
      }
      .creator-avatar-wrap {
        margin: 0 auto;
      }
      .creator-hero-desc {
        text-align: center;
      }
      #space-hud {
        display: none;
      }
    }

    @media (max-width: 768px) {
      #top-nav-bar {
        padding: 0 14px;
      }
      .telemetry-chip.warp, .telemetry-chip.fps {
        display: none;
      }
      #space-radar-panel {
        top: 72px;
        right: 14px;
        width: 110px;
        height: 110px;
      }
      #subtitles-viewport {
        bottom: 10vh;
        padding: 0 12px;
      }
      .subtitle-glass-card {
        padding: 18px 20px;
        border-radius: 18px;
      }
      .sub-arabic-headline {
        font-size: 1.25rem;
      }
      .sub-english-subtext {
        font-size: 0.78rem;
      }
      #quick-controls {
        bottom: 14px;
        left: 14px;
      }
      .ctrl-pill {
        padding: 6px 10px;
        font-size: 0.7rem;
      }
    }
"""

if __name__ == "__main__":
    css = generate_css()
    print(f"Generated CSS: {len(css.splitlines())} lines")
