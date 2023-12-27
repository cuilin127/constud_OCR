class APIResponse:
    def __init__(self, code, message, object):
        self.code = code
        self.message = message
        self.object = object