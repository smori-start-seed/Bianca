// src/pipelines.rs
use crate::sim::{SatuRingSim, WIDTH, HEIGHT};
use wgpu::util::DeviceExt;

pub struct SatuRingPipelines {
    pub update_pipeline: wgpu::ComputePipeline,
    pub update_bind_group_layout: wgpu::BindGroupLayout,
    pub update_bind_group: wgpu::BindGroup,
}

impl SatuRingPipelines {
    pub fn new(device: &wgpu::Device, sim: &SatuRingSim) -> Self {
        let update_shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
            label: Some("SatuRing Update Shader"),
            source: wgpu::ShaderSource::Wgsl(include_str!("shaders/update.wgsl").into()),
        });

        let update_bind_group_layout =
            device.create_bind_group_layout(&wgpu::BindGroupLayoutDescriptor {
                label: Some("SatuRing Update BGL"),
                entries: &[
                    // params
                    wgpu::BindGroupLayoutEntry {
                        binding: 0,
                        visibility: wgpu::ShaderStages::COMPUTE,
                        ty: wgpu::BindingType::Buffer {
                            ty: wgpu::BufferBindingType::Uniform,
                            has_dynamic_offset: false,
                            min_binding_size: None,
                        },
                        count: None,
                    },
                    // color_grid
                    wgpu::BindGroupLayoutEntry {
                        binding: 1,
                        visibility: wgpu::ShaderStages::COMPUTE,
                        ty: wgpu::BindingType::Buffer {
                            ty: wgpu::BufferBindingType::Storage { read_only: false },
                            has_dynamic_offset: false,
                            min_binding_size: None,
                        },
                        count: None,
                    },
                    // drift_field
                    wgpu::BindGroupLayoutEntry {
                        binding: 2,
                        visibility: wgpu::ShaderStages::COMPUTE,
                        ty: wgpu::BindingType::Buffer {
                            ty: wgpu::BufferBindingType::Storage { read_only: false },
                            has_dynamic_offset: false,
                            min_binding_size: None,
                        },
                        count: None,
                    },
                    // resonance_field
                    wgpu::BindGroupLayoutEntry {
                        binding: 3,
                        visibility: wgpu::ShaderStages::COMPUTE,
                        ty: wgpu::BindingType::Buffer {
                            ty: wgpu::BufferBindingType::Storage { read_only: false },
                            has_dynamic_offset: false,
                            min_binding_size: None,
                        },
                        count: None,
                    },
                    // vortex_field
                    wgpu::BindGroupLayoutEntry {
                        binding: 4,
                        visibility: wgpu::ShaderStages::COMPUTE,
                        ty: wgpu::BindingType::Buffer {
                            ty: wgpu::BufferBindingType::Storage { read_only: false },
                            has_dynamic_offset: false,
                            min_binding_size: None,
                        },
                        count: None,
                    },
                    // harmony_field
                    wgpu::BindGroupLayoutEntry {
                        binding: 5,
                        visibility: wgpu::ShaderStages::COMPUTE,
                        ty: wgpu::BindingType::Buffer {
                            ty: wgpu::BufferBindingType::Storage { read_only: false },
                            has_dynamic_offset: false,
                            min_binding_size: None,
                        },
                        count: None,
                    },
                    // overlay_mask
                    wgpu::BindGroupLayoutEntry {
                        binding: 6,
                        visibility: wgpu::ShaderStages::COMPUTE,
                        ty: wgpu::BindingType::Buffer {
                            ty: wgpu::BufferBindingType::Storage { read_only: false },
                            has_dynamic_offset: false,
                            min_binding_size: None,
                        },
                        count: None,
                    },
                ],
            });

        let update_bind_group = device.create_bind_group(&wgpu::BindGroupDescriptor {
            label: Some("SatuRing Update BG"),
            layout: &update_bind_group_layout,
            entries: &[
                wgpu::BindGroupEntry {
                    binding: 0,
                    resource: sim.params_buffer.as_entire_binding(),
                },
                wgpu::BindGroupEntry {
                    binding: 1,
                    resource: sim.color_grid.as_entire_binding(),
                },
                wgpu::BindGroupEntry {
                    binding: 2,
                    resource: sim.drift_field.as_entire_binding(),
                },
                wgpu::BindGroupEntry {
                    binding: 3,
                    resource: sim.resonance_field.as_entire_binding(),
                },
                wgpu::BindGroupEntry {
                    binding: 4,
                    resource: sim.vortex_field.as_entire_binding(),
                },
                wgpu::BindGroupEntry {
                    binding: 5,
                    resource: sim.harmony_field.as_entire_binding(),
                },
                wgpu::BindGroupEntry {
                    binding: 6,
                    resource: sim.overlay_mask.as_entire_binding(),
                },
            ],
        });

        let update_pipeline_layout =
            device.create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
                label: Some("SatuRing Update Pipeline Layout"),
                bind_group_layouts: &[&update_bind_group_layout],
                push_constant_ranges: &[],
            });

        let update_pipeline = device.create_compute_pipeline(&wgpu::ComputePipelineDescriptor {
            label: Some("SatuRing Update Pipeline"),
            layout: Some(&update_pipeline_layout),
            module: &update_shader,
            entry_point: "main",
        });

        Self {
            update_pipeline,
            update_bind_group_layout,
            update_bind_group,
        }
    }

    pub fn dispatch_update(
        &self,
        encoder: &mut wgpu::CommandEncoder,
        device: &wgpu::Device,
    ) {
        let mut cpass = encoder.begin_compute_pass(&wgpu::ComputePassDescriptor {
            label: Some("SatuRing Update Pass"),
        });
        cpass.set_pipeline(&self.update_pipeline);
        cpass.set_bind_group(0, &self.update_bind_group, &[]);

        let wg_x = (WIDTH + 7) / 8;
        let wg_y = (HEIGHT + 7) / 8;

        cpass.dispatch_workgroups(wg_x, wg_y, 1);
    }
}

// src/pipelines.rs (nur Render-Teil)

use crate::sim::{SatuRingSim, WIDTH, HEIGHT};

pub struct RenderPipelineSet {
    pub pipeline: wgpu::RenderPipeline,
    pub bind_group: wgpu::BindGroup,
    pub target_view: wgpu::TextureView,
}

pub struct SatuRingRenderPipelines {
    pub base: RenderPipelineSet,
    pub drift: RenderPipelineSet,
    pub resonance: RenderPipelineSet,
    pub vortex: RenderPipelineSet,
    pub harmony: RenderPipelineSet,
    pub overlay: RenderPipelineSet,
}

impl SatuRingRenderPipelines {
    pub fn new(
        device: &wgpu::Device,
        sim: &SatuRingSim,
        surface_format: wgpu::TextureFormat,
    ) -> Self {
        let quad_shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
            label: Some("Fullscreen Quad Shader"),
            source: wgpu::ShaderSource::Wgsl(include_str!("shaders/fullscreen_quad.wgsl").into()),
        });

        fn make_layer(
            device: &wgpu::Device,
            quad_shader: &wgpu::ShaderModule,
            surface_format: wgpu::TextureFormat,
            params_buffer: &wgpu::Buffer,
            field_buffer: &wgpu::Buffer,
            shader_path: &str,
            label: &str,
        ) -> RenderPipelineSet {
            let shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
                label: Some(label),
                source: wgpu::ShaderSource::Wgsl(include_str!(shader_path).into()),
            });

            let texture = device.create_texture(&wgpu::TextureDescriptor {
                label: Some(&format!("{label} Texture")),
                size: wgpu::Extent3d {
                    width: WIDTH,
                    height: HEIGHT,
                    depth_or_array_layers: 1,
                },
                mip_level_count: 1,
                sample_count: 1,
                dimension: wgpu::TextureDimension::D2,
                format: surface_format,
                usage: wgpu::TextureUsages::RENDER_ATTACHMENT | wgpu::TextureUsages::TEXTURE_BINDING,
                view_formats: &[],
            });

            let view = texture.create_view(&wgpu::TextureViewDescriptor::default());

            let bgl = device.create_bind_group_layout(&wgpu::BindGroupLayoutDescriptor {
                label: Some(&format!("{label} BGL")),
                entries: &[
                    wgpu::BindGroupLayoutEntry {
                        binding: 0,
                        visibility: wgpu::ShaderStages::FRAGMENT,
                        ty: wgpu::BindingType::Buffer {
                            ty: wgpu::BufferBindingType::Uniform,
                            has_dynamic_offset: false,
                            min_binding_size: None,
                        },
                        count: None,
                    },
                    wgpu::BindGroupLayoutEntry {
                        binding: 1,
                        visibility: wgpu::ShaderStages::FRAGMENT,
                        ty: wgpu::BindingType::Buffer {
                            ty: wgpu::BufferBindingType::Storage { read_only: true },
                            has_dynamic_offset: false,
                            min_binding_size: None,
                        },
                        count: None,
                    },
                ],
            });

            let bind_group = device.create_bind_group(&wgpu::BindGroupDescriptor {
                label: Some(&format!("{label} BG")),
                layout: &bgl,
                entries: &[
                    wgpu::BindGroupEntry {
                        binding: 0,
                        resource: params_buffer.as_entire_binding(),
                    },
                    wgpu::BindGroupEntry {
                        binding: 1,
                        resource: field_buffer.as_entire_binding(),
                    },
                ],
            });

            let pipeline_layout =
                device.create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
                    label: Some(&format!("{label} Pipeline Layout")),
                    bind_group_layouts: &[&bgl],
                    push_constant_ranges: &[],
                });

            let pipeline = device.create_render_pipeline(&wgpu::RenderPipelineDescriptor {
                label: Some(&format!("{label} Pipeline")),
                layout: Some(&pipeline_layout),
                vertex: wgpu::VertexState {
                    module: quad_shader,
                    entry_point: "vs_main",
                    buffers: &[],
                },
                fragment: Some(wgpu::FragmentState {
                    module: &shader,
                    entry_point: "fs_main",
                    targets: &[Some(wgpu::ColorTargetState {
                        format: surface_format,
                        blend: Some(wgpu::BlendState::ALPHA_BLENDING),
                        write_mask: wgpu::ColorWrites::ALL,
                    })],
                }),
                primitive: wgpu::PrimitiveState::default(),
                depth_stencil: None,
                multisample: wgpu::MultisampleState::default(),
                multiview: None,
            });

            RenderPipelineSet {
                pipeline,
                bind_group,
                target_view: view,
            }
        }

        Self {
            base: make_layer(
                device,
                &quad_shader,
                surface_format,
                &sim.params_buffer,
                &sim.color_grid,
                "shaders/render_base.wgsl",
                "Base",
            ),
            drift: make_layer(
                device,
                &quad_shader,
                surface_format,
                &sim.params_buffer,
                &sim.drift_field,
                "shaders/render_drift.wgsl",
                "Drift",
            ),
            resonance: make_layer(
                device,
                &quad_shader,
                surface_format,
                &sim.params_buffer,
                &sim.resonance_field,
                "shaders/render_resonance.wgsl",
                "Resonance",
            ),
            vortex: make_layer(
                device,
                &quad_shader,
                surface_format,
                &sim.params_buffer,
                &sim.vortex_field,
                "shaders/render_vortex.wgsl",
                "Vortex",
            ),
            harmony: make_layer(
                device,
                &quad_shader,
                surface_format,
                &sim.params_buffer,
                &sim.harmony_field,
                "shaders/render_harmony.wgsl",
                "Harmony",
            ),
            overlay: make_layer(
                device,
                &quad_shader,
                surface_format,
                &sim.params_buffer,
                &sim.overlay_mask,
                "shaders/render_overlay.wgsl",
                "Overlay",
            ),
        }
    }
}

pub struct CompositePipeline {
    pub pipeline: wgpu::RenderPipeline,
    pub bind_group: wgpu::BindGroup,
}

impl CompositePipeline {
    pub fn new(
        device: &wgpu::Device,
        surface_format: wgpu::TextureFormat,
        layers: &[&wgpu::TextureView],
    ) -> Self {
        let shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
            label: Some("Composite Shader"),
            source: wgpu::ShaderSource::Wgsl(include_str!("shaders/composite.wgsl").into()),
        });

        let bgl = device.create_bind_group_layout(&wgpu::BindGroupLayoutDescriptor {
            label: Some("Composite BGL"),
            entries: &[
                // 6 Texturen
                (0..6).map(|i| wgpu::BindGroupLayoutEntry {
                    binding: i,
                    visibility: wgpu::ShaderStages::FRAGMENT,
                    ty: wgpu::BindingType::Texture {
                        sample_type: wgpu::TextureSampleType::Float { filterable: false },
                        view_dimension: wgpu::TextureViewDimension::D2,
                        multisampled: false,
                    },
                    count: None,
                }).collect::<Vec<_>>()
            ].concat(),
        });

        let bind_group = device.create_bind_group(&wgpu::BindGroupDescriptor {
            label: Some("Composite BG"),
            layout: &bgl,
            entries: &[
                (0..6).map(|i| wgpu::BindGroupEntry {
                    binding: i,
                    resource: wgpu::BindingResource::TextureView(layers[i]),
                }).collect::<Vec<_>>()
            ].concat(),
        });

        let pipeline_layout =
            device.create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
                label: Some("Composite Pipeline Layout"),
                bind_group_layouts: &[&bgl],
                push_constant_ranges: &[],
            });

        let pipeline = device.create_render_pipeline(&wgpu::RenderPipelineDescriptor {
            label: Some("Composite Pipeline"),
            layout: Some(&pipeline_layout),
            vertex: wgpu::VertexState {
                module: &shader,
                entry_point: "vs_main",
                buffers: &[],
            },
            fragment: Some(wgpu::FragmentState {
                module: &shader,
                entry_point: "fs_main",
                targets: &[Some(wgpu::ColorTargetState {
                    format: surface_format,
                    blend: Some(wgpu::BlendState::REPLACE),
                    write_mask: wgpu::ColorWrites::ALL,
                })],
            }),
            primitive: wgpu::PrimitiveState::default(),
            depth_stencil: None,
            multisample: wgpu::MultisampleState::default(),
            multiview: None,
        });

        Self { pipeline, bind_group }
    }
}

