#include "common_params.wgsl"

@group(0) @binding(0)
var<uniform> params: SatuRingParams;

@group(0) @binding(1)
var<storage, read> resonance_field: array<vec2<f32>>; // x=intensity, y=phase

@fragment
fn fs_main(@builtin(position) pos: vec4<f32>) -> @location(0) vec4<f32> {
    let x = clamp(u32(pos.x), 0u, WIDTH - 1u);
    let y = clamp(u32(pos.y), 0u, HEIGHT - 1u);
    let i = idx(x, y);

    let intensity = resonance_field[i].x;
    let c = vec3<f32>(1.0, 0.7, 0.4);
    return vec4<f32>(c * intensity, intensity * 0.4);
}

