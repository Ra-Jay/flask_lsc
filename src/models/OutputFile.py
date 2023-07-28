class OutputFile:
    def __init__(self, classification, accuracy, error_rate, path, filename):
        self.classification = classification
        self.accuracy = accuracy
        self.error_rate = error_rate
        self.path = path
        self.filename = filename