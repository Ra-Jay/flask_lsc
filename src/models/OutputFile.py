class OutputFile:
    def __init__(self, name, classification, accuracy, error_rate, data, input_id, created_at, updated_at, deleted_at):
        self.name = name
        self.classification = classification
        self.accuracy = accuracy
        self.error_rate = error_rate
        self.data = data
        self.input_id = input_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at