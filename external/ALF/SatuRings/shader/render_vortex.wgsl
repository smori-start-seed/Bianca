#include "common_params.wgsl"

@group(0) @binding(0)
var<uniform> params: SatuRingParams;

@group(0) @binding(1)
var<storage, read> vortex_field: array<vec2<f32>>; // x=rotation, y=turbulence

@fragment
fn fs_main(@builtin(position) pos: vec4<f32>) -> @location(0) vec4<f32> {
    let x = clamp(u32(pos.x), 0u, WIDTH - 1u);
    let y = clamp(u32(pos.y), 0u, HEIGHT - 1u);
    let i = idx(x, y);

    let rot = vortex_field[i].x;
    let turb = vortex_field[i].y;

    let mag = clamp(abs(rot) * 4.0 + turb * 2.0, 0.0, 1.0);
    let c = vec3<f32>(0.47, 0.7, 1.0);

    return vec4<f32>(c * mag, 0.25 + turb * 0.3);
}

