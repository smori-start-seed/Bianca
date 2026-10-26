class SessionManager:
    def __init__(self, identity):
        self.identity = identity

    def start(self):
        self.identity.data["session_active"] = True

    def end(self):
        self.identity.data["session_active"] = False
