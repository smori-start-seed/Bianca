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

const WIDTH: u32 = 96u;
const HEIGHT: u32 = 54u;

fn idx(x: u32, y: u32) -> u32 {
    return y * WIDTH + x;
}

