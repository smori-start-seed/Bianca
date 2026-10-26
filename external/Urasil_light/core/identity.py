import json
import os

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

class Identity:
    def __init__(self, data):
        self.data = data

    @staticmethod
    def load():
        path = os.path.join(DATA_PATH, "identity.json")
        baseline_path = os.path.join(DATA_PATH, "baseline_identity.json")

        # Baseline laden
        with open(baseline_path, "r") as f:
            baseline = json.load(f)

        # Identität laden oder baseline kopieren
        if os.path.exists(path):
            with open(path, "r") as f:
                identity = json.load(f)
        else:
            identity = baseline.copy()

        return Identity(identity)

    @staticmethod
    def save(data):
        path = os.path.join(DATA_PATH, "identity.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
