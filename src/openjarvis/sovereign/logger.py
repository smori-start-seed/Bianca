"""
Interaction Ledger — the memory of the Bianca node.
Ported from OpenJarvis/kernel/logger.py: human/AI-readable Markdown audits
written under a configurable logs directory.
"""

import datetime
from pathlib import Path


class InteractionLogger:
    """Handles the 'Interaction Ledger' by writing audit logs to Markdown files."""

    def __init__(self, logs_dir: str):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def log_event(self, event_type: str, message: str, actor: str = "Bianca"):
        """Logs a new interaction event to a timestamped Markdown file."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        log_file = self.logs_dir / f"interaction_{stamp}.md"

        entry = f"""
### [Event] {event_type}
- **Timestamp**: {timestamp}
- **Actor**: {actor}
- **Message**: {message}

---
"""
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry)
        return str(log_file)