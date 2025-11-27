
class AdScrapingError(Exception):
    def __init__(self, message, value):
        super().__init__(message)
        self.value = value

    def __str__(self):
        return f"{self.args[0]} (Contexto: {self.value})"