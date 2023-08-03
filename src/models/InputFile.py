class InputFile:
    def __init__(self, name, dimensions, size, extension, data, weight_id, created_at, updated_at, deleted_at):
        self.name = name
        self.dimensions = dimensions
        self.size = size
        self.extension = extension
        self.data = data
        self.weight_id = weight_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at