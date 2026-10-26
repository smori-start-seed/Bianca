use wgpu::util::DeviceExt;

pub const WIDTH: u32 = 96;
pub const HEIGHT: u32 = 54;
pub const GRID_SIZE: usize = (WIDTH * HEIGHT) as usize;

// -----------------------------
// Parameter-Struct
// -----------------------------
#[repr(C)]
#[derive(Clone, Copy, bytemuck::Pod, bytemuck::Zeroable)]
pub struct SatuRingParams {
    pub tick_rate: f32,

    pub drift_strength: f32,
    pub drift_variance: f32,
    pub drift_bias_x: f32,
    pub drift_bias_y: f32,

    pub resonance_intensity: f32,
    pub resonance_frequency: f32,
    pub resonance_decay: f32,

    pub vortex_radius: f32,
    pub vortex_strength: f32,
    pub vortex_turbulence: f32,

    pub harmony_bias: f32,
    pub harmony_snap: f32,
    pub harmony_threshold: f32,

    pub spread_res: f32,
    pub spread_vortex: f32,
    pub spread_harmony: f32,

    pub emerge_res: f32,
    pub emerge_vortex: f32,
    pub emerge_harmony: f32,

    pub overlay_internal_opacity: f32,
    pub overlay_external_opacity: f32,

    pub internal_start: f32,
    pub internal_end: f32,
    pub external_start: f32,
    pub external_end: f32,
}

// -----------------------------
// Default-Parameter
// -----------------------------
impl Default for SatuRingParams {
    fn default() -> Self {
        Self {
            tick_rate: 30.0,

            drift_strength: 0.015,
            drift_variance: 0.008,
            drift_bias_x: 0.2,
            drift_bias_y: 0.3,

            resonance_intensity: 0.35,
            resonance_frequency: 0.18,
            resonance_decay: 0.12,

            vortex_radius: 0.08,
            vortex_strength: 0.42,
            vortex_turbulence: 0.27,

            harmony_bias: 0.30,
            harmony_snap: 0.22,
            harmony_threshold: 0.18,

            spread_res: 0.40,
            spread_vortex: 0.35,
            spread_harmony: 0.28,

            emerge_res: 0.32,
            emerge_vortex: 0.30,
            emerge_harmony: 0.24,

            overlay_internal_opacity: 0.15,
            overlay_external_opacity: 0.10,

            internal_start: 0.10,
            internal_end: 0.85,
            external_start: 0.00,
            external_end: 1.00,
        }
    }
}

// -----------------------------
// GPU-Felder (Buffer)
// -----------------------------
pub struct SatuRingSim {
    pub params: SatuRingParams,
    pub params_buffer: wgpu::Buffer,

    pub color_grid: wgpu::Buffer,
    pub drift_field: wgpu::Buffer,
    pub resonance_field: wgpu::Buffer,
    pub vortex_field: wgpu::Buffer,
    pub harmony_field: wgpu::Buffer,
    pub overlay_mask: wgpu::Buffer,
}

impl SatuRingSim {
    pub fn new(device: &wgpu::Device) -> Self {
        let params = SatuRingParams::default();

        // Parameter-Uniform
        let params_buffer = device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
            label: Some("SatuRing Params Buffer"),
            contents: bytemuck::bytes_of(&params),
            usage: wgpu::BufferUsages::UNIFORM | wgpu::BufferUsages::COPY_DST,
        });

        // Hilfsfunktion für Felder
        fn make_field(device: &wgpu::Device, label: &str, element_size: usize) -> wgpu::Buffer {
            device.create_buffer(&wgpu::BufferDescriptor {
                label: Some(label),
                size: (GRID_SIZE * element_size) as u64,
                usage: wgpu::BufferUsages::STORAGE | wgpu::BufferUsages::COPY_DST,
                mapped_at_creation: false,
            })
        }

        // Felder anlegen
        let color_grid = make_field(device, "ColorGrid", 16);     // vec4<f32>
        let drift_field = make_field(device, "DriftField", 8);    // vec2<f32>
        let resonance_field = make_field(device, "ResonanceField", 8); // vec2<f32>
        let vortex_field = make_field(device, "VortexField", 8);  // vec2<f32>
        let harmony_field = make_field(device, "HarmonyField", 8); // vec2<f32>
        let overlay_mask = make_field(device, "OverlayMask", 4);  // f32

        Self {
            params,
            params_buffer,
            color_grid,
            drift_field,
            resonance_field,
            vortex_field,
            harmony_field,
            overlay_mask,
        }
    }
}

