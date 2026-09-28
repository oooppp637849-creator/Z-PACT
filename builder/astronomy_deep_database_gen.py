# builder/astronomy_deep_database_gen.py
# Generates extensive deep-space astrophysical database, chiptune music arpeggiator, and Morse code synthesizer

def generate_astronomy_deep_js():
    records = []
    
    astro_data = [
      ("ASTRO-026", "AURA-9 Polar Hexagon", 284000000, "34.2 km/s", "4.2e-4", "Class V Jovian Gas", "1.92 mSv/hr", "الحلقات الميثانية تمتص الأشعة تحت الحمراء وتعيد إشعاعها بنمط رنيني يحاكي الإشارات المشفرة."),
      ("ASTRO-027", "AURA-9 Outer Ring Gap", 295000000, "28.8 km/s", "3.8e-4", "Water Ice & Methane Clathrate", "1.45 mSv/hr", "الفجوة الحلقية توفر مساراً آمناً للسفن الفضائية للعبور دون الاصطدام بالركام الجليدي."),
      ("ASTRO-028", "Moon Styx-I Polar Basin", 312000000, "16.4 km/s", "1.2e-5", "Silicate Basalt & Carbonaceous", "0.98 mSv/hr", "جاذبية كوكب AURA-9 تحدث تشوهات مدية في باطن هذا القمر الصغير مما يولد طاقة حرارية."),
      ("ASTRO-029", "GLACIES-V Glacial Trench 01", 580000000, "42.1 km/s", "8.5e-5", "Nitrogen Ice Frost", "0.04 mSv/hr", "الهياكل الكريستالية عند درجة الصفر المطلق تعمل كأقراص ذاكرة ضخمة لا تفقد البيانات أبداً."),
      ("ASTRO-030", "GLACIES-V Crystalline Canyon", 592000000, "40.5 km/s", "9.1e-5", "Pure Quartz-Ice Refractive", "0.06 mSv/hr", "الانكسار الضوئي عبر الكتل الجليدية يعطي ألواناً خلابة تشبه واجهات المستخدم الفاخرة."),
      ("ASTRO-031", "GLACIES Sub-Surface Ocean", 610000000, "38.0 km/s", "1.1e-4", "Saline Ammonia Eutectic", "0.01 mSv/hr", "المحيط السائل تحت الجليد محمي تماماً من الإشعاعات الكونية، بيئة مثالية للخوادم السرية."),
      ("ASTRO-032", "NEXUS-01 North Spire Array", 980000000, "55.4 km/s", "2.4e-3", "Superconducting Graphene", "1.85 mSv/hr", "الأبراج الشمالية مسؤولة عن توزيع حركة المرور الرقمية لمليارات المستخدمين في آن واحد."),
      ("ASTRO-033", "NEXUS-01 Computational Basin", 1010000000, "52.8 km/s", "3.1e-3", "Silicon-Germanium Qubits", "2.10 mSv/hr", "الحوض الاستوائي يمثل قلب المعالجة المركزية حيث يتم اتخاذ القرارات الخوارزمية الفائقة."),
      ("ASTRO-034", "PYRO-X Caldera Prime", 1350000000, "68.2 km/s", "1.8e-3", "Superheated Magmatic Silicates", "7.40 mSv/hr", "الحمم البركانية المنصهرة توفر طاقة حرارية لا تنضب لتشغيل أسراب البوتات السحابية."),
      ("ASTRO-035", "SOL-PRIME Magnetic Flux Tube", 1980000000, "124.5 km/s", "1.2e11", "Relativistic Synchrotron", "45.0 mSv/hr", "الحقل المغناطيسي الهائل للنجم النابض يعمل كمنجنيق فضائي لدفع السفن الكونية بسرعات فائقة."),
      ("ASTRO-036", "Black Hole Event Horizon", 2450000000, "210.0 km/s", "8.4e7", "Extreme Gravitational Redshift", "88.0 mSv/hr", "تمدد الزمن عند أفق الحدث يثبت أن السرعة الفائقة تجعل الصعب ممكناً."),
      ("ASTRO-037", "AURA-9 Middle Cloud Belt", 288000000, "31.5 km/s", "4.0e-4", "Ammonium Hydrosulfide", "1.65 mSv/hr", "الغيوم البرتقالية والبنية تشكل دوامات ضخمة تدور بسرعات متوازنة مع الدوران الذاتي للكوكب."),
      ("ASTRO-038", "AURA-9 Polar Hexagon Jetstream", 286000000, "33.8 km/s", "4.1e-4", "High-Velocity Methane Jet", "1.80 mSv/hr", "التيار النفاث السداسي يحافظ على سرعة ثابتة تبلغ 450 كم/ساعة عبر القرون الماضية."),
      ("ASTRO-039", "Moon Nix Orbital Position", 305000000, "18.2 km/s", "1.4e-5", "Anorthosite Crust", "0.85 mSv/hr", "القمر الصغير يعكس 65% من الضوء الساقط عليه مما يجعله منارة ملاحية طبيعية."),
      ("ASTRO-040", "Moon Kerberos Crater Rim", 318000000, "15.1 km/s", "1.1e-5", "Metallic Iron Core", "0.75 mSv/hr", "الحفرة الصدمية الكبرى تحتوي على مكامن غنية بالحديد والنيكل عالية النقاء."),
      ("ASTRO-041", "GLACIES Frozen Geyser Field", 585000000, "41.8 km/s", "8.7e-5", "Cryogenic Nitrogen Vapor", "0.05 mSv/hr", "الانفجارات الجليدية تقذف بلورات النيتروجين لمسافة 40 كم في الغلاف الجوي الرقيق."),
      ("ASTRO-042", "GLACIES South Pole Glacial Sheet", 595000000, "40.1 km/s", "9.3e-5", "Hyper-Dense Crystalline Ice", "0.03 mSv/hr", "الطبقة الجليدية الجنوبية يبلغ سمكها 14 كم وتعمل كدرع طبيعي ضد أي إشعاعات خارجية."),
      ("ASTRO-043", "GLACIES Crystalline Cave 04", 602000000, "39.4 km/s", "1.0e-4", "Optical Crystal Columns", "0.02 mSv/hr", "الكهوف الكريستالية الداخلية تحتوي على تشكيلات صاعدة وهابطة ذات نقاء بصري تام."),
      ("ASTRO-044", "NEXUS-01 South Photonic Hub", 995000000, "54.1 km/s", "2.6e-3", "Optoelectronic Transceivers", "1.90 mSv/hr", "المركز الجنوبي يربط القارة الصناعية بالشبكة المدارية عبر كابلات ألياف فائقة الكثافة."),
      ("ASTRO-045", "NEXUS-01 West Quantum Foundry", 1025000000, "51.5 km/s", "3.3e-3", "Graphene Wafer Fab", "2.25 mSv/hr", "مصانع الرقاقات تنتج يومياً ملايين المعالجات الموجهة لتشغيل أسراب الروبوتات الذكية."),
      ("ASTRO-046", "PYRO-X Magma Trench 07", 1370000000, "66.5 km/s", "1.9e-3", "Liquid Peridotite", "7.80 mSv/hr", "الخندق الصهاري يمثل أعمق نقطة حرارية على الكوكب حيث تتجاوز الحرارة 2,200 مئوية."),
      ("ASTRO-047", "PYRO-X Basalt Plateau", 1390000000, "65.1 km/s", "2.0e-3", "Solidified Columnar Basalt", "6.90 mSv/hr", "الهضبة البازلتية توفر أرضية صلبة مستقرة لإنشاء منصات الهبوط وتفريغ الشحنات المعدنية."),
      ("ASTRO-048", "AERO-TEMPEST Eye Wall", 1835000000, "82.4 km/s", "5.2e-4", "Dense Emerald Vapor", "3.10 mSv/hr", "جدار عين الإعصار يشهد أعلى سرعة رياح في المنظومة، حيث تتجاوز 3,100 كم في الساعة."),
      ("ASTRO-049", "AERO-TEMPEST Upper Stratosphere", 1810000000, "84.0 km/s", "4.8e-4", "Ionized Methane Wisps", "2.80 mSv/hr", "الطبقات العليا تتميز بلونها الزمردي البراق وتوفر بيئة مثالية لحصاد الطاقة الساكنة."),
      ("ASTRO-050", "SOL-PRIME Equatorial Corona", 2170000000, "122.0 km/s", "1.1e11", "Fully Ionized Hydrogen", "42.0 mSv/hr", "الهالة الاستوائية تشع بضوء ذهبي مبهر وتصدر تدفقات نيوترينو فائقة الاستقرار."),
      ("ASTRO-051", "SOL-PRIME North Magnetic Pole", 2190000000, "126.8 km/s", "1.4e11", "Relativistic Particle Beam", "48.5 mSv/hr", "القطب المغناطيسي يطلق شعاعاً مستمراً من الجسيمات المشحونة يعمل كمنارة ملاحة عبر المجرة."),
      ("ASTRO-052", "Asteroid Sigma Heavy Cluster", 2370000000, "22.5 km/s", "8.2e-6", "Metallic Nickel-Iron", "1.05 mSv/hr", "تجمع صخري ضخم يحتوي على كتل معدنية تزن مليارات الأطنان صالحة للإنشاءات الفضائية."),
      ("ASTRO-053", "Asteroid Sigma Carbonaceous Pocket", 2390000000, "24.1 km/s", "7.5e-6", "Organic Carbon Matrix", "0.95 mSv/hr", "الجيب الكربوني يحتوي على أحماض أمينية ومواد عضوية بدائية تثبت أصل الحياة في الكون."),
      ("ASTRO-054", "Void Horizon Relativistic Lensing Ring", 2570000000, "205.0 km/s", "7.9e7", "Gravitational Photon Ring", "82.0 mSv/hr", "حلقة الفوتونات المضيئة تمثل الحد الفاصل بين الفضاء العادي ومنطقة انحناء الزمكان التام."),
      ("ASTRO-055", "Z-PACT Orbital Command Station", 2890000000, "12.0 km/s", "1.0e-5", "Controlled Life Matrix", "0.01 mSv/hr", "المحطة المركزية الكبرى ترحب بسفينة المهندس عبده صابر معلنة اكتمال الرحلة بنجاح ساحق.")
    ]

    for refId, target, dist, vel, mag, spec, rad, notes in astro_data:
        records.append(f"""      {{
        refId: '{refId}',
        target: '{target}',
        distanceKm: {dist},
        radialVelocity: '{vel}',
        magneticFieldTesla: '{mag}',
        spectralSignature: '{spec}',
        radiationDosimetry: '{rad}',
        notesAr: '{notes}',
        notesEn: 'Scientific survey record for {target} compiled by Commander Abdo Saber.'
      }},""")

    records_js = "\n".join(records)

    header = """    /* =========================================================================
       DEEP ASTROPHYSICAL SENSOR LOGS & PROCEDURAL CHIPTUNE MUSIC ENGINE
       ========================================================================= */

    // In-Depth Astrophysical Telemetry Database
    const DEEP_SPACE_LOG_DATABASE = [
"""

    footer = """    ];

    /* -------------------------------------------------------------------------
       RETRO CHIPTUNE ARPEGGIATOR & PROCEDURAL AUDIO SYNTHESIZER
       ------------------------------------------------------------------------- */
    const CHIPTUNE_NOTES = [
      261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25,
      587.33, 659.25, 698.46, 783.99, 880.00, 987.77, 1046.50
    ];

    let chiptuneInterval = null;
    let chiptuneStep = 0;

    window.toggleRetroChiptune = function() {
      initAudioEngine();
      if (chiptuneInterval) {
        clearInterval(chiptuneInterval);
        chiptuneInterval = null;
        console.log('[Chiptune] Synthesizer paused.');
      } else {
        chiptuneStep = 0;
        chiptuneInterval = setInterval(() => {
          if (!audioCtx || isAudioMuted) return;
          const noteFreq = CHIPTUNE_NOTES[chiptuneStep % CHIPTUNE_NOTES.length];
          playCinematicFX(noteFreq, 'square', 0.12, 0.08);
          chiptuneStep = (chiptuneStep + 1) % 32;
        }, 140);
        console.log('[Chiptune] Synthesizer started.');
      }
    };

    // Procedural Morse Code Audio Encoder
    const MORSE_MAP = {
      'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
      'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
      'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
      'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
      'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---'
    };

    window.playMorseBeacon = function(text = 'ZPACT') {
      initAudioEngine();
      if (!audioCtx || isAudioMuted) return;
      const clean = text.toUpperCase();
      let delay = 0;

      for (let ch of clean) {
        const code = MORSE_MAP[ch];
        if (code) {
          for (let symbol of code) {
            const isDash = symbol === '-';
            const dur = isDash ? 0.18 : 0.06;
            setTimeout(() => {
              playCinematicFX(750, 'sine', dur, 0.15);
            }, delay * 1000);
            delay += dur + 0.06;
          }
          delay += 0.18;
        }
      }
    };
"""
    return header + records_js + "\n" + footer

if __name__ == "__main__":
    deep_astro = generate_astronomy_deep_js()
    print(f"Generated Deep Astronomy JS: {len(deep_astro.splitlines())} lines")
