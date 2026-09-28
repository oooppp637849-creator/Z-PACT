# builder/html_gen.py
# Generates comprehensive, high-contrast, crystal-clear HTML DOM for the 10,000-line Scrollytelling Experience

def generate_html_body():
    return """  <!-- =========================================================================
       MASTER THREE.JS WEBGL CANVAS CONTAINER
       ========================================================================= -->
  <div id="ue-canvas-container">
    <canvas id="ue-canvas"></canvas>
  </div>

  <!-- NATIVE UNFREEZABLE SCROLL TRACK (3500vh FOR PROLONGED DEEP SPACE VOYAGE) -->
  <div id="scroll-track"></div>

  <!-- OFFSCREEN CANVASES FOR PROCEDURAL TEXTURE GENERATION -->
  <canvas id="crt-game-canvas" class="hidden-sim-canvas" width="640" height="480"></canvas>
  <canvas id="phone-sim-canvas" class="hidden-sim-canvas" width="512" height="1024"></canvas>
  <canvas id="railway-log-canvas" class="hidden-sim-canvas" width="512" height="512"></canvas>
  <canvas id="planet-gas-canvas" class="hidden-sim-canvas" width="1024" height="512"></canvas>
  <canvas id="planet-cyber-canvas" class="hidden-sim-canvas" width="1024" height="512"></canvas>
  <canvas id="planet-lava-canvas" class="hidden-sim-canvas" width="1024" height="512"></canvas>
  <canvas id="planet-ice-canvas" class="hidden-sim-canvas" width="1024" height="512"></canvas>

  <!-- CINEMATIC FILMIC POST-PROCESS OVERLAYS -->
  <div id="scanlines-layer"></div>
  <div id="vignette-overlay"></div>
  <div id="glitch-burst"></div>

  <!-- =========================================================================
       TOP FLIGHT HUD & TELEMETRY NAV BAR
       ========================================================================= -->
  <header id="top-nav-bar">
    <div class="hud-brand-group">
      <div class="hud-logo-icon">Z</div>
      <div class="hud-title-col">
        <span class="hud-main-title">ABDO SABER // VOYAGE</span>
        <span class="hud-sub-role">مهندس أتمتة الأنظمة والذكاء الاصطناعي</span>
      </div>
    </div>

    <!-- Live Telemetry Badges -->
    <div class="hud-telemetry-badges">
      <div class="telemetry-chip">
        <span class="chip-dot"></span>
        <span>STATUS: <b id="telemetry-status-text" style="color:#10b981;">SYS_OPTIMAL</b></span>
      </div>
      <div class="telemetry-chip warp">
        <span class="chip-dot"></span>
        <span>WARP: <b id="telemetry-warp-text" style="color:#38bdf8;">0.00 c</b></span>
      </div>
      <div class="telemetry-chip fps">
        <span class="chip-dot"></span>
        <span>FPS: <b id="telemetry-fps-text" style="color:#f59e0b;">60</b></span>
      </div>
    </div>

    <!-- Top Action Buttons -->
    <div class="hud-actions-group">
      <button id="audio-toggle-btn" class="hud-btn" onclick="toggleCosmicAudio()" title="تبديل المؤثرات الصوتية">
        <span id="audio-btn-icon">🔊</span>
        <span id="audio-btn-label">AUDIO: ACTIVE</span>
      </button>
      <button class="hud-btn" onclick="toggleTerminal()" title="فتح وحدة التحكم الكونية">
        <span>⚡</span>
        <span>TERMINAL [CLI]</span>
      </button>
    </div>
  </header>

  <!-- TOP TIMELINE SCRUBBER -->
  <div id="timeline-scrubber">
    <div id="timeline-progress"></div>
  </div>

  <!-- =========================================================================
       2D ORBITAL RADAR MINIMAP (TOP RIGHT)
       ========================================================================= -->
  <div id="space-radar-panel" title="رادار الملاحة الكونية بعيد المدى">
    <canvas id="radar-canvas" width="160" height="160"></canvas>
    <div class="radar-tag">RADAR 360°</div>
  </div>

  <!-- =========================================================================
       SPACE EXPLORATION TELEMETRY HUD (LEFT COCKPIT)
       ========================================================================= -->
  <div id="space-hud">
    <div class="hud-panel-card">
      <div class="hud-panel-header">
        <span class="hud-panel-title">STELLAR TELEMETRY</span>
        <span id="hud-nav-mode" style="font-size:0.68rem; color:#38bdf8; font-family:var(--font-mono);">AUTO-PILOT</span>
      </div>

      <div class="hud-data-row">
        <span class="hud-data-label">SECTOR:</span>
        <span class="hud-data-val accent" id="hud-val-sector">INTERSTELLAR HIGHWAY</span>
      </div>

      <div class="hud-data-row">
        <span class="hud-data-label">TARGET:</span>
        <span class="hud-data-val gold" id="hud-val-target">SCANNING EXOPLANETS...</span>
      </div>

      <div class="hud-data-row">
        <span class="hud-data-label">DISTANCE:</span>
        <span class="hud-data-val" id="hud-val-distance">1,480 AU</span>
      </div>

      <div class="hud-data-row">
        <span class="hud-data-label">ATMOSPHERE:</span>
        <span class="hud-data-val emerald" id="hud-val-atmo">METHANE / HYDROGEN</span>
      </div>

      <div class="hud-data-row">
        <span class="hud-data-label">ANOMALIES:</span>
        <span class="hud-data-val accent" id="hud-val-anomalies">0 DETECTED</span>
      </div>

      <!-- Real-time audio waveform visualizer -->
      <div class="hud-waveform" id="hud-waveform-bars">
        <div class="waveform-bar" style="height: 40%;"></div>
        <div class="waveform-bar" style="height: 65%;"></div>
        <div class="waveform-bar" style="height: 90%;"></div>
        <div class="waveform-bar" style="height: 50%;"></div>
        <div class="waveform-bar" style="height: 75%;"></div>
        <div class="waveform-bar" style="height: 30%;"></div>
        <div class="waveform-bar" style="height: 85%;"></div>
        <div class="waveform-bar" style="height: 60%;"></div>
        <div class="waveform-bar" style="height: 45%;"></div>
        <div class="waveform-bar" style="height: 95%;"></div>
        <div class="waveform-bar" style="height: 70%;"></div>
        <div class="waveform-bar" style="height: 35%;"></div>
      </div>
    </div>
  </div>

  <!-- =========================================================================
       HIGH-READABILITY ELEVATED SUBTITLE CARDS (CENTER VIEWPORT)
       ========================================================================= -->
  <div id="subtitles-viewport">

    <!-- SUB 1: NOSTALGIA CRT GAMING — starts visible on load -->
    <div id="sub-1" class="subtitle-glass-card" style="display:block;opacity:1;transform:translateY(0) scale(1);">
      <div class="sub-phase-badge">STAGE 01 // 2009 NOSTALGIA</div>
      <h2 class="sub-arabic-headline">حيث بدأت الحكاية.. أمام شاشات CRT وألعاب الطفولة</h2>
      <p class="sub-english-subtext">THE GENESIS // RETRO CRT PHOSPHOR & ARCADE PASSION</p>
      <div class="sub-interactive-hint">
        <span>🎮 محاكاة ألعاب حقيقية على الشاشة: Plants vs Zombies, TMNT, WolfTeam</span>
      </div>
    </div>

    <!-- SUB 2: THE GLITCH FREEZE & CRASH -->
    <div id="sub-2" class="subtitle-glass-card">
      <div class="sub-phase-badge purple">STAGE 02 // SYSTEM CRITICAL</div>
      <h2 class="sub-arabic-headline">وفجأة.. تجمّد العالم، وانهارت طبقات الزجاج</h2>
      <p class="sub-english-subtext">FATAL EXCEPTION // THE BREAK THROUGH REALITY</p>
      <div class="sub-interactive-hint">
        <span>⚡ انهيار فيزيائي 3D لشاشة الـ CRT وتشتت الشظايا</span>
      </div>
    </div>

    <!-- SUB 3: THE VOID & HELLO WORLD -->
    <div id="sub-3" class="subtitle-glass-card">
      <div class="sub-phase-badge emerald">STAGE 03 // THE CODE VOID</div>
      <h2 class="sub-arabic-headline">السطر الأول.. حين أنارت لغة الآلة الظلام الدامس</h2>
      <p class="sub-english-subtext">print("Hello, World!") // BIRTH OF LOGIC</p>
      <div class="sub-interactive-hint">
        <span>🟢 أمطار مصفوفة كود الماتريكس في فضاء ثلاثي الأبعاد</span>
      </div>
    </div>

    <!-- SUB 4: AI AWAKENING & NEURAL SWARM -->
    <div id="sub-4" class="subtitle-glass-card">
      <div class="sub-phase-badge">STAGE 04 // NEURAL GENESIS</div>
      <h2 class="sub-arabic-headline">يقظة الذكاء الاصطناعي.. 100 ألف جسيم يشكلون العقل الرقمي</h2>
      <p class="sub-english-subtext">AI SINGULARITY // 100,000 GPGPU NEURAL CORE</p>
      <div class="sub-interactive-hint">
        <span>✨ حرّك الماوس أو اللمس للتفاعل مع المجال المغناطيسي العصبي</span>
      </div>
    </div>

    <!-- SUB 5: TELEGRAM AUTOMATION & RAILWAY DATACENTER -->
    <div id="sub-5" class="subtitle-glass-card">
      <div class="sub-phase-badge gold">STAGE 05 // CLOUD ORCHESTRATION</div>
      <h2 class="sub-arabic-headline">أتمتة تيليجرام الضخمة.. وسيرفرات سحابية تنبض بالبيانات</h2>
      <p class="sub-english-subtext">TELEGRAM BOT SWARM // RAILWAY CLOUD DATACENTER</p>
      <div class="sub-interactive-hint">
        <span>☁️ بث مباشر لتدفق بيانات الدوكر وسجلات الأوامر في الوقت الفعلي</span>
      </div>
    </div>

    <!-- SUB 6: DEPARTURE INTO DEEP SPACE -->
    <div id="sub-6" class="subtitle-glass-card">
      <div class="sub-phase-badge">STAGE 06 // COSMIC LAUNCH</div>
      <h2 class="sub-arabic-headline">الانطلاق نحو المجهول.. مغادرة المدار وبدء رحلة الكواكب</h2>
      <p class="sub-english-subtext">WARP SPEED ENGAGED // DEEP SPACE EXPEDITION</p>
      <div class="sub-interactive-hint">
        <span>🚀 استكشاف الفضاء العميق وزيارة الكواكب والمجرات في رحلة ملحمية</span>
      </div>
    </div>

    <!-- SUB 7: PLANET AURA-9 (GAS GIANT) -->
    <div id="sub-7" class="subtitle-glass-card">
      <div class="sub-phase-badge gold">SECTOR 01 // EXOPLANET AURA-9</div>
      <h2 class="sub-arabic-headline">العملاق الغازي [AURA-9].. حلقات الميثان وعواصف لا تهدأ</h2>
      <p class="sub-english-subtext">JOVIAN GAS GIANT // ATMOSPHERIC RESONANCE</p>
      <div class="sub-interactive-hint">
        <span>🪐 3 أقمار تدور في مدارات متزامنة مع حلقات كريستالية مضيئة</span>
      </div>
    </div>

    <!-- SUB 8: PLANET GLACIES (CRYO ICE WORLD) -->
    <div id="sub-8" class="subtitle-glass-card">
      <div class="sub-phase-badge emerald">SECTOR 02 // EXOPLANET GLACIES</div>
      <h2 class="sub-arabic-headline">عالم الجليد الأبدي [GLACIES].. تبلور البيانات عند الصفر المطلق</h2>
      <p class="sub-english-subtext">CRYO-WORLD // ABSOLUTE ZERO DATA VAULT</p>
      <div class="sub-interactive-hint">
        <span>❄️ كهوف كريستالية تحفظ الشيفرات البرمجية للأبد</span>
      </div>
    </div>

    <!-- SUB 9: PLANET NEXUS-01 (CYBERNETIC CORE) -->
    <div id="sub-9" class="subtitle-glass-card">
      <div class="sub-phase-badge purple">SECTOR 03 // NEXUS-01 CYBER CORE</div>
      <h2 class="sub-arabic-headline">كوكب السيبرانية [NEXUS-01].. شبكة دوائر كمومية تحيط بالعالم</h2>
      <p class="sub-english-subtext">CYBER ECUMENOPOLIS // QUANTUM DATA ARTERY</p>
      <div class="sub-interactive-hint">
        <span>🌐 مليارات الترانزستورات الكمومية ترسل نبضات ضوئية عبر المدار</span>
      </div>
    </div>

    <!-- SUB 10: PLANET PYRO-X (VOLCANIC PLASMA) -->
    <div id="sub-10" class="subtitle-glass-card">
      <div class="sub-phase-badge gold">SECTOR 04 // PYRO-X VOLCANIC</div>
      <h2 class="sub-arabic-headline">جحيم البلازما [PYRO-X].. محيطات من الحمم والطاقة الفائقة</h2>
      <p class="sub-english-subtext">SUPERHEATED PLASMA // PURE COMPUTATIONAL ENERGY</p>
      <div class="sub-interactive-hint">
        <span>🔥 صهر المعالجات وتوليد طاقة تشغيل الأنظمة المؤتمتة</span>
      </div>
    </div>

    <!-- SUB 11: SOL-PRIME & SINGULARITY -->
    <div id="sub-11" class="subtitle-glass-card">
      <div class="sub-phase-badge">SECTOR 05 // SOLAR MAGNETAR & VOID</div>
      <h2 class="sub-arabic-headline">النجم النابض وثقب الزمكان.. بوابة العبور إلى المحطة الأخيرة</h2>
      <p class="sub-english-subtext">SOLAR CORONA // GRAVITATIONAL SINGULARITY</p>
      <div class="sub-interactive-hint">
        <span>💫 انحناء الضوء حول أفق الحدث والقفز الفائق نحو موطن Z-PACT</span>
      </div>
    </div>

    <!-- SUB 12: Z-PACT HOMEWORLD CLIMAX -->
    <div id="sub-12" class="subtitle-glass-card">
      <div class="sub-phase-badge emerald">STAGE 07 // Z-PACT COMMAND</div>
      <h2 class="sub-arabic-headline">الوصول إلى الموطن.. منصة Z-PACT وعصر الأتمتة الشاملة</h2>
      <p class="sub-english-subtext">ECOSYSTEM DESTINATION // ARCHITECT: ABDO SABER</p>
      <div class="sub-interactive-hint">
        <span>👑 مرحباً بك في المقر الرسمي لمنظومة Z-PACT البرمجية</span>
      </div>
    </div>

  </div>

  <!-- QUICK STEP CONTROLS (BOTTOM LEFT) -->
  <div id="quick-controls">
    <button class="ctrl-pill" onclick="stepExperience(-1)" title="المرحلة السابقة">
      <span>◀</span>
      <span>PREV</span>
    </button>
    <button class="ctrl-pill" onclick="stepExperience(1)" title="المرحلة التالية">
      <span>NEXT</span>
      <span>▶</span>
    </button>
    <button class="ctrl-pill" onclick="warpToCosmicStage(0.55)" title="القفز السريع لرحلة الكواكب">
      <span>🪐</span>
      <span>DEEP SPACE</span>
    </button>
    <button class="ctrl-pill" onclick="warpToCosmicStage(0.92)" title="القفز السريع للمنصة النهائية">
      <span>🏛️</span>
      <span>Z-PACT</span>
    </button>
  </div>

  <!-- SCROLL PROMPT (BOTTOM CENTER) -->
  <div id="scroll-prompt">
    <div class="scroll-arrow-anim"></div>
    <span class="scroll-prompt-text">SCROLL TO TRAVEL</span>
  </div>

  <!-- =========================================================================
       INTERACTIVE COSMIC TERMINAL DRAWER (RIGHT SIDE)
       ========================================================================= -->
  <div id="cosmic-terminal">
    <div class="term-header">
      <div class="term-dots">
        <span class="term-dot red"></span>
        <span class="term-dot yellow"></span>
        <span class="term-dot green"></span>
      </div>
      <span class="term-title">⚡ COSMIC OS // v4.2.0-STABLE</span>
      <button class="term-close-btn" onclick="toggleTerminal()" title="إغلاق التيرمينال">✕</button>
    </div>

    <!-- Terminal Tabs -->
    <div class="term-tabs">
      <div class="term-tab active" onclick="switchTermTab('console')">CONSOLE</div>
      <div class="term-tab" onclick="switchTermTab('telemetry')">PLANET_RADAR</div>
      <div class="term-tab" onclick="switchTermTab('swarm')">TELEGRAM_BOTS</div>
      <div class="term-tab" onclick="switchTermTab('missions')">MISSION_LOGS</div>
      <div class="term-tab" onclick="switchTermTab('diagnostics')">DIAGNOSTICS</div>
    </div>

    <!-- Terminal Output Log Body -->
    <div class="term-body" id="terminal-logs-body">
      <div style="color:#38bdf8;">>> Initializing Z-PACT Deep Space Terminal Environment...</div>
      <div style="color:#10b981;">>> Quantum cores verified. 8 Exoplanet beacons detected on radar.</div>
      <div style="color:#94a3b8;">>> Type 'help' for full command list, or click quick buttons below.</div>
      <div style="color:#fbbf24;">----------------------------------------------------------</div>
    </div>

    <!-- Terminal Quick Execution Buttons -->
    <div class="term-quick-btns">
      <button class="term-q-btn" onclick="execTermCommand('scan')">🔍 scan</button>
      <button class="term-q-btn" onclick="execTermCommand('planets')">🪐 planets</button>
      <button class="term-q-btn" onclick="execTermCommand('warp next')">🚀 warp next</button>
      <button class="term-q-btn" onclick="execTermCommand('bots')">🤖 bots</button>
      <button class="term-q-btn" onclick="execTermCommand('deploy')">⚡ deploy</button>
      <button class="term-q-btn" onclick="execTermCommand('kpis')">📊 kpis</button>
      <button class="term-q-btn" onclick="execTermCommand('matrix')">🟢 matrix</button>
      <button class="term-q-btn" onclick="execTermCommand('clear')">🧹 clear</button>
    </div>

    <!-- Terminal Input Line -->
    <div class="term-input-row">
      <span class="term-prompt-symbol">abdosaber@zpact:~$</span>
      <input type="text" id="term-cli-input" placeholder="Type a command (help, scan, warp, bots)..." autocomplete="off" spellcheck="false" />
    </div>
  </div>

  <!-- =========================================================================
       STAGE 6: FINAL CLIMAX SHOWCASE (Z-PACT HOMEWORLD)
       ========================================================================= -->
  <section id="final-climax-stage">
    <div class="climax-container">

      <!-- Creator Hero Presentation Card -->
      <div class="creator-hero-card reveal">
        <div class="creator-avatar-wrap">
          <video class="creator-avatar-video" src="/frontend/assets/5816566040681452108.mp4" autoplay loop muted playsinline></video>
        </div>

        <div class="creator-bio-content">
          <div class="creator-badge-row">
            <span class="sub-phase-badge gold">SYSTEMS ARCHITECT</span>
            <span class="sub-phase-badge emerald">AI & TELEGRAM ENGINEER</span>
            <span class="sub-phase-badge">Z-PACT FOUNDER</span>
          </div>

          <h1 class="creator-hero-name">عبده صابر // Abdo Saber</h1>
          <div class="creator-hero-title">Automation Architect & AI Systems Specialist</div>

          <p class="creator-hero-desc">
            مهندس برمجيات ومصمم أنظمة أتمتة فائقة الأداء، متخصص في بناء البوتات الذكية الضخمة، وهندسة البنية التحتية السحابية على Railway و Docker، وتطوير منصات الذكاء الاصطناعي التي تخدم مئات الآلاف من المستخدمين بكفاءة متناهية واستجابة بالمللي ثانية.
          </p>
        </div>
      </div>

      <!-- Core Achievements & KPIs -->
      <div class="kpi-metrics-grid reveal-stagger">
        <div class="kpi-card">
          <div class="kpi-number">15M+</div>
          <div class="kpi-label">استدعاء API شهرياً</div>
          <div class="kpi-sub">MONTHLY TRANSACTIONS</div>
        </div>

        <div class="kpi-card">
          <div class="kpi-number">99.99%</div>
          <div class="kpi-label">جاهزية واستقرار السيرفرات</div>
          <div class="kpi-sub">CLOUD HIGH-AVAILABILITY</div>
        </div>

        <div class="kpi-card">
          <div class="kpi-number">250+</div>
          <div class="kpi-label">سيرفر وبوت مؤتمت بالكامل</div>
          <div class="kpi-sub">ACTIVE TELEGRAM ENGINES</div>
        </div>

        <div class="kpi-card">
          <div class="kpi-number">&lt;10ms</div>
          <div class="kpi-label">زمن استجابة فائق السرعة</div>
          <div class="kpi-sub">ULTRA-LOW LATENCY PIPELINE</div>
        </div>
      </div>

      <!-- Production Projects Showcase Grid -->
      <div class="portfolio-grid reveal-stagger">
        <div class="project-card">
          <span class="project-badge">CORE ECOSYSTEM</span>
          <h3 class="project-title">Z-PACT Enterprise Platform</h3>
          <p class="project-desc">
            المنصة المركزية المتكاملة لإدارة الخدمات الرقمية، الملفات المشفرة، وأنظمة الذكاء الاصطناعي مع واجهة مستخدم فائقة السرعة وبوابات دفع مؤتمتة بالكامل.
          </p>
          <div class="project-tech-tags">
            <span class="tech-tag">FastAPI</span>
            <span class="tech-tag">PostgreSQL</span>
            <span class="tech-tag">Redis</span>
            <span class="tech-tag">WebGL</span>
          </div>
        </div>

        <div class="project-card">
          <span class="project-badge">AUTOMATION SWARM</span>
          <h3 class="project-title">Telegram Autonomous Bot Cluster</h3>
          <p class="project-desc">
            مجموعة بوتات تيليجرام عملاقة لمعالجة الملفات والمدفوعات والمحتوى الرقمي، تدير أكثر من 100 ألف طلب يومياً بدون أي تدخل بشري.
          </p>
          <div class="project-tech-tags">
            <span class="tech-tag">Python Telethon</span>
            <span class="tech-tag">Aiogram</span>
            <span class="tech-tag">RabbitMQ</span>
            <span class="tech-tag">Docker</span>
          </div>
        </div>

        <div class="project-card">
          <span class="project-badge">CLOUD DEPLOYMENT</span>
          <h3 class="project-title">Railway High-Velocity Pipelines</h3>
          <p class="project-desc">
            هندسة نشر سحابي مرنة ومتطورة تعتمد على الحاويات الموزعة مع المراقبة اللحظية والتحجيم التلقائي وفق كثافة حركة المرور.
          </p>
          <div class="project-tech-tags">
            <span class="tech-tag">Railway CI/CD</span>
            <span class="tech-tag">Docker Swarm</span>
            <span class="tech-tag">Prometheus</span>
          </div>
        </div>
      </div>

      <!-- Final Action Buttons & Navigation CTAs -->
      <div class="climax-cta-row reveal">
        <a href="/store" class="cta-btn primary">
          <span>🚀</span>
          <span>الدخول إلى منصة Z-PACT الرئيسية</span>
        </a>
        <a href="https://t.me/n0accent" target="_blank" class="cta-btn secondary">
          <span>💬</span>
          <span>تواصل مع عبده صابر على تيليجرام (@n0accent)</span>
        </a>
        <button class="cta-btn secondary" onclick="rewindCosmicSimulation()">
          <span>🔄</span>
          <span>إعادة خوض الرحلة من البداية</span>
        </button>
      </div>

    </div>
  </section>
"""

if __name__ == "__main__":
    html = generate_html_body()
    print(f"Generated HTML Body: {len(html.splitlines())} lines")
