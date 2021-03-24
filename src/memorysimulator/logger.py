
class Logger:
    def on_malloc(self, address, num_words):
        pass

    def on_free(self, address, num_words):
        pass

    def on_read(self, address):
        pass

    def on_write(self, address):
        pass

    def on_construct(self, address, typ):
        pass
        

class HistoryLogger(Logger):
    def __init__(self):
        self.history = []

    def on_read(self, address):
        self.history.append(address)

    def on_write(self, address):
        self.history.append(address)
