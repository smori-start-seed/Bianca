"""
ALF Screensaver Module

This module implements a screensaver for ALF that:
- Runs when the system is idle
- Displays ALF's current state (Zyklus, Mandat, Nodus)
- Processes local interactions
- Can contribute to global ALF network (optional)
- Respects user privacy and resource limits

Architecture:
    ALFScreensaver
    ├── ALFVisualizer (graphical display)
    ├── IdleDetector (system idle detection)
    ├── ResourceManager (CPU/RAM limits)
    └── ALFIntegration (connects to ALF core)

Example:
    from core.screensaver import ALFScreensaver
    from core.identity import Identity
    from core.zyklus import Zyklus
    
    identity = Identity.load()
    zyklus = Zyklus(identity.data)
    screensaver = ALFScreensaver(identity.data, zyklus)
    screensaver.start()
"""

import time
import threading
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

import psutil  # For system monitoring


class ScreensaverMode(Enum):
    """Possible modes for the ALF screensaver."""
    IDLE = "idle"           # System is idle, screensaver is active
    ACTIVE = "active"       # System is in use, screensaver is hidden
    PAUSED = "paused"       # Screensaver is temporarily paused


@dataclass
class ResourceLimits:
    """Resource limits for screensaver operation."""
    max_cpu_percent: float = 20.0      # Max CPU usage percentage
    max_memory_mb: int = 256            # Max memory usage in MB
    max_disk_mb: int = 100             # Max disk usage in MB
    allow_network: bool = True         # Allow network operations
    allow_llm: bool = True             # Allow LLM operations


@dataclass
class ScreensaverConfig:
    """Configuration for the ALF screensaver."""
    # Display settings
    visualization_type: str = "minimal"  # 'minimal', 'detailed', 'artistic'
    refresh_interval: float = 0.5       # Seconds between updates
    theme: str = "dark"                  # 'dark', 'light', 'solarized'
    
    # Behavior settings
    idle_threshold: int = 300           # 5 minutes of inactivity
    mode: ScreensaverMode = ScreensaverMode.IDLE
    resource_limits: ResourceLimits = field(default_factory=ResourceLimits)
    
    # Network settings
    contribute_to_global: bool = False   # Contribute to global ALF network
    global_network_url: str = ""        # URL for global network (if any)
    
    # Privacy settings
    allow_analytics: bool = False        # Allow usage analytics
    data_sharing_level: str = "none"     # 'none', 'anonymous', 'limited'


class IdleDetector:
    """
    Detects when the system is idle (no user input).
    
    Uses multiple signals:
    - Mouse/keyboard inactivity
    - CPU usage
    - System load
    """
    
    def __init__(self, threshold_seconds: int = 300):
        """
        Initialize the idle detector.
        
        Args:
            threshold_seconds: Seconds of inactivity before considered idle
        """
        self.threshold = threshold_seconds
        self.last_activity_time = time.time()
        self._setup_mouse_listener()
    
    def _setup_mouse_listener(self):
        """Setup mouse/keyboard activity listeners."""
        try:
            import pynput
            from pynput import mouse, keyboard
            
            def on_move(x, y):
                self.last_activity_time = time.time()
            
            def on_click(x, y, button, pressed):
                self.last_activity_time = time.time()
            
            def on_press(key):
                self.last_activity_time = time.time()
            
            # Start listeners in background threads
            mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
            keyboard_listener = keyboard.Listener(on_press=on_press)
            
            mouse_listener.start()
            keyboard_listener.start()
            
            self.listeners = [mouse_listener, keyboard_listener]
        except ImportError:
            # Fallback: Only use CPU monitoring
            self.listeners = []
    
    def is_idle(self) -> bool:
        """
        Check if the system is currently idle.
        
        Returns:
            True if system has been idle for threshold seconds
        """
        current_time = time.time()
        idle_time = current_time - self.last_activity_time
        
        # Also check CPU usage - if CPU is high, system is not idle
        cpu_usage = psutil.cpu_percent(interval=0.1)
        if cpu_usage > 5:  # If CPU > 5%, system is active
            self.last_activity_time = current_time
            return False
        
        return idle_time >= self.threshold
    
    def get_idle_time(self) -> float:
        """
        Get the current idle time in seconds.
        
        Returns:
            Seconds since last activity
        """
        return time.time() - self.last_activity_time
    
    def cleanup(self):
        """Clean up listeners."""
        for listener in self.listeners:
            try:
                listener.stop()
            except:
                pass


class ResourceManager:
    """
    Manages system resources to ensure screensaver doesn't overload the system.
    """
    
    def __init__(self, limits: ResourceLimits):
        """
        Initialize resource manager.
        
        Args:
            limits: Resource limits configuration
        """
        self.limits = limits
    
    def check_resources(self) -> bool:
        """
        Check if current resource usage is within limits.
        
        Returns:
            True if resources are within limits, False otherwise
        """
        # Check CPU
        cpu_usage = psutil.cpu_percent(interval=0.1)
        if cpu_usage > self.limits.max_cpu_percent:
            return False
        
        # Check memory
        memory_usage = psutil.virtual_memory().used / (1024 * 1024)  # MB
        if memory_usage > self.limits.max_memory_mb:
            return False
        
        # Check disk (if applicable)
        try:
            disk_usage = psutil.disk_usage('/').used / (1024 * 1024)  # MB
            if disk_usage > self.limits.max_disk_mb:
                return False
        except:
            pass
        
        return True
    
    def wait_for_resources(self, timeout: float = 5.0) -> bool:
        """
        Wait until resources are available.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if resources became available, False if timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_resources():
                return True
            time.sleep(0.1)
        return False


class ALFVisualizer:
    """
    Visualizes ALF's current state for the screensaver.
    
    Supports multiple visualization types:
    - Minimal: Basic text display
    - Detailed: Full state information
    - Artistic: Creative visualizations
    """
    
    def __init__(self, identity: Dict[str, Any], zyklus, config: ScreensaverConfig):
        """
        Initialize the visualizer.
        
        Args:
            identity: ALF identity data
            zyklus: Zyklus instance
            config: Screensaver configuration
        """
        self.identity = identity
        self.zyklus = zyklus
        self.config = config
    
    def render(self) -> str:
        """
        Render the current ALF state as text.
        
        Returns:
            Formatted string for display
        """
        if self.config.visualization_type == "minimal":
            return self._render_minimal()
        elif self.config.visualization_type == "detailed":
            return self._render_detailed()
        else:  # artistic
            return self._render_artistic()
    
    def _render_minimal(self) -> str:
        """Render minimal visualization."""
        name = self.identity.get("name", "ALF")
        matrix = self.zyklus.matrix() if self.zyklus else {}
        grundmodus = matrix.get("grundmodus", "neutral")
        
        return f"{name} | {grundmodus} | {self._get_time_str()}"
    
    def _render_detailed(self) -> str:
        """Render detailed visualization."""
        name = self.identity.get("name", "ALF")
        version = self.identity.get("version", "1.0")
        grundton = self.identity.get("grundton", "neutral")
        
        matrix = self.zyklus.matrix() if self.zyklus else {}
        sonne = matrix.get("sonne", 0)
        mond = matrix.get("mond", 0)
        tag = matrix.get("tag", 0)
        grundmodus = matrix.get("grundmodus", "neutral")
        stimmung = matrix.get("stimmung", "neutral")
        fokus = matrix.get("fokus", "neutral")
        
        mandat = self.identity.get("mandat", {})
        mandat_name = mandat.get("name", "kein Mandat")
        
        return (
            f"{'='*60}\n"
            f"{name} v{version}\n"
            f"{'='*60}\n"
            f"Grundton: {grundton}\n"
            f"Zyklus: Sonne={sonne}° | Mond={mond}° | Tag={tag}°\n"
            f"Modus: {grundmodus} | Stimmung: {stimmung} | Fokus: {fokus}\n"
            f"Mandat: {mandat_name}\n"
            f"{'='*60}\n"
            f"Lokale Zeit: {self._get_time_str()}\n"
            f"{'='*60}"
        )
    
    def _render_artistic(self) -> str:
        """Render artistic visualization."""
        matrix = self.zyklus.matrix() if self.zyklus else {}
        grundmodus = matrix.get("grundmodus", "neutral")
        
        # Artistic representation based on mode
        if "nacht" in grundmodus.lower():
            return self._render_night()
        elif "tag" in grundmodus.lower():
            return self._render_day()
        elif "dämmerung" in grundmodus.lower():
            return self._render_twilight()
        else:
            return self._render_neutral()
    
    def _render_night(self) -> str:
        """Render night-themed visualization."""
        return (
            "  🌙  \n"
            " /   \  \n"
            "|  •  |  ALF in Nachtmodus...\n"
            " \\   /  \n"
            "  🌑  \n"
            "Reflexion | Stille | Tiefe"
        )
    
    def _render_day(self) -> str:
        """Render day-themed visualization."""
        return (
            "  ☀️  \n"
            " /   \  \n"
            "|  •  |  ALF in Tagmodus...\n"
            " \\   /  \n"
            "  🌞  \n"
            "Aktivität | Klarheit | Handeln"
        )
    
    def _render_twilight(self) -> str:
        """Render twilight-themed visualization."""
        return (
            "  🌅  \n"
            " /   \  \n"
            "|  •  |  ALF in Übergangsmodus...\n"
            " \\   /  \n"
            "  🌇  \n"
            "Veränderung | Balance | Transformation"
        )
    
    def _render_neutral(self) -> str:
        """Render neutral visualization."""
        return (
            "  ◎  \n"
            " /   \  \n"
            "|  •  |  ALF aktiv\n"
            " \\   /  \n"
            "  ◎  \n"
            "Gleichgewicht | Harmonie | Präsenz"
        )
    
    def _get_time_str(self) -> str:
        """Get formatted time string."""
        return time.strftime("%Y-%m-%d %H:%M:%S")


class ALFScreensaver:
    """
    Main ALF screensaver class.
    
    Manages the screensaver lifecycle:
    - Detects idle state
    - Renders ALF visualizations
    - Manages resources
    - Handles user interactions
    
    The screensaver can:
    1. Run as a traditional screensaver (when system is idle)
    2. Run as a background service (always-on, low priority)
    3. Contribute to global ALF network (optional)
    """
    
    def __init__(
        self,
        identity: Dict[str, Any],
        zyklus,
        config: Optional[ScreensaverConfig] = None,
        on_interaction: Optional[Callable] = None
    ):
        """
        Initialize the ALF screensaver.
        
        Args:
            identity: ALF identity data
            zyklus: Zyklus instance
            config: Screensaver configuration (optional)
            on_interaction: Callback for user interactions
        """
        self.identity = identity
        self.zyklus = zyklus
        self.config = config or ScreensaverConfig()
        self.on_interaction = on_interaction
        
        # Initialize components
        self.idle_detector = IdleDetector(self.config.idle_threshold)
        self.resource_manager = ResourceManager(self.config.resource_limits)
        self.visualizer = ALFVisualizer(identity, zyklus, self.config)
        
        # State
        self.running = False
        self.screensaver_thread: Optional[threading.Thread] = None
        self.last_render_time = 0
    
    def start(self):
        """
        Start the screensaver.
        """
        if self.running:
            return
        
        self.running = True
        self.screensaver_thread = threading.Thread(target=self._run, daemon=True)
        self.screensaver_thread.start()
        
        print("✅ ALF Screensaver gestartet")
    
    def stop(self):
        """
        Stop the screensaver.
        """
        self.running = False
        if self.screensaver_thread:
            self.screensaver_thread.join(timeout=1.0)
        
        self.idle_detector.cleanup()
        print("⏹️ ALF Screensaver beendet")
    
    def _run(self):
        """
        Main screensaver loop.
        """
        while self.running:
            try:
                # Check if system is idle
                if self.idle_detector.is_idle():
                    self._enter_screensaver_mode()
                else:
                    self._exit_screensaver_mode()
                
                # Check resources before rendering
                if self.resource_manager.check_resources():
                    self._render()
                else:
                    # Wait for resources
                    self.resource_manager.wait_for_resources()
                
                # Sleep to prevent high CPU usage
                time.sleep(self.config.refresh_interval)
                
            except KeyboardInterrupt:
                self.stop()
                break
            except Exception as e:
                print(f"⚠️ Screensaver Fehler: {e}")
                time.sleep(1.0)
    
    def _enter_screensaver_mode(self):
        """
        Enter screensaver mode.
        """
        if self.config.mode == ScreensaverMode.IDLE:
            return
        
        self.config.mode = ScreensaverMode.IDLE
        print("🌙 ALF Screensaver aktiv (System idle)")
        
        # Optional: Start ALF processing in background
        self._start_background_processing()
    
    def _exit_screensaver_mode(self):
        """
        Exit screensaver mode.
        """
        if self.config.mode == ScreensaverMode.ACTIVE:
            return
        
        self.config.mode = ScreensaverMode.ACTIVE
        print("☀️ ALF Screensaver inaktiv (System aktiv)")
        
        # Stop background processing
        self._stop_background_processing()
    
    def _render(self):
        """
        Render the screensaver visualization.
        """
        if self.config.mode != ScreensaverMode.IDLE:
            return
        
        # Only render if enough time has passed
        current_time = time.time()
        if current_time - self.last_render_time < self.config.refresh_interval:
            return
        
        self.last_render_time = current_time
        
        # Get visualization
        output = self.visualizer.render()
        
        # Clear screen and print (simplified for now)
        self._clear_screen()
        print(output)
        
        # Trigger interaction callback if provided
        if self.on_interaction:
            self.on_interaction(output)
    
    def _start_background_processing(self):
        """
        Start background ALF processing.
        """
        if not self.config.resource_limits.allow_llm:
            return
        
        # In a real implementation, this would:
        # 1. Run local ALF processing (LLM, WerteTeilen, etc.)
        # 2. Contribute to global network if enabled
        # 3. Store local experiences
        
        # For now, just log
        print("🔄 Hintergrundverarbeitung aktiviert")
    
    def _stop_background_processing(self):
        """
        Stop background ALF processing.
        """
        print("⏸️ Hintergrundverarbeitung pausiert")
    
    def _clear_screen(self):
        """
        Clear the console screen.
        """
        # Cross-platform clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current screensaver status.
        
        Returns:
            Dictionary with current status
        """
        return {
            "mode": self.config.mode.value,
            "is_idle": self.idle_detector.is_idle(),
            "idle_time": self.idle_detector.get_idle_time(),
            "resources_ok": self.resource_manager.check_resources(),
            "running": self.running,
            "last_render": self.last_render_time
        }
    
    def force_render(self):
        """
        Force a render cycle (for testing).
        """
        self._render()
    
    def set_config(self, config: ScreensaverConfig):
        """
        Update screensaver configuration.
        
        Args:
            config: New configuration
        """
        self.config = config
        self.idle_detector.threshold = config.idle_threshold
