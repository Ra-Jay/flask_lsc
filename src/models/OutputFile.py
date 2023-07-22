class OutputFile:
    def __init__(self, classification, accuracy, error_rate, filename):
        self.classification = classification
        self.accuracy = accuracy
        self.error_rate = error_rate
        self.filename = filename