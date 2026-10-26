#include "common_params.wgsl" // oder Inhalt direkt reinkopieren

@group(0) @binding(0)
var<uniform> params: SatuRingParams;

@group(0) @binding(1)
var<storage, read> color_grid: array<vec4<f32>>;

@fragment
fn fs_main(@builtin(position) pos: vec4<f32>) -> @location(0) vec4<f32> {
    let x = clamp(u32(pos.x), 0u, WIDTH - 1u);
    let y = clamp(u32(pos.y), 0u, HEIGHT - 1u);
    let i = idx(x, y);
    return color_grid[i]; // rgb = Farbe, a = Energie oder 1.0
}

