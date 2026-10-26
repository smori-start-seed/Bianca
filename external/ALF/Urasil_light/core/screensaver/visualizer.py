"""
ALF Visualizer Module

This module provides visualization capabilities for the ALF screensaver,
displaying ALF's state, interactions, and growth in various styles.

Features:
- Multiple visualization modes (minimal, detailed, artistic)
- Dynamic rendering based on ALF state
- Resource-efficient rendering
- Customizable display options

Usage:
    from core.screensaver.visualizer import ALFVisualizer
    visualizer = ALFVisualizer(config)
    visualizer.render(alf_state)
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
import time


class VisualizationMode(Enum):
    """Available visualization modes."""
    MINIMAL = "minimal"
    DETAILED = "detailed"
    ARTISTIC = "artistic"
    TERMINAL = "terminal"


@dataclass
class VisualizationConfig:
    """Configuration for ALF visualization."""
    mode: VisualizationMode = VisualizationMode.MINIMAL
    width: int = 80
    height: int = 24
    color_scheme: str = "default"
    animation_speed: float = 1.0
    show_stats: bool = True
    show_interactions: bool = True
    show_network: bool = False
    max_fps: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "mode": self.mode.value,
            "width": self.width,
            "height": self.height,
            "color_scheme": self.color_scheme,
            "animation_speed": self.animation_speed,
            "show_stats": self.show_stats,
            "show_interactions": self.show_interactions,
            "show_network": self.show_network,
            "max_fps": self.max_fps
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VisualizationConfig":
        """Create from dictionary."""
        return cls(
            mode=VisualizationMode(data.get("mode", "minimal")),
            width=data.get("width", 80),
            height=data.get("height", 24),
            color_scheme=data.get("color_scheme", "default"),
            animation_speed=data.get("animation_speed", 1.0),
            show_stats=data.get("show_stats", True),
            show_interactions=data.get("show_interactions", True),
            show_network=data.get("show_network", False),
            max_fps=data.get("max_fps", 30)
        )


class ALFVisualizer:
    """
    Visualizes ALF's state and interactions.
    
    This class provides multiple visualization modes for displaying
    ALF's current state, recent interactions, and growth patterns.
    """
    
    def __init__(self, config: Optional[VisualizationConfig] = None):
        """
        Initialize the visualizer.
        
        Args:
            config: Visualization configuration
        """
        self.config = config or VisualizationConfig()
        self._last_render_time = 0
        self._frame_count = 0
    
    def render(self, state: Dict[str, Any]) -> str:
        """
        Render ALF's state as a string.
        
        Args:
            state: ALF state dictionary
            
        Returns:
            Rendered visualization as string
        """
        # Rate limiting
        current_time = time.time()
        if current_time - self._last_render_time < 1.0 / self.config.max_fps:
            return self._get_cached_frame()
        
        self._last_render_time = current_time
        self._frame_count += 1
        
        # Select renderer based on mode
        if self.config.mode == VisualizationMode.MINIMAL:
            return self._render_minimal(state)
        elif self.config.mode == VisualizationMode.DETAILED:
            return self._render_detailed(state)
        elif self.config.mode == VisualizationMode.ARTISTIC:
            return self._render_artistic(state)
        else:
            return self._render_terminal(state)
    
    def _get_cached_frame(self) -> str:
        """Get a cached/empty frame for rate limiting."""
        return ""
    
    def _render_minimal(self, state: Dict[str, Any]) -> str:
        """Render minimal visualization."""
        lines = []
        
        # Header
        name = state.get("identity", {}).get("name", "ALF")
        lines.append(f" {name} ")
        lines.append("")
        
        # Status
        status = state.get("status", "active")
        lines.append(f" Status: {status}")
        
        # Cycle
        zyklus = state.get("zyklus", {})
        phase = zyklus.get("phase", "unknown")
        lines.append(f" Phase: {phase}")
        
        # Stats
        if self.config.show_stats:
            stats = state.get("stats", {})
            lines.append(f" Interactions: {stats.get('total_interactions', 0)}")
            lines.append(f" Experience: {stats.get('total_experience', 0)}")
        
        return "\n".join(lines)
    
    def _render_detailed(self, state: Dict[str, Any]) -> str:
        """Render detailed visualization."""
        lines = []
        
        # Header
        name = state.get("identity", {}).get("name", "ALF")
        version = state.get("identity", {}).get("version", "1.0")
        lines.append(f"╔═══════════════════════════════════════════════════════════╗")
        lines.append(f"║  {name} v{version} {' ' * (40 - len(name) - len(version) - 4)}║")
        lines.append(f"╚═══════════════════════════════════════════════════════════╝")
        lines.append("")
        
        # Cycle Information
        zyklus = state.get("zyklus", {})
        lines.append("┌─ Zyklus ─────────────────────────────────────────────┐")
        lines.append(f"│ Phase: {zyklus.get('phase', 'unknown'):<42} │")
        lines.append(f"│ Sonne: {zyklus.get('sonne', 0):<42} │")
        lines.append(f"│ Mond:  {zyklus.get('mond', 0):<42} │")
        lines.append(f"│ Tag:   {zyklus.get('tag', 0):<42} │")
        lines.append("└──────────────────────────────────────────────────────┘")
        lines.append("")
        
        # Identity
        identity = state.get("identity", {})
        lines.append("┌─ Identity ────────────────────────────────────────────┐")
        lines.append(f"│ Name: {identity.get('name', 'ALF'):<43} │")
        lines.append(f"│ Grundton: {identity.get('grundton', 'neutral'):<38} │")
        lines.append(f"│ Mandat: {identity.get('mandat', {}).get('name', 'None'):<41} │")
        lines.append("└──────────────────────────────────────────────────────┘")
        lines.append("")
        
        # Statistics
        if self.config.show_stats:
            stats = state.get("stats", {})
            lines.append("┌─ Statistics ───────────────────────────────────────────┐")
            lines.append(f"│ Total Interactions: {stats.get('total_interactions', 0):<28} │")
            lines.append(f"│ Experience Entries: {stats.get('total_experience', 0):<26} │")
            lines.append(f"│ LLM Calls: {stats.get('llm_calls', 0):<35} │")
            lines.append(f"│ Whitelist Version: {stats.get('whitelist_version', '1.0'):<27} │")
            lines.append("└──────────────────────────────────────────────────────┘")
            lines.append("")
        
        # Recent Interactions
        if self.config.show_interactions:
            interactions = state.get("recent_interactions", [])[:5]
            if interactions:
                lines.append("┌─ Recent Interactions ─────────────────────────────────┐")
                for i, interaction in enumerate(interactions, 1):
                    input_text = interaction.get("input", "")[:30]
                    output_text = interaction.get("output", "")[:30]
                    lines.append(f"│ {i}. Input:  {input_text:<35} │")
                    lines.append(f"│    Output: {output_text:<35} │")
                lines.append("└──────────────────────────────────────────────────────┘")
        
        return "\n".join(lines)
    
    def _render_artistic(self, state: Dict[str, Any]) -> str:
        """Render artistic visualization with ASCII art."""
        lines = []
        
        # Get state values
        zyklus = state.get("zyklus", {})
        sonne = zyklus.get("sonne", 0)
        mond = zyklus.get("mond", 0)
        tag = zyklus.get("tag", 0)
        
        # Calculate sizes based on values
        sonne_size = int(sonne * 10)
        mond_size = int(mond * 10)
        tag_size = int(tag * 10)
        
        # Draw sun
        lines.append(self._draw_circle(sonne_size, "☀"))
        lines.append(f"  Sonne: {sonne:.2f}")
        lines.append("")
        
        # Draw moon
        lines.append(self._draw_circle(mond_size, "☽"))
        lines.append(f"  Mond: {mond:.2f}")
        lines.append("")
        
        # Draw day
        lines.append(self._draw_bar(tag_size, "▰"))
        lines.append(f"  Tag: {tag:.2f}")
        lines.append("")
        
        # Draw ALF name
        name = state.get("identity", {}).get("name", "ALF")
        lines.append(f"   {name}")
        lines.append(f"   {'=' * len(name)}")
        
        return "\n".join(lines)
    
    def _draw_circle(self, size: int, char: str) -> str:
        """Draw a simple circle with given size."""
        if size <= 0:
            return char
        
        diameter = max(3, size * 2 + 1)
        radius = diameter // 2
        
        result = []
        for y in range(-radius, radius + 1):
            line = []
            for x in range(-radius, radius + 1):
                if x * x + y * y <= radius * radius + radius:
                    line.append(char)
                else:
                    line.append(" ")
            result.append("".join(line))
        
        return "\n".join(result)
    
    def _draw_bar(self, size: int, char: str) -> str:
        """Draw a progress bar."""
        return char * max(1, size)
    
    def _render_terminal(self, state: Dict[str, Any]) -> str:
        """Render for terminal display (ANSI colors)."""
        lines = []
        
        # Use ANSI colors if supported
        use_colors = True  # Could detect terminal support
        
        # Header
        name = state.get("identity", {}).get("name", "ALF")
        if use_colors:
            lines.append(f"\033[1;36m{name}\033[0m")
        else:
            lines.append(name)
        lines.append("")
        
        # Cycle
        zyklus = state.get("zyklus", {})
        phase = zyklus.get("phase", "unknown")
        if use_colors:
            lines.append(f"\033[33mPhase:\033[0m {phase}")
        else:
            lines.append(f"Phase: {phase}")
        
        # Stats
        if self.config.show_stats:
            stats = state.get("stats", {})
            if use_colors:
                lines.append(f"\033[32mInteractions:\033[0m {stats.get('total_interactions', 0)}")
                lines.append(f"\033[32mExperience:\033[0m {stats.get('total_experience', 0)}")
            else:
                lines.append(f"Interactions: {stats.get('total_interactions', 0)}")
                lines.append(f"Experience: {stats.get('total_experience', 0)}")
        
        return "\n".join(lines)
    
    def get_frame_rate(self) -> float:
        """Get current frame rate."""
        if self._frame_count == 0:
            return 0.0
        
        elapsed = time.time() - self._last_render_time
        if elapsed <= 0:
            return 0.0
        
        return self._frame_count / elapsed
