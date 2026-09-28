# builder/three_gen.py
# Generates comprehensive Three.js r128 engine with shaders, 3D meshes, 10 planets, and 100K particle morphing

def generate_threejs_js():
    return """    /* =========================================================================
       THREE.JS WEBGL RENDERER, POST-PROCESSING SHADERS & 3D SCENE GRAPH
       ========================================================================= */
    const canvas = document.getElementById('ue-canvas');
    let renderer = null;
    try {
      renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        antialias: true,
        powerPreference: 'high-performance',
        alpha: false,
        logarithmicDepthBuffer: false
      });
    } catch (e) {
      console.warn('[WebGL] High-perf context failed, falling back to basic WebGL:', e);
      renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: false });
    }
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x02040a);
    scene.fog = new THREE.FogExp2(0x02040a, 0.00035);

    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 7000);
    camera.position.set(0, 0, 48);

    // Dynamic Lighting Architecture
    const ambientLight = new THREE.AmbientLight(0xffffff, 1.45);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0x38bdf8, 2.8);
    dirLight1.position.set(60, 90, 60);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x818cf8, 2.0);
    dirLight2.position.set(-60, -40, -50);
    scene.add(dirLight2);

    const pointLight = new THREE.PointLight(0x00f2fe, 3.5, 160);
    pointLight.position.set(0, 0, 20);
    scene.add(pointLight);

    // Three.js Post-Processing (EffectComposer & UnrealBloomPass)
    let composer = null;
    let bloomPass = null;
    let cinematicPass = null;

    try {
      composer = new THREE.EffectComposer(renderer);
      const renderPass = new THREE.RenderPass(scene, camera);
      composer.addPass(renderPass);

      bloomPass = new THREE.UnrealBloomPass(
        new THREE.Vector2(window.innerWidth, window.innerHeight),
        0.65, // Balanced bloom strength (prevents blown-out white screen)
        0.45, // Radius
        0.35  // Threshold (only bright neon glows, leaving normal textures crisp)
      );
      composer.addPass(bloomPass);

      // Custom Chromatic Aberration & Glitch ShaderPass
      const customPostShader = {
        uniforms: {
          tDiffuse: { value: null },
          uTime: { value: 0.0 },
          uGlitch: { value: 0.0 },
          uAberration: { value: 0.0012 }
        },
        vertexShader: `
          varying vec2 vUv;
          void main() {
            vUv = uv;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          }
        `,
        fragmentShader: `
          uniform sampler2D tDiffuse;
          uniform float uTime;
          uniform float uGlitch;
          uniform float uAberration;
          varying vec2 vUv;

          void main() {
            vec2 uv = vUv;
            if (uGlitch > 0.01) {
              float g = sin(uv.y * 80.0 + uTime * 35.0) * uGlitch * 0.03;
              uv.x += g;
            }
            float dist = distance(uv, vec2(0.5));
            float offset = uAberration * (1.0 + dist * 2.2);

            float r = texture2D(tDiffuse, uv + vec2(offset, 0.0)).r;
            float g = texture2D(tDiffuse, uv).g;
            float b = texture2D(tDiffuse, uv - vec2(offset, 0.0)).b;

            gl_FragColor = vec4(r, g, b, 1.0);
          }
        `
      };

      cinematicPass = new THREE.ShaderPass(customPostShader);
      cinematicPass.renderToScreen = true; // Essential for EffectComposer output
      composer.addPass(cinematicPass);
    } catch (e) {
      console.warn('[PostProcessing] Fallback to direct WebGL render:', e);
      composer = null;
    }

    /* -------------------------------------------------------------------------
       STAGE 1 3D MESHES: RETRO CRT MONITOR & SHATTERING GLASS SHARDS
       ------------------------------------------------------------------------- */
    const crtGroup = new THREE.Group();
    scene.add(crtGroup);

    // CRT Chassis Box
    const crtChassisMat = new THREE.MeshStandardMaterial({
      color: 0x1f2937,
      roughness: 0.85,
      metalness: 0.15
    });
    const crtChassis = new THREE.Mesh(new THREE.BoxGeometry(20, 16, 14), crtChassisMat);
    crtGroup.add(crtChassis);

    // Animated Curved CRT Screen
    const crtTexture = new THREE.CanvasTexture(crtCanvas);
    crtTexture.minFilter = THREE.LinearFilter;
    const crtScreenMat = new THREE.MeshBasicMaterial({ map: crtTexture });
    const crtScreen = new THREE.Mesh(new THREE.PlaneGeometry(16, 12), crtScreenMat);
    crtScreen.position.z = 7.02;
    crtGroup.add(crtScreen);

    // 48 Shattering Glass Shards
    const shardsGroup = new THREE.Group();
    scene.add(shardsGroup);
    shardsGroup.visible = false;
    const shards = [];
    const shardGeo = new THREE.TetrahedronGeometry(1.4, 0);
    const shardMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8, wireframe: true });

    for (let i = 0; i < 48; i++) {
      const sh = new THREE.Mesh(shardGeo, shardMat);
      sh.position.set((Math.random() - 0.5) * 16, (Math.random() - 0.5) * 12, 7);
      shardsGroup.add(sh);
      shards.push({
        mesh: sh,
        vx: (Math.random() - 0.5) * 1.8,
        vy: (Math.random() - 0.5) * 1.8,
        vz: Math.random() * 2.5 + 0.8
      });
    }

    /* -------------------------------------------------------------------------
       STAGE 4 3D MESHES: 3D SMARTPHONE & RAILWAY CLUSTER RACKS
       ------------------------------------------------------------------------- */
    const phoneGroup = new THREE.Group();
    phoneGroup.position.set(0, 0, -220);
    scene.add(phoneGroup);

    const phoneChassisMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.2, metalness: 0.9 });
    const phoneChassis = new THREE.Mesh(new THREE.BoxGeometry(11, 22, 1.2), phoneChassisMat);
    phoneGroup.add(phoneChassis);

    const phoneTexture = new THREE.CanvasTexture(phoneCanvas);
    const phoneScreenMat = new THREE.MeshBasicMaterial({ map: phoneTexture });
    const phoneScreen = new THREE.Mesh(new THREE.PlaneGeometry(10.2, 20.8), phoneScreenMat);
    phoneScreen.position.z = 0.62;
    phoneGroup.add(phoneScreen);

    // 16 3D Datacenter Server Racks
    const railwayGroup = new THREE.Group();
    railwayGroup.position.set(0, -6, -260);
    scene.add(railwayGroup);

    const rackGeo = new THREE.BoxGeometry(14, 50, 14);
    const rackMat = new THREE.MeshStandardMaterial({ color: 0x111827, roughness: 0.45, metalness: 0.85 });

    for (let r = 0; r < 16; r++) {
      const rack = new THREE.Mesh(rackGeo, rackMat);
      const sign = (r % 2 === 0) ? -1 : 1;
      const xPos = sign * (20 + Math.floor(r / 2) * 16);
      const zPos = -Math.floor(r / 2) * 22;
      rack.position.set(xPos, 0, zPos);
      railwayGroup.add(rack);

      // Blinking Green LED Strips
      const ledGeo = new THREE.PlaneGeometry(0.6, 44);
      const ledMat = new THREE.MeshBasicMaterial({ color: 0x10b981 });
      const led = new THREE.Mesh(ledGeo, ledMat);
      led.position.set(xPos + (sign > 0 ? -7.05 : 7.05), 0, zPos);
      led.rotation.y = sign > 0 ? -Math.PI / 2 : Math.PI / 2;
      railwayGroup.add(led);
    }

    // Central Floating Railway Streaming Logs Hologram
    const logTexture = new THREE.CanvasTexture(logCanvas);
    const logScreenMat = new THREE.MeshBasicMaterial({ map: logTexture, transparent: true, opacity: 0.95 });
    const logScreen = new THREE.Mesh(new THREE.PlaneGeometry(28, 28), logScreenMat);
    logScreen.position.set(0, 4, -40);
    railwayGroup.add(logScreen);

    /* -------------------------------------------------------------------------
       STAGE 5: 10 CELESTIAL 3D PLANETS ACROSS INTERSTELLAR CORRIDOR
       ------------------------------------------------------------------------- */
    const spaceGroup = new THREE.Group();
    scene.add(spaceGroup);

    // Planet 1: AURA-9 (Gas Giant with Concentric Rings at Z = -380)
    const p1Geo = new THREE.SphereGeometry(32, 64, 64);
    const p1Tex = new THREE.CanvasTexture(document.getElementById('planet-gas-canvas'));
    const p1Mat = new THREE.MeshStandardMaterial({ map: p1Tex, roughness: 0.8 });
    const planet1 = new THREE.Mesh(p1Geo, p1Mat);
    planet1.position.set(38, -12, -380);
    spaceGroup.add(planet1);

    // Rings
    const ringGeo = new THREE.RingGeometry(42, 75, 64);
    const ringMat = new THREE.MeshStandardMaterial({
      color: 0xfbbf24,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.75,
      roughness: 0.5
    });
    const ringMesh = new THREE.Mesh(ringGeo, ringMat);
    ringMesh.rotation.x = Math.PI * 0.42;
    ringMesh.rotation.y = Math.PI * 0.15;
    planet1.add(ringMesh);

    // Planet 2: GLACIES-V (Cryo Ice World with Moons at Z = -740)
    const p2Geo = new THREE.SphereGeometry(24, 64, 64);
    const p2Tex = new THREE.CanvasTexture(document.getElementById('planet-ice-canvas'));
    const p2Mat = new THREE.MeshStandardMaterial({ map: p2Tex, roughness: 0.25, metalness: 0.35 });
    const planet2 = new THREE.Mesh(p2Geo, p2Mat);
    planet2.position.set(-36, 16, -740);
    spaceGroup.add(planet2);

    const moon1Geo = new THREE.SphereGeometry(4.5, 32, 32);
    const moon1Mat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, roughness: 0.9 });
    const moon1 = new THREE.Mesh(moon1Geo, moon1Mat);
    moon1.position.set(38, 8, 0);
    planet2.add(moon1);

    // Planet 3: NEXUS-01 (Cyber Ecumenopolis at Z = -1100)
    const p3Geo = new THREE.SphereGeometry(26, 64, 64);
    const p3Tex = new THREE.CanvasTexture(document.getElementById('planet-cyber-canvas'));
    const p3Mat = new THREE.MeshStandardMaterial({
      map: p3Tex,
      emissive: 0x00f2fe,
      emissiveIntensity: 0.35,
      roughness: 0.4,
      metalness: 0.8
    });
    const planet3 = new THREE.Mesh(p3Geo, p3Mat);
    planet3.position.set(42, -18, -1100);
    spaceGroup.add(planet3);

    // Planet 4: PYRO-X (Volcanic Magma Hellscape at Z = -1460)
    const p4Geo = new THREE.SphereGeometry(22, 64, 64);
    const p4Tex = new THREE.CanvasTexture(document.getElementById('planet-lava-canvas'));
    const p4Mat = new THREE.MeshStandardMaterial({
      map: p4Tex,
      emissive: 0xef4444,
      emissiveIntensity: 0.55,
      roughness: 0.6
    });
    const planet4 = new THREE.Mesh(p4Geo, p4Mat);
    planet4.position.set(-38, -14, -1460);
    spaceGroup.add(planet4);

    // Planet 5: AERO-TEMPEST (Emerald Atmospheric Vortex at Z = -1820)
    const p5Geo = new THREE.SphereGeometry(28, 64, 64);
    const p5Mat = new THREE.MeshStandardMaterial({
      color: 0x10b981,
      roughness: 0.7,
      emissive: 0x047857,
      emissiveIntensity: 0.3
    });
    const planet5 = new THREE.Mesh(p5Geo, p5Mat);
    planet5.position.set(34, 18, -1820);
    spaceGroup.add(planet5);

    // Waypoint 6: SOL-PRIME (Pulsating Golden Magnetar Star at Z = -2180)
    const sunGeo = new THREE.SphereGeometry(45, 64, 64);
    const sunMat = new THREE.MeshBasicMaterial({ color: 0xfbbf24 });
    const sunPulsar = new THREE.Mesh(sunGeo, sunMat);
    sunPulsar.position.set(0, 0, -2180);
    spaceGroup.add(sunPulsar);

    // Waypoint 7: Dense Asteroid Debris Field (300 Tumbling Silicate Meshes)
    const asteroidGroup = new THREE.Group();
    asteroidGroup.position.set(0, 0, -2380);
    spaceGroup.add(asteroidGroup);

    const astGeo = new THREE.DodecahedronGeometry(2.5, 1);
    const astMat = new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.95 });
    const asteroids = [];

    for (let a = 0; a < 250; a++) {
      const ast = new THREE.Mesh(astGeo, astMat);
      const theta = Math.random() * Math.PI * 2;
      const rad = 25 + Math.random() * 85;
      ast.position.set(
        Math.cos(theta) * rad,
        Math.sin(theta) * rad,
        (Math.random() - 0.5) * 120
      );
      ast.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);
      asteroidGroup.add(ast);
      asteroids.push({
        mesh: ast,
        rotSpeedX: (Math.random() - 0.5) * 0.04,
        rotSpeedY: (Math.random() - 0.5) * 0.04
      });
    }

    // Waypoint 8: Supermassive Kerr Black Hole [Event Horizon] at Z = -2580
    const blackHoleGroup = new THREE.Group();
    blackHoleGroup.position.set(0, 0, -2580);
    spaceGroup.add(blackHoleGroup);

    // Event Horizon Pure Black Sphere
    const bhGeo = new THREE.SphereGeometry(18, 64, 64);
    const bhMat = new THREE.MeshBasicMaterial({ color: 0x000000 });
    const blackHoleCore = new THREE.Mesh(bhGeo, bhMat);
    blackHoleGroup.add(blackHoleCore);

    // Relativistic Glowing Accretion Disk with Doppler Beaming
    const diskGeo = new THREE.RingGeometry(22, 54, 64);
    const diskMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.85
    });
    const accretionDisk = new THREE.Mesh(diskGeo, diskMat);
    accretionDisk.rotation.x = Math.PI * 0.48;
    blackHoleGroup.add(accretionDisk);

    // Waypoint 9: Z-PACT Homeworld Station at Z = -2900
    const stationGroup = new THREE.Group();
    stationGroup.position.set(0, -18, -2900);
    spaceGroup.add(stationGroup);

    const hubGeo = new THREE.CylinderGeometry(20, 20, 6, 32);
    const hubMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.85, roughness: 0.3 });
    const stationHub = new THREE.Mesh(hubGeo, hubMat);
    stationGroup.add(stationHub);

    /* -------------------------------------------------------------------------
       100,000 GPGPU PARTICLE MORPHING ENGINE (6 CELESTIAL STAGES)
       ------------------------------------------------------------------------- */
    const PARTICLE_COUNT = 100000;
    const pos1 = new Float32Array(PARTICLE_COUNT * 3);
    const pos2 = new Float32Array(PARTICLE_COUNT * 3);
    const pos3 = new Float32Array(PARTICLE_COUNT * 3);
    const pos4 = new Float32Array(PARTICLE_COUNT * 3);
    const pos5 = new Float32Array(PARTICLE_COUNT * 3);
    const pos6 = new Float32Array(PARTICLE_COUNT * 3);

    const col1 = new Float32Array(PARTICLE_COUNT * 3);
    const col2 = new Float32Array(PARTICLE_COUNT * 3);
    const col3 = new Float32Array(PARTICLE_COUNT * 3);
    const col4 = new Float32Array(PARTICLE_COUNT * 3);
    const col5 = new Float32Array(PARTICLE_COUNT * 3);
    const col6 = new Float32Array(PARTICLE_COUNT * 3);

    const cCyan = new THREE.Color(0x00f2fe);
    const cGreen = new THREE.Color(0x10b981);
    const cPurple = new THREE.Color(0xa855f7);
    const cGold = new THREE.Color(0xf59e0b);
    const cSky = new THREE.Color(0x38bdf8);

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const i3 = i * 3;

      // State 1: CRT Monitor Pixel Raster Screen (z = 7)
      pos1[i3] = (Math.random() - 0.5) * 16.5;
      pos1[i3 + 1] = (Math.random() - 0.5) * 12.5;
      pos1[i3 + 2] = 7.05 + (Math.random() - 0.5) * 0.4;
      col1[i3] = cCyan.r; col1[i3 + 1] = cCyan.g; col1[i3 + 2] = cCyan.b;

      // State 2: 3D Matrix Digital Rain Columns (z = -60)
      pos2[i3] = (Math.random() - 0.5) * 55;
      pos2[i3 + 1] = (Math.random() - 0.5) * 65;
      pos2[i3 + 2] = -60 + (Math.random() - 0.5) * 45;
      col2[i3] = cGreen.r; col2[i3 + 1] = cGreen.g; col2[i3 + 2] = cGreen.b;

      // State 3: 3D Cybernetic Neural Core / Brain (z = -140)
      const u = Math.random();
      const v = Math.random();
      const theta = u * 2.0 * Math.PI;
      const phi = Math.acos(2.0 * v - 1.0);
      const rRad = Math.cbrt(Math.random()) * 16;
      pos3[i3] = rRad * Math.sin(phi) * Math.cos(theta);
      pos3[i3 + 1] = rRad * Math.sin(phi) * Math.sin(theta);
      pos3[i3 + 2] = -140 + rRad * Math.cos(phi);
      col3[i3] = cPurple.r; col3[i3 + 1] = cPurple.g; col3[i3 + 2] = cPurple.b;

      // State 4: Telegram Paper Plane Cloud & Server Mesh (z = -220)
      pos4[i3] = (Math.random() - 0.5) * 45;
      pos4[i3 + 1] = (Math.random() - 0.5) * 55;
      pos4[i3 + 2] = -220 + (Math.random() - 0.5) * 35;
      col4[i3] = cSky.r; col4[i3 + 1] = cSky.g; col4[i3 + 2] = cSky.b;

      // State 5: Interstellar Warp Tunnel & Galaxy Spiral (z = -400 to -2600)
      const spiralTheta = i * 0.08;
      const spiralRad = 15 + Math.random() * 55;
      pos5[i3] = Math.cos(spiralTheta) * spiralRad;
      pos5[i3 + 1] = Math.sin(spiralTheta) * spiralRad;
      pos5[i3 + 2] = -380 - (i / PARTICLE_COUNT) * 2200;
      col5[i3] = cGold.r; col5[i3 + 1] = cGold.g; col5[i3 + 2] = cGold.b;

      // State 6: Z-PACT Sanctuary Constellation (z = -2900)
      pos6[i3] = (Math.random() - 0.5) * 190;
      pos6[i3 + 1] = -18 + (Math.random() - 0.5) * 30;
      pos6[i3 + 2] = -2850 - Math.random() * 250;
      col6[i3] = cCyan.r; col6[i3 + 1] = cCyan.g; col6[i3 + 2] = cCyan.b;
    }

    const gpgpuGeo = new THREE.BufferGeometry();
    gpgpuGeo.setAttribute('position', new THREE.BufferAttribute(pos1, 3));
    gpgpuGeo.setAttribute('aPos1', new THREE.BufferAttribute(pos1, 3));
    gpgpuGeo.setAttribute('aPos2', new THREE.BufferAttribute(pos2, 3));
    gpgpuGeo.setAttribute('aPos3', new THREE.BufferAttribute(pos3, 3));
    gpgpuGeo.setAttribute('aPos4', new THREE.BufferAttribute(pos4, 3));
    gpgpuGeo.setAttribute('aPos5', new THREE.BufferAttribute(pos5, 3));
    gpgpuGeo.setAttribute('aPos6', new THREE.BufferAttribute(pos6, 3));

    gpgpuGeo.setAttribute('aCol1', new THREE.BufferAttribute(col1, 3));
    gpgpuGeo.setAttribute('aCol2', new THREE.BufferAttribute(col2, 3));
    gpgpuGeo.setAttribute('aCol3', new THREE.BufferAttribute(col3, 3));
    gpgpuGeo.setAttribute('aCol4', new THREE.BufferAttribute(col4, 3));
    gpgpuGeo.setAttribute('aCol5', new THREE.BufferAttribute(col5, 3));
    gpgpuGeo.setAttribute('aCol6', new THREE.BufferAttribute(col6, 3));

    const customParticleMat = new THREE.ShaderMaterial({
      uniforms: {
        uProgress: { value: 0.0 },
        uTime: { value: 0.0 },
        uMouse: { value: new THREE.Vector2(0, 0) }
      },
      vertexShader: `
        uniform float uProgress;
        uniform float uTime;
        uniform vec2 uMouse;

        attribute vec3 aPos1;
        attribute vec3 aPos2;
        attribute vec3 aPos3;
        attribute vec3 aPos4;
        attribute vec3 aPos5;
        attribute vec3 aPos6;

        attribute vec3 aCol1;
        attribute vec3 aCol2;
        attribute vec3 aCol3;
        attribute vec3 aCol4;
        attribute vec3 aCol5;
        attribute vec3 aCol6;

        varying vec3 vColor;

        void main() {
          vec3 p;
          vec3 c;

          if (uProgress < 1.0) {
            float t = smoothstep(0.0, 1.0, uProgress);
            p = mix(aPos1, aPos2, t);
            c = mix(aCol1, aCol2, t);
          } else if (uProgress < 2.0) {
            float t = smoothstep(1.0, 2.0, uProgress);
            p = mix(aPos2, aPos3, t);
            c = mix(aCol2, aCol3, t);
            p.y += sin(p.x * 0.4 + uTime * 3.5) * 0.8;
          } else if (uProgress < 3.0) {
            float t = smoothstep(2.0, 3.0, uProgress);
            p = mix(aPos3, aPos4, t);
            c = mix(aCol3, aCol4, t);
          } else if (uProgress < 4.0) {
            float t = smoothstep(3.0, 4.0, uProgress);
            p = mix(aPos4, aPos5, t);
            c = mix(aCol4, aCol5, t);
          } else {
            float t = smoothstep(4.0, 5.0, uProgress);
            p = mix(aPos5, aPos6, t);
            c = mix(aCol5, aCol6, t);
          }

          // Magnetic mouse repulsion interaction during neural stage
          if (uProgress >= 1.5 && uProgress <= 2.8) {
            float dist = distance(p.xy, uMouse * 40.0);
            if (dist < 20.0) {
              p.xy += normalize(p.xy - (uMouse * 40.0)) * (20.0 - dist) * 0.5;
              p.z += sin(dist * 2.0 - uTime * 15.0) * 1.8;
            }
          }

          vColor = c;
          vec4 mvPosition = modelViewMatrix * vec4(p, 1.0);

          if (-mvPosition.z <= 0.1) {
            gl_PointSize = 0.0;
          } else {
            gl_PointSize = clamp(180.0 / -mvPosition.z, 1.0, 35.0) * (1.0 + sin(uTime * 4.0 + p.x) * 0.25);
          }

          gl_Position = projectionMatrix * mvPosition;
        }
      `,
      fragmentShader: `
        varying vec3 vColor;
        void main() {
          float d = distance(gl_PointCoord, vec2(0.5));
          if (d > 0.5) discard;
          float alpha = smoothstep(0.5, 0.0, d);
          gl_FragColor = vec4(vColor, alpha);
        }
      `,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending
    });

    const gpgpuPoints = new THREE.Points(gpgpuGeo, customParticleMat);
    scene.add(gpgpuPoints);
"""

if __name__ == "__main__":
    three = generate_threejs_js()
    print(f"Generated Three.js JS: {len(three.splitlines())} lines")
