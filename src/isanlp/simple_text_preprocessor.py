class SimpleTextPreprocessor:
    def __init__(self, delay_init=False):
        self.mapper = [
            ('_x000D_', ''),
            ('\n ', '\n'),
            (' \n', '\n'),
            ('\n\n', '\n'),
        ]

    def __call__(self, text):
        for pair in self.mapper:
            key, value = pair
            while key in text:
                text = text.replace(key, value)

        if text[:2] == '. ':
            text = text[2:]

        return {
            'text': text.strip()
        }
