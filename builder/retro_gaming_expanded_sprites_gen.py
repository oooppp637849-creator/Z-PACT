# builder/retro_gaming_expanded_sprites_gen.py
# Generates comprehensive pixel-art sprite matrices, zero-GC particle pool, and interactive game controls

def generate_retro_gaming_expanded_js():
    return """    /* =========================================================================
       RETRO SPRITE MATRICES, ZERO-GC PARTICLE POOL & INTERACTIVE CONTROLS
       ========================================================================= */

    // High-Performance Zero-GC Particle Pool (150 Slots)
    class CanvasParticlePool {
      constructor(maxParticles = 150) {
        this.maxParticles = maxParticles;
        this.particles = new Array(maxParticles);
        for (let i = 0; i < maxParticles; i++) {
          this.particles[i] = {
            active: false,
            x: 0, y: 0,
            vx: 0, vy: 0,
            life: 0, maxLife: 1,
            size: 2,
            color: '#ffffff',
            alpha: 1.0,
            type: 'spark'
          };
        }
      }

      spawn(x, y, vx, vy, size, color, maxLife, type = 'spark') {
        for (let i = 0; i < this.maxParticles; i++) {
          const p = this.particles[i];
          if (!p.active) {
            p.active = true;
            p.x = x;
            p.y = y;
            p.vx = vx;
            p.vy = vy;
            p.size = size;
            p.color = color;
            p.life = 0;
            p.maxLife = maxLife;
            p.alpha = 1.0;
            p.type = type;
            return;
          }
        }
      }

      updateAndDraw(ctx) {
        for (let i = 0; i < this.maxParticles; i++) {
          const p = this.particles[i];
          if (p.active) {
            p.x += p.vx;
            p.y += p.vy;
            p.life += 0.03;
            p.alpha = Math.max(0, 1.0 - (p.life / p.maxLife));

            if (p.life >= p.maxLife) {
              p.active = false;
              continue;
            }

            ctx.save();
            ctx.globalAlpha = p.alpha;
            ctx.fillStyle = p.color;

            if (p.type === 'spark') {
              ctx.beginPath();
              ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
              ctx.fill();
            } else if (p.type === 'slash') {
              ctx.fillRect(p.x, p.y, p.size * 3, p.size);
            } else if (p.type === 'smoke') {
              ctx.beginPath();
              ctx.arc(p.x, p.y, p.size * (1 + p.life), 0, Math.PI * 2);
              ctx.fill();
            }
            ctx.restore();
          }
        }
      }
    }

    const crtParticlePool = new CanvasParticlePool(150);

    // Interactive Click on CRT Screen
    crtCanvas.addEventListener('click', (e) => {
      initAudioEngine();
      const rect = crtCanvas.getBoundingClientRect();
      const clickX = ((e.clientX - rect.left) / rect.width) * crtCanvas.width;
      const clickY = ((e.clientY - rect.top) / rect.height) * crtCanvas.height;

      if (crtChannel === 0) {
        // Spawn pea & sound
        pvzPeas.push({ x: 140, y: clickY, vx: 6.5 });
        playRetroLaser();
        for (let i = 0; i < 8; i++) {
          crtParticlePool.spawn(
            clickX, clickY,
            (Math.random() - 0.5) * 4, (Math.random() - 0.5) * 4,
            3, '#86efac', 0.4, 'spark'
          );
        }
      } else if (crtChannel === 1) {
        // TMNT Katana strike
        playRetroJump();
        for (let i = 0; i < 14; i++) {
          crtParticlePool.spawn(
            clickX, clickY,
            (Math.random() - 0.5) * 8, (Math.random() - 0.5) * 8,
            4, '#38bdf8', 0.5, 'slash'
          );
        }
      } else if (crtChannel === 2) {
        // WolfTeam Gunfire
        playRetroExplosion();
        for (let i = 0; i < 18; i++) {
          crtParticlePool.spawn(
            clickX, clickY,
            (Math.random() - 0.5) * 6, (Math.random() - 0.5) * 6,
            5, '#fbbf24', 0.6, 'smoke'
          );
        }
      }
    });

    // Integrated Particle Rendering into CRT Main Loop
    const originalRenderCRT = renderCRTGameplay;
    renderCRTGameplay = function(time) {
      originalRenderCRT(time);
      crtParticlePool.updateAndDraw(crtCtx);
    };

    // 16-Bit Pixel Art Data Tables & Retro Palette Mapping
    const RETRO_PIXEL_PALETTE = {
      PEASHOOTER_GREEN_DARK: '#15803d',
      PEASHOOTER_GREEN_LIGHT: '#4ade80',
      PEASHOOTER_MOUTH: '#14532d',
      SUNFLOWER_YELLOW: '#facc15',
      SUNFLOWER_BROWN: '#713f12',
      ZOMBIE_SKIN: '#4ade80',
      ZOMBIE_COAT: '#78350f',
      ZOMBIE_PANTS: '#1e3a8a',
      ZOMBIE_CONE: '#f97316',
      ZOMBIE_BUCKET: '#94a3b8',
      TMNT_LEO_SKIN: '#22c55e',
      TMNT_LEO_BANDANA: '#3b82f6',
      TMNT_LEO_SHELL: '#92400e',
      TMNT_KATANA_STEEL: '#e2e8f0',
      TMNT_FOOT_PURPLE: '#7e22ce',
      WOLF_FUR_CHARCOAL: '#1e293b',
      WOLF_FUR_CRIMSON: '#ef4444',
      WOLF_CLAWS_IVORY: '#f8fafc'
    };

    // Detailed Sprite Matrix for PvZ Peashooter Head
    const SPRITE_PEASHOOTER_16x16 = [
      [0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0],
      [0,0,0,1,1,1,2,2,2,1,1,1,0,0,0,0],
      [0,0,1,1,2,2,2,2,2,2,2,1,1,0,0,0],
      [0,1,1,2,2,3,3,2,2,3,3,2,1,1,0,0],
      [0,1,2,2,3,4,4,3,3,4,4,3,2,1,1,1],
      [1,1,2,2,3,4,4,3,3,4,4,3,2,1,5,5],
      [1,2,2,2,2,3,3,2,2,3,3,2,2,1,5,5],
      [1,2,2,2,2,2,2,2,2,2,2,2,2,1,5,5],
      [1,2,2,2,2,2,2,2,2,2,2,2,2,1,5,5],
      [1,1,2,2,2,2,2,2,2,2,2,2,1,1,1,1],
      [0,1,1,2,2,2,2,2,2,2,2,1,1,0,0,0],
      [0,0,1,1,1,2,2,2,2,1,1,1,0,0,0,0],
      [0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0],
      [0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0],
      [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0]
    ];

    // Detailed Sprite Matrix for Leonardo Turtle Face
    const SPRITE_LEONARDO_16x16 = [
      [0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0],
      [0,0,1,1,1,2,2,2,2,1,1,1,0,0,0,0],
      [0,1,1,2,2,2,2,2,2,2,2,1,1,0,0,0],
      [1,1,2,2,2,2,2,2,2,2,2,2,1,1,0,0],
      [1,2,2,2,2,2,2,2,2,2,2,2,2,1,0,0],
      [1,1,6,6,6,6,6,6,6,6,6,6,1,1,6,6],
      [1,6,6,7,7,6,6,6,6,7,7,6,6,1,6,6],
      [1,6,7,8,8,7,6,6,7,8,8,7,6,1,0,0],
      [1,6,6,7,7,6,6,6,6,7,7,6,6,1,0,0],
      [1,1,6,6,6,6,6,6,6,6,6,6,1,1,0,0],
      [0,1,2,2,2,2,2,2,2,2,2,2,1,0,0,0],
      [0,1,2,2,2,1,1,1,1,2,2,2,1,0,0,0],
      [0,0,1,2,2,2,2,2,2,2,2,1,0,0,0,0],
      [0,0,1,1,2,2,2,2,2,2,1,1,0,0,0,0],
      [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0],
      [0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0]
    ];

    // Detailed Sprite Matrix for Zombie Walk Frame 1
    const SPRITE_ZOMBIE_WALK_16x16 = [
      [0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
      [0,0,0,1,2,2,2,2,2,1,0,0,0,0,0,0],
      [0,0,1,2,3,3,2,3,3,2,1,0,0,0,0,0],
      [0,0,1,2,3,4,2,3,4,2,1,0,0,0,0,0],
      [0,0,1,2,2,2,2,2,2,2,1,0,0,0,0,0],
      [0,0,0,1,2,1,1,1,2,1,0,0,0,0,0,0],
      [0,0,0,1,1,5,5,1,1,0,0,0,0,0,0,0],
      [0,0,1,5,5,5,5,5,5,1,0,0,0,0,0,0],
      [0,1,5,5,5,5,5,5,5,5,1,1,1,1,0,0],
      [1,5,5,5,5,5,5,5,5,5,1,2,2,2,1,0],
      [1,5,5,5,5,5,5,5,5,5,1,2,2,2,1,0],
      [0,1,1,6,6,6,6,6,6,1,1,0,0,0,0,0],
      [0,0,1,6,6,1,1,6,6,1,0,0,0,0,0,0],
      [0,0,1,6,6,1,1,6,6,1,0,0,0,0,0,0],
      [0,0,1,7,7,1,1,7,7,1,0,0,0,0,0,0],
      [0,1,7,7,7,1,1,7,7,7,1,0,0,0,0,0]
    ];

    // Detailed Sprite Matrix for Werewolf Claw Slash
    const SPRITE_WEREWOLF_CLAW_16x16 = [
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,3],
      [0,0,0,0,0,0,0,0,0,0,0,0,1,2,3,0],
      [0,0,0,0,0,0,0,0,0,0,0,1,2,3,0,0],
      [0,0,0,0,0,0,0,0,0,0,1,2,3,0,0,0],
      [0,0,0,0,0,0,0,0,0,1,2,3,0,0,0,0],
      [0,0,0,0,0,0,0,0,1,2,3,0,0,0,0,0],
      [0,0,0,0,0,0,0,1,2,3,0,0,0,0,0,0],
      [0,0,0,0,0,0,1,2,3,0,0,0,0,0,0,0],
      [0,0,0,0,0,1,2,3,0,0,0,0,0,0,0,0],
      [0,0,0,0,1,2,3,0,0,0,0,0,0,0,0,0],
      [0,0,0,1,2,3,0,0,0,0,0,0,0,0,0,0],
      [0,0,1,2,3,0,0,0,0,0,0,0,0,0,0,0],
      [0,1,2,3,0,0,0,0,0,0,0,0,0,0,0,0],
      [1,2,3,0,0,0,0,0,0,0,0,0,0,0,0,0]
    ];

    // Detailed Sprite Matrix for Telegram Paper Plane
    const SPRITE_TELEGRAM_PLANE_16x16 = [
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1],
      [0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0],
      [0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0],
      [0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0],
      [0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0],
      [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0],
      [0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0],
      [1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0],
      [1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0],
      [1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0],
      [1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
      [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    ];
"""

if __name__ == "__main__":
    expanded_sprites = generate_retro_gaming_expanded_js()
    print(f"Generated Expanded Sprites JS: {len(expanded_sprites.splitlines())} lines")
