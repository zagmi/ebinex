from typing import Any, Dict

class Sigma:
    LF = r'\n'
    NULL = r'\u0000'

class Frame:

    def __init__(self, command: str, headers: Dict, body: Any):
        self.command = command
        self.headers = headers
        self.body = body or ''

    def __str__(self):
        lines = [self.command]
        skip_content_length = 'content-length' in self.headers
        if skip_content_length:
            del self.headers['content-length']

        for name in self.headers:
            value = self.headers[name]
            lines.append(f"{name}:{value}")

        if self.body is not None and not skip_content_length:
            content_length = len(str(self.body))
            lines.append(f'content-length:{content_length}')

        lines.append(f'{Sigma.LF}{self.body}')
        return Sigma.LF.join(lines)

    @staticmethod
    def unmarshall(data: str):
        lines = data.split(Sigma.LF)
        command = lines[0].strip()
        headers = {}
        body = None
        start = 1

        for start in range(1, len(lines)):
            line = lines[start].strip()
            if line == '':
                break
            key_value = line.split(':', 1)
            if len(key_value) == 2:
                key, value = key_value
                headers[key.strip()] = value.strip()

        if start + 1 < len(lines):
            body_line = lines[start + 1].strip()
            body = None if body_line == Sigma.NULL else body_line[:-1]

        return Frame(command, headers, body)

    @staticmethod
    def marshall(command: str, headers: Dict, body: Any):
        return f'{Frame(command, headers, body)}{Sigma.NULL}'
