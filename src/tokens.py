class Token:
    def __init__(self, kind, value=None, line=None, col=None):
        self.kind = kind
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        if self.value is None:
            return f"Token({self.kind})"
        return f"Token({self.kind}, {self.value})"
