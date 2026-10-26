// src/shaders/update.wgsl

struct SatuRingParams {
    tick_rate: f32,

    drift_strength: f32,
    drift_variance: f32,
    drift_bias_x: f32,
    drift_bias_y: f32,

    resonance_intensity: f32,
    resonance_frequency: f32,
    resonance_decay: f32,

    vortex_radius: f32,
    vortex_strength: f32,
    vortex_turbulence: f32,

    harmony_bias: f32,
    harmony_snap: f32,
    harmony_threshold: f32,

    spread_res: f32,
    spread_vortex: f32,
    spread_harmony: f32,

    emerge_res: f32,
    emerge_vortex: f32,
    emerge_harmony: f32,

    overlay_internal_opacity: f32,
    overlay_external_opacity: f32,

    internal_start: f32,
    internal_end: f32,
    external_start: f32,
    external_end: f32,
};

@group(0) @binding(0)
var<uniform> params: SatuRingParams;

@group(0) @binding(1)
var<storage, read_write> color_grid: array<vec4<f32>>;

@group(0) @binding(2)
var<storage, read_write> drift_field: array<vec2<f32>>;

@group(0) @binding(3)
var<storage, read_write> resonance_field: array<vec2<f32>>; // x=intensity, y=phase

@group(0) @binding(4)
var<storage, read_write> vortex_field: array<vec2<f32>>; // x=rotation, y=turbulence

@group(0) @binding(5)
var<storage, read_write> harmony_field: array<vec2<f32>>; // x=stability, y=snap

@group(0) @binding(6)
var<storage, read_write> overlay_mask: array<f32>; // overlayValue (intern/extern aus energy)

const WIDTH: u32 = 96u;
const HEIGHT: u32 = 54u;

fn idx(x: u32, y: u32) -> u32 {
    return y * WIDTH + x;
}

// sehr einfache Pseudo-Random-Funktion aus Koordinaten
fn hash2(p: vec2<u32>) -> f32 {
    let n = f32(p.x * 374761393u + p.y * 668265263u);
    let s = sin(n * 0.0000001);
    return fract(s * 43758.5453);
}

@compute @workgroup_size(8, 8, 1)
fn main(@builtin(global_invocation_id) gid: vec3<u32>) {
    if (gid.x >= WIDTH || gid.y >= HEIGHT) {
        return;
    }

    let i = idx(gid.x, gid.y);

    // -------------------
    // Drift-Update
    // -------------------
    var drift = drift_field[i];

    drift.x = drift.x + params.drift_strength * params.drift_bias_x;
    drift.y = drift.y + params.drift_strength * params.drift_bias_y;

    let r1 = hash2(gid.xy);
    let r2 = hash2(gid.yx + vec2<u32>(17u, 53u));

    let v = params.drift_variance;
    drift.x = drift.x + (r1 * 2.0 - 1.0) * v;
    drift.y = drift.y + (r2 * 2.0 - 1.0) * v;

    let damping_M = 0.05;
    drift = drift * (1.0 - damping_M);

    drift_field[i] = drift;

    // -------------------
    // Resonance-Update
    // -------------------
    var res = resonance_field[i];
    var intensity = res.x;
    var phase = res.y;

    phase = phase + params.resonance_frequency;
    if (phase > 1.0) {
        phase = phase - 1.0;
    }

    let pulse = sin(phase * 6.2831853);
    intensity = max(0.0, pulse * params.resonance_intensity);

    intensity = intensity * (1.0 - params.resonance_decay);

    let damping_N = 0.05;
    intensity = pow(intensity, 1.0 - damping_N);

    resonance_field[i] = vec2<f32>(intensity, phase);

    // -------------------
    // Vortex-Update
    // -------------------
    var vortex = vortex_field[i];
    var rotation = vortex.x;
    var turbulence = vortex.y;

    rotation = rotation + (drift.x - drift.y) * params.vortex_strength;
    turbulence = turbulence + intensity * params.vortex_turbulence;

    if (abs(rotation) > params.vortex_radius) {
        rotation = rotation * 0.9;
    }

    rotation = rotation * (1.0 + params.spread_vortex);
    turbulence = turbulence * (1.0 + params.emerge_vortex);

    vortex_field[i] = vec2<f32>(rotation, turbulence);

    // -------------------
    // Harmony-Update
    // -------------------
    var harmony = harmony_field[i];
    var stability = harmony.x;
    var snap = harmony.y;

    let instability = abs(rotation) + turbulence;

    if (instability > params.harmony_threshold) {
        snap = snap + params.harmony_snap;
    } else {
        snap = snap * 0.95;
    }

    stability = stability + params.harmony_bias * (1.0 - instability);

    stability = stability * (1.0 + params.spread_harmony);
    snap = snap * (1.0 + params.emerge_harmony);

    harmony_field[i] = vec2<f32>(stability, snap);

    // -------------------
    // Overlay-Update
    // -------------------
    let col = color_grid[i];
    let energy = col.w;

    var overlay_val: f32;

    if (energy >= params.internal_start && energy <= params.internal_end) {
        overlay_val = params.overlay_internal_opacity;
    } else {
        overlay_val = params.overlay_external_opacity;
    }

    overlay_mask[i] = overlay_val;
}

