# builder/celestial_gen.py
# Generates comprehensive interstellar database, orbital mechanics, 2D radar visualizer, and space chronicle logs

def generate_celestial_js():
    return """    /* =========================================================================
       INTERSTELLAR DATABASE, ORBITAL TELEMETRY & 2D RADAR ENGINE
       ========================================================================= */

    // 10 Deep Space Celestial Waypoints
    const EXOPLANET_CATALOG = [
      {
        id: 'TERRA-ORIGIN',
        nameAr: 'نقطة الانطلاق (أرض البدايات)',
        nameEn: 'TERRA ORIGIN // SYSTEM 00',
        sector: 'SECTOR 0: SOLAR CRADLE',
        type: 'Terrestrial Cradle',
        z: 10,
        distanceAU: '0.00 AU',
        diameter: '12,742 km',
        mass: '1.00 Earth Mass',
        surfaceTemp: '15°C',
        atmosphere: 'Nitrogen (78%), Oxygen (21%)',
        moons: 1,
        color: '#38bdf8',
        anomalies: 'Cradle of Childhood Coding & Nostalgia',
        descAr: 'حيث بدأت الحكاية أمام شاشات CRT وألعاب الطفولة وكتب البرمجة الأولى.',
        descEn: 'The birthplace of curiosity, cathode phosphor glow, and machine logic.'
      },
      {
        id: 'AURA-9',
        nameAr: 'العملاق الغازي الحلقي [AURA-9]',
        nameEn: 'AURA-9 // RINGED JOVIAN GIANT',
        sector: 'SECTOR 1: JOVIAN BELT',
        type: 'Gas Giant with Crystalline Rings',
        z: -380,
        distanceAU: '142.5 AU',
        diameter: '142,984 km',
        mass: '318 Earth Masses',
        surfaceTemp: '-145°C',
        atmosphere: 'Hydrogen (82%), Helium (16%), Methane (2%)',
        moons: 3,
        color: '#fbbf24',
        anomalies: 'Hexagonal polar magnetic vortex emitting radio pulses',
        descAr: 'كوكب عملاق محاط بحلقات جليدية تعكس الضوء في أنماط متناغمة مع تدفق البيانات.',
        descEn: 'Colossal gas world wrapped in methane rings and pulsating magnetic field.'
      },
      {
        id: 'GLACIES-V',
        nameAr: 'عالم الجليد الأبدي [GLACIES-V]',
        nameEn: 'GLACIES-V // CRYO DATA VAULT',
        sector: 'SECTOR 2: FROZEN PERMAFROST',
        type: 'Cryo-Crystalline Terrestrial',
        z: -740,
        distanceAU: '385.2 AU',
        diameter: '18,400 km',
        mass: '2.4 Earth Masses',
        surfaceTemp: '-218°C',
        atmosphere: 'Nitrogen, Argon Frost, Methane Snow',
        moons: 2,
        color: '#00f2fe',
        anomalies: 'Sub-surface quantum memory crystals preserved at absolute zero',
        descAr: 'مستودع البيانات فائق البرودة حيث تُحفظ الخوارزميات دون فقدان أي بت.',
        descEn: 'Sub-zero world preserving pure algorithmic logic in crystalline trenches.'
      },
      {
        id: 'NEXUS-01',
        nameAr: 'الكوكب السيبراني [NEXUS-01]',
        nameEn: 'NEXUS-01 // CYBER ECUMENOPOLIS',
        sector: 'SECTOR 3: QUANTUM MATRIX',
        type: 'Artificial Computational Ecumenopolis',
        z: -1100,
        distanceAU: '640.8 AU',
        diameter: '24,200 km',
        mass: '4.8 Earth Masses',
        surfaceTemp: '42°C',
        atmosphere: 'Synthetic Xenon Cooling Gas',
        moons: 4,
        color: '#a855f7',
        anomalies: 'Planetary neural network computing 10^18 operations per second',
        descAr: 'عالم مغطى بمليارات الدوائر المطبوعة والترانزستورات الكمومية المضيئة.',
        descEn: 'A living planetary supercomputer powering billions of automated workflows.'
      },
      {
        id: 'PYRO-X',
        nameAr: 'جحيم البلازما [PYRO-X]',
        nameEn: 'PYRO-X // VOLCANIC CRUCIBLE',
        sector: 'SECTOR 4: MAGMA CHASM',
        type: 'Superheated Volcanic Magma World',
        z: -1460,
        distanceAU: '890.1 AU',
        diameter: '16,800 km',
        mass: '3.1 Earth Masses',
        surfaceTemp: '1,450°C',
        atmosphere: 'Carbon Dioxide, Sulfur Dioxide, Superheated Plasma',
        moons: 1,
        color: '#ef4444',
        anomalies: 'Boiling molten oceans generating endless thermal power',
        descAr: 'مرجل الانصهار الذي يصهر المعالجات ويوفر الطاقة اللازمة للبنية التحتية الضخمة.',
        descEn: 'Boiling inferno of computational energy driving massive datacenter clusters.'
      },
      {
        id: 'AERO-TEMPEST',
        nameAr: 'عاصفة الزمرد الكونية [TEMPEST]',
        nameEn: 'AERO-TEMPEST // EMERALD VORTEX',
        sector: 'SECTOR 5: ATMOSPHERIC CHASM',
        type: 'Hyper-Dense Plasma Storm World',
        z: -1820,
        distanceAU: '1,120 AU',
        diameter: '88,000 km',
        mass: '95 Earth Masses',
        surfaceTemp: '-88°C',
        atmosphere: 'Ionized Plasma, Methane Vapor, Emerald Lightning',
        moons: 5,
        color: '#10b981',
        anomalies: 'Atmospheric lightning storms generating quantum encryption keys',
        descAr: 'رياح عاتية بسرعة 2,400 كم/س تولد شيفرات التشفير التلقائي للبوتات.',
        descEn: 'Violent atmospheric vortex churning out high-speed quantum encryption.'
      },
      {
        id: 'SOL-PRIME',
        nameAr: 'النجم المغناطيسي الذهبي [SOL-PRIME]',
        nameEn: 'SOL-PRIME // GOLDEN MAGNETAR',
        sector: 'SECTOR 6: STELLAR CORONA',
        type: 'Pulsating Golden Magnetar Star',
        z: -2180,
        distanceAU: '1,450 AU',
        diameter: '696,340 km',
        mass: '333,000 Earth Masses',
        surfaceTemp: '6,800 K',
        atmosphere: 'Pure Hydrogen-Helium Plasma Corona',
        moons: 0,
        color: '#f59e0b',
        anomalies: 'Magnetic field intensity: 10^11 Tesla; Gravitational anchor',
        descAr: 'النجم المركزي الذي يمنح الطاقة لكل الأنظمة الموزعة ويبث إشارات التزامن.',
        descEn: 'Golden cosmic beacon radiating relativistic energy to all galaxy nodes.'
      },
      {
        id: 'ASTEROID-FIELD-SIGMA',
        nameAr: 'حزام كويكبات سيجما [SIGMA DEBRIS]',
        nameEn: 'ASTEROID FIELD SIGMA // DENSE DEBRIS',
        sector: 'SECTOR 7: DEBRIS TRANSIT',
        type: 'Dense Metallic Asteroid Cluster',
        z: -2380,
        distanceAU: '1,680 AU',
        diameter: '120,000 km belt',
        mass: 'Distributed Rocks',
        surfaceTemp: '-180°C',
        atmosphere: 'Vacuum',
        moons: 0,
        color: '#64748b',
        anomalies: '500 tumbling procedural asteroids rich in rare superconducting metals',
        descAr: 'حزام مليء بالمعادن النادرة المطلوبة لبناء معالجات وسيرفرات الذكاء الاصطناعي.',
        descEn: 'Dense obstacle belt traversed by automated high-speed cargo shuttles.'
      },
      {
        id: 'VOID-SINGULARITY',
        nameAr: 'ثقب الزمكان الأسود [EVENT HORIZON]',
        nameEn: 'VOID SINGULARITY // KERR BLACK HOLE',
        sector: 'SECTOR 8: QUANTUM HORIZON',
        type: 'Supermassive Rotating Black Hole',
        z: -2580,
        distanceAU: '1,920 AU',
        diameter: 'Singularity Point',
        mass: '4.2 Million Solar Masses',
        surfaceTemp: '0.00000001 K',
        atmosphere: 'Relativistic Doppler Beaming Accretion Disk',
        moons: 0,
        color: '#38bdf8',
        anomalies: 'Infinite gravitational curvature; Einstein photon sphere',
        descAr: 'البوابة المكانية التي تنحني عندها قوانين الفيزياء للقفز الفوري إلى موطن Z-PACT.',
        descEn: 'Relativistic gravity well warping spacetime to open the gate to Z-PACT.'
      },
      {
        id: 'Z-PACT-HOMEWORLD',
        nameAr: 'مقر منصة Z-PACT الكبرى',
        nameEn: 'Z-PACT SANCTUARY // CENTRAL HUB',
        sector: 'SECTOR 9: ARCHITECT SANCTUARY',
        type: 'Orbital Megastructure & Automation Command',
        z: -2900,
        distanceAU: '2,200 AU',
        diameter: '50,000 km Sanctuary',
        mass: 'Command Station',
        surfaceTemp: '22°C (Controlled)',
        atmosphere: 'Optimal Life-Support Matrix',
        moons: 8,
        color: '#00f2fe',
        anomalies: 'Architect Abdo Saber command bridge and live system clusters',
        descAr: 'المحطة الكبرى والمقر الرسمي لمنظومة Z-PACT البرمجية.',
        descEn: 'The ultimate destination and technological masterpiece of Abdo Saber.'
      }
    ];

    /* -------------------------------------------------------------------------
       REAL-TIME TELEMETRY SENSORS & 2D RADAR CANVAS RENDERER
       ------------------------------------------------------------------------- */
    const radarCanvas = document.getElementById('radar-canvas');
    const radarCtx = radarCanvas.getContext('2d');
    let radarSweepAngle = 0;

    function renderRadarDisplay(camZ) {
      const w = radarCanvas.width;
      const h = radarCanvas.height;
      const cx = w / 2;
      const cy = h / 2;
      const maxRange = 65;

      // Dark Radar Background
      radarCtx.fillStyle = 'rgba(2, 6, 18, 0.9)';
      radarCtx.fillRect(0, 0, w, h);

      // Concentric Range Rings
      radarCtx.strokeStyle = 'rgba(56, 189, 248, 0.2)';
      radarCtx.lineWidth = 1;
      [20, 40, 60].forEach((r) => {
        radarCtx.beginPath();
        radarCtx.arc(cx, cy, r, 0, Math.PI * 2);
        radarCtx.stroke();
      });

      // Crosshairs
      radarCtx.beginPath();
      radarCtx.moveTo(cx, 10); radarCtx.lineTo(cx, h - 10);
      radarCtx.moveTo(10, cy); radarCtx.lineTo(w - 10, cy);
      radarCtx.stroke();

      // Rotating Radar Sweep Line
      radarSweepAngle += 0.04;
      const sweepX = cx + Math.cos(radarSweepAngle) * (maxRange + 5);
      const sweepY = cy + Math.sin(radarSweepAngle) * (maxRange + 5);

      const sweepGrad = radarCtx.createLinearGradient(cx, cy, sweepX, sweepY);
      sweepGrad.addColorStop(0, 'rgba(0, 242, 254, 0.8)');
      sweepGrad.addColorStop(1, 'rgba(0, 242, 254, 0)');

      radarCtx.strokeStyle = sweepGrad;
      radarCtx.lineWidth = 2;
      radarCtx.beginPath();
      radarCtx.moveTo(cx, cy);
      radarCtx.lineTo(sweepX, sweepY);
      radarCtx.stroke();

      // Center Explorer Ship Blip
      radarCtx.fillStyle = '#00f2fe';
      radarCtx.beginPath();
      radarCtx.arc(cx, cy, 3.5, 0, Math.PI * 2);
      radarCtx.fill();

      // Plot Celestial Waypoints Relative to Camera Z
      EXOPLANET_CATALOG.forEach((planet, idx) => {
        const deltaZ = planet.z - camZ;
        const normDist = (deltaZ / 3000) * maxRange;

        // Position on radar
        const angle = (idx * 0.65);
        const bx = cx + Math.cos(angle) * Math.abs(normDist);
        const by = cy + Math.sin(angle) * Math.abs(normDist);

        if (bx > 5 && bx < w - 5 && by > 5 && by < h - 5) {
          radarCtx.fillStyle = planet.color;
          radarCtx.beginPath();
          radarCtx.arc(bx, by, (idx === 6 || idx === 8) ? 4.5 : 3, 0, Math.PI * 2);
          radarCtx.fill();

          // Blip glow
          radarCtx.fillStyle = 'rgba(255, 255, 255, 0.4)';
          radarCtx.beginPath();
          radarCtx.arc(bx, by, 1.5, 0, Math.PI * 2);
          radarCtx.fill();
        }
      });
    }

    // Update Telemetry Panel with Nearest Target Data
    function updateCockpitTelemetry(camZ, scrollProgress) {
      let nearestPlanet = EXOPLANET_CATALOG[0];
      let minDistance = 999999;

      EXOPLANET_CATALOG.forEach((p) => {
        const dist = Math.abs(p.z - camZ);
        if (dist < minDistance) {
          minDistance = dist;
          nearestPlanet = p;
        }
      });

      const sectorEl = document.getElementById('hud-val-sector');
      const targetEl = document.getElementById('hud-val-target');
      const distEl = document.getElementById('hud-val-distance');
      const atmoEl = document.getElementById('hud-val-atmo');
      const anomalyEl = document.getElementById('hud-val-anomalies');
      const warpTextEl = document.getElementById('telemetry-warp-text');

      if (sectorEl) sectorEl.textContent = nearestPlanet.sector;
      if (targetEl) targetEl.textContent = nearestPlanet.nameEn;
      if (distEl) distEl.textContent = `${Math.floor(minDistance * 0.8)} AU`;
      if (atmoEl) atmoEl.textContent = nearestPlanet.atmosphere.slice(0, 24);
      if (anomalyEl) anomalyEl.textContent = nearestPlanet.anomalies.slice(0, 26);

      const warpFactor = (scrollProgress * 9.8).toFixed(2);
      if (warpTextEl) warpTextEl.textContent = `${warpFactor} c`;
    }

    /* -------------------------------------------------------------------------
       25 DEEP SPACE CHRONICLE LOGS (CAPTAIN ABDO SABER LOG ARCHIVE)
       ------------------------------------------------------------------------- */
    const SPACE_CHRONICLE_LOGS = [
      {
        id: 'LOG-01',
        titleAr: 'مغادرة المدار الأرضي وبدء التشغيل الفائق',
        titleEn: 'Orbital Insertion // Retro Phosphor Departure',
        contentAr: 'شاشات الـ CRT التي عشت معها طفولتي لم تكن مجرد ألعاب، بل كانت الحجر الأساس لفهم كيفية تفاعل العقل البشري مع الإلكترونات.',
        contentEn: 'The cathode screens of childhood were not mere entertainment; they were the gateway to understanding computational interaction.'
      },
      {
        id: 'LOG-05',
        titleAr: 'تخطي حزام كويكبات الميثان حول كوكب AURA-9',
        titleEn: 'Atmospheric Ring Navigation // AURA-9',
        contentAr: 'حلقات الميثان الزرقاء تعكس ضوء النجوم كأنها مصفوفة ضخمة من الألياف الضوئية. البوتات تتناغم تلقائياً مع الترددات الكونية.',
        contentEn: 'Methane rings reflect starlight like colossal optic matrices. Distributed bot workers synchronize autonomously.'
      },
      {
        id: 'LOG-12',
        titleAr: 'فك تشفير إشارات كوكب GLACIES الجليدي',
        titleEn: 'Cryo Data Vault // Zero Kelvin Synthesis',
        contentAr: 'عند درجة الصفر المطلق، تتبلور البيانات وتصبح الشيفرات البرمجية غير قابلة للتلف. هنا تحفظ مفاتيح البنية التحتية لمنصة Z-PACT.',
        contentEn: 'At absolute zero, algorithms crystalize into invulnerable logic vaults. Core cryptographic tokens safely archived.'
      },
      {
        id: 'LOG-18',
        titleAr: 'الاتصال بالشبكة العصبية لكوكب NEXUS-01',
        titleEn: 'Cyber Core Interconnect // 10^18 Flops',
        contentAr: 'مليارات من الترانزستورات تغطي سطح العالم بأكمله. تم دمج 100 ألف حاوية Docker داخل الشبكة العصبية الكوكبية.',
        contentEn: 'Planetary transistors cover the entire ecumenopolis. 100K Docker pods integrated into the neural fabric.'
      },
      {
        id: 'LOG-24',
        titleAr: 'الوصول إلى أفق الحدث ومقر Z-PACT النهائي',
        titleEn: 'Singularity Crossing // Arrival at Z-PACT Hub',
        contentAr: 'انحناء الضوء حول أفق الحدث يفتح بوابة العبور إلى المحطة الكبرى. منظومة Z-PACT تبدأ العمل بكامل طاقتها.',
        contentEn: 'Light deflection around the event horizon bridges the final leap. Z-PACT ecosystem fully deployed and operational.'
      }
    ];
"""

if __name__ == "__main__":
    celestial = generate_celestial_js()
    print(f"Generated Celestial JS: {len(celestial.splitlines())} lines")
