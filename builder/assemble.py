# builder/assemble.py
# Master Assembler: Combines all modules and writes directly to frontend/pages/creator.html & index.html
# All JS libraries are INLINED — zero CDN dependencies, works fully offline & bypasses tracking prevention.

import os
import sys

# Ensure current working directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from builder.css_gen import generate_css
from builder.html_gen import generate_html_body
from builder.audio_gen import generate_audio_js
from builder.games_gen import generate_games_js
from builder.celestial_gen import generate_celestial_js
from builder.space_events_lore_gen import generate_space_events_js
from builder.space_expedition_chronicles_gen import generate_expedition_chronicles_js
from builder.cosmic_encyclopedia_lore_gen import generate_cosmic_encyclopedia_js
from builder.planetary_defense_tactics_gen import generate_flight_protocols_js
from builder.astronomy_deep_database_gen import generate_astronomy_deep_js
from builder.microservices_code_showcase_gen import generate_microservices_code_js
from builder.retro_gaming_expanded_sprites_gen import generate_retro_gaming_expanded_js
from builder.three_gen import generate_threejs_js
from builder.terminal_gen import generate_terminal_js
from builder.terminal_expanded_gen import generate_terminal_expanded_js
from builder.loop_gen import generate_loop_js


def _read_lib(filename):
    """Read a JS library from the local libs folder."""
    lib_path = os.path.join("frontend", "assets", "libs", filename)
    if not os.path.exists(lib_path):
        print(f"  [WARN] Missing lib: {lib_path} — will use CDN fallback for this file.")
        return None
    with open(lib_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def build():
    # ── Load & inline all JS libraries ──────────────────────────────────────
    three_lib         = _read_lib("three.min.js")
    effect_composer   = _read_lib("EffectComposer.js")
    render_pass       = _read_lib("RenderPass.js")
    shader_pass       = _read_lib("ShaderPass.js")
    copy_shader       = _read_lib("CopyShader.js")
    lum_highpass      = _read_lib("LuminosityHighPassShader.js")
    unreal_bloom      = _read_lib("UnrealBloomPass.js")
    gsap_lib          = _read_lib("gsap.min.js")

    def inline_or_cdn(content, cdn_url, label):
        """Return an inline <script> block, or fall back to a CDN src tag."""
        if content:
            return f"<script>/* {label} — inlined for offline support */\n{content}\n</script>"
        else:
            return f'<script src="{cdn_url}"></script><!-- CDN FALLBACK -->'

    three_tag = inline_or_cdn(
        three_lib, "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js", "Three.js r128")
    effect_composer_tag = inline_or_cdn(
        effect_composer,
        "https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/EffectComposer.js",
        "EffectComposer")
    render_pass_tag = inline_or_cdn(
        render_pass,
        "https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/RenderPass.js",
        "RenderPass")
    shader_pass_tag = inline_or_cdn(
        shader_pass,
        "https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/ShaderPass.js",
        "ShaderPass")
    copy_shader_tag = inline_or_cdn(
        copy_shader,
        "https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/shaders/CopyShader.js",
        "CopyShader")
    lum_highpass_tag = inline_or_cdn(
        lum_highpass,
        "https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/shaders/LuminosityHighPassShader.js",
        "LuminosityHighPassShader")
    unreal_bloom_tag = inline_or_cdn(
        unreal_bloom,
        "https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/UnrealBloomPass.js",
        "UnrealBloomPass")
    gsap_tag = inline_or_cdn(
        gsap_lib, "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js", "GSAP 3.12.2")

    # ── Generate all JS modules ──────────────────────────────────────────────
    css             = generate_css()
    html_body       = generate_html_body()
    audio           = generate_audio_js()
    games           = generate_games_js()
    retro_sprites   = generate_retro_gaming_expanded_js()
    celestial       = generate_celestial_js()
    space_events    = generate_space_events_js()
    chronicles      = generate_expedition_chronicles_js()
    encyclopedia    = generate_cosmic_encyclopedia_js()
    protocols       = generate_flight_protocols_js()
    astronomy_deep  = generate_astronomy_deep_js()
    microservices   = generate_microservices_code_js()
    three           = generate_threejs_js()
    terminal        = generate_terminal_js()
    terminal_exp    = generate_terminal_expanded_js()
    loop            = generate_loop_js()

    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <meta name="description" content="عبده صابر — مهندس أتمتة الأنظمة والذكاء الاصطناعي. رحلة تفاعلية ثلاثية الأبعاد عبر الفضاء." />
  <title>عبده صابر // Abdo Saber - Automation Architect &amp; AI Systems Specialist</title>

  <!-- Modern Typography (Space Grotesk, Cairo, JetBrains Mono) -->
  <link rel="preconnect" href="https://fonts.googleapis.com" crossorigin />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&family=Space+Grotesk:wght@500;700;800&display=swap" rel="stylesheet" />

  <!-- ======================================================================
       INLINED JS LIBRARIES — Zero CDN dependencies. Works fully offline.
       Bypasses browser tracking prevention that blocks cross-origin scripts.
       ====================================================================== -->
  {three_tag}
  {effect_composer_tag}
  {render_pass_tag}
  {shader_pass_tag}
  {copy_shader_tag}
  {lum_highpass_tag}
  {unreal_bloom_tag}
  {gsap_tag}

  <!-- Promote THREE postprocessing classes to THREE namespace -->
  <script>
    if (typeof THREE !== 'undefined') {{
      // EffectComposer etc. are already attached to THREE by their UMD wrappers
      // but some older builds need explicit namespace promotion:
      if (typeof EffectComposer !== 'undefined' && !THREE.EffectComposer) THREE.EffectComposer = EffectComposer;
      if (typeof RenderPass    !== 'undefined' && !THREE.RenderPass)     THREE.RenderPass    = RenderPass;
      if (typeof ShaderPass    !== 'undefined' && !THREE.ShaderPass)     THREE.ShaderPass    = ShaderPass;
      if (typeof UnrealBloomPass !== 'undefined' && !THREE.UnrealBloomPass) THREE.UnrealBloomPass = UnrealBloomPass;
      console.log('[ENGINE] Three.js r128 + PostProcessing stack loaded inline ✓');
    }} else {{
      console.error('[ENGINE] FATAL: THREE.js failed to load.');
    }}
  </script>

  <style>
{css}
  </style>
</head>
<body>

{html_body}

  <script>
    /* =========================================================================
       GLOBAL CORE STATE & SAFE IN-MEMORY FILESYSTEM INITIALIZATION
       ========================================================================= */
    window.VIRTUAL_FS = {{}};
    const VIRTUAL_FS = window.VIRTUAL_FS;
    let targetScroll = 0.0;
    let currentScroll = 0.0;

{audio}

{games}

{retro_sprites}

{celestial}

{space_events}

{chronicles}

{encyclopedia}

{protocols}

{astronomy_deep}

{microservices}

{three}

{terminal}

{terminal_exp}

{loop}
  </script>
</body>
</html>
"""

    out_file_creator = os.path.join("frontend", "pages", "creator.html")
    with open(out_file_creator, "w", encoding="utf-8") as f:
        f.write(html)

    out_file_index = "index.html"
    with open(out_file_index, "w", encoding="utf-8") as f:
        f.write(html)

    line_count = len(html.splitlines())
    file_size_kb = len(html.encode("utf-8")) / 1024
    print(f"\n{'='*60}")
    print(f"  ASSEMBLY COMPLETE — ALL LIBS INLINED OFFLINE")
    print(f"{'='*60}")
    print(f"  Output 1 : {out_file_creator}")
    print(f"  Output 2 : {out_file_index}")
    print(f"  Lines    : {line_count:,}")
    print(f"  Size     : {file_size_kb:.1f} KB")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    build()
