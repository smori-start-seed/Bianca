#include "common_params.wgsl"

@group(0) @binding(0)
var<uniform> params: SatuRingParams;

@group(0) @binding(1)
var<storage, read> overlay_mask: array<f32>;

@fragment
fn fs_main(@builtin(position) pos: vec4<f32>) -> @location(0) vec4<f32> {
    let x = clamp(u32(pos.x), 0u, WIDTH - 1u);
    let y = clamp(u32(pos.y), 0u, HEIGHT - 1u);
    let i = idx(x, y);

    let v = overlay_mask[i];
    // neutrales Grau, nur Alpha wichtig
    return vec4<f32>(0.0, 0.0, 0.0, v);
}

