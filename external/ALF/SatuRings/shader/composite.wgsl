@group(0) @binding(0) var base_tex: texture_2d<f32>;
@group(0) @binding(1) var drift_tex: texture_2d<f32>;
@group(0) @binding(2) var res_tex: texture_2d<f32>;
@group(0) @binding(3) var vortex_tex: texture_2d<f32>;
@group(0) @binding(4) var harmony_tex: texture_2d<f32>;
@group(0) @binding(5) var overlay_tex: texture_2d<f32>;

@fragment
fn fs_main(@builtin(position) pos: vec4<f32>) -> @location(0) vec4<f32> {
    let uv = pos.xy;

    let base = textureLoad(base_tex, vec2<i32>(i32(uv.x), i32(uv.y)), 0);
    let drift = textureLoad(drift_tex, vec2<i32>(i32(uv.x), i32(uv.y)), 0);
    let res = textureLoad(res_tex, vec2<i32>(i32(uv.x), i32(uv.y)), 0);
    let vortex = textureLoad(vortex_tex, vec2<i32>(i32(uv.x), i32(uv.y)), 0);
    let harmony = textureLoad(harmony_tex, vec2<i32>(i32(uv.x), i32(uv.y)), 0);
    let overlay = textureLoad(overlay_tex, vec2<i32>(i32(uv.x), i32(uv.y)), 0);

    var col = base;

    // Add
    col.rgb = col.rgb + drift.rgb * drift.a;

    // Screen
    col.rgb = 1.0 - (1.0 - col.rgb) * (1.0 - res.rgb * res.a);

    // Overlay
    col.rgb = mix(
        2.0 * col.rgb * vortex.rgb,
        1.0 - 2.0 * (1.0 - col.rgb) * (1.0 - vortex.rgb),
        step(0.5, col.rgb)
    );

    // Soft-Light
    col.rgb = mix(
        sqrt(col.rgb) * harmony.rgb,
        (col.rgb * harmony.rgb) + (col.rgb * (1.0 - harmony.rgb)),
        harmony.a
    );

    // Overlay-Maske (Alpha)
    col.rgb = mix(col.rgb, col.rgb * 0.5, overlay.a);

    col.a = 1.0;
    return col;
}

