"""
ALF Screensaver Module

This module provides a screensaver interface for ALF that:
1. Runs when the system is idle
2. Displays ALF's current state and interactions
3. Allows local processing without user intervention
4. Can optionally contribute to the global ALF network

Usage:
    from core.screensaver import ALFScreensaver
    screensaver = ALFScreensaver(identity, zyklus)
    screensaver.start()
"""

from .screensaver import (
    ALFScreensaver,
    ScreensaverMode,
    ResourceLimits,
    ScreensaverConfig,
    IdleDetector,
    ResourceManager,
    ALFVisualizer
)

__all__ = [
    'ALFScreensaver',
    'ALFVisualizer',
    'ScreensaverMode',
    'ResourceLimits',
    'ScreensaverConfig',
    'IdleDetector',
    'ResourceManager'
]
