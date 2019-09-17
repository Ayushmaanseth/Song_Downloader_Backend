import falcon


class Response(falcon.Response):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def json(self):
        return self.media

    @json.setter
    def json(self, value):
        self.media = value

    @property
    def status_code(self):
        return int(self.status.split()[0])

    @status_code.setter
    def status_code(self, code):
        self.status = getattr(falcon, f"HTTP_{code}")
