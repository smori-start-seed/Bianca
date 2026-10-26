#include "common_params.wgsl"

@group(0) @binding(0)
var<uniform> params: SatuRingParams;

@group(0) @binding(1)
var<storage, read> harmony_field: array<vec2<f32>>; // x=stability, y=snap

@fragment
fn fs_main(@builtin(position) pos: vec4<f32>) -> @location(0) vec4<f32> {
    let x = clamp(u32(pos.x), 0u, WIDTH - 1u);
    let y = clamp(u32(pos.y), 0u, HEIGHT - 1u);
    let i = idx(x, y);

    let stability = harmony_field[i].x;
    let snap = harmony_field[i].y;

    let size = clamp(snap * 0.5, 0.0, 1.0);
    let c = vec3<f32>(0.8, 1.0, 0.8) * stability;

    return vec4<f32>(c, size * 0.3);
}

