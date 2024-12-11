from typing import Dict

class BYTE:
    LF = r'\n'
    NULL = r'\u0000'

class Frame:

    def __init__(self, command, headers: Dict, body):
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
            lines.append(f'content-length:{len(self.body)}')

        lines.append(f'{BYTE.LF}{self.body}')
        return BYTE.LF.join(lines)

    @staticmethod
    def unmarshall(data: str):
        lines = data.split(BYTE.LF)
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
            body = None if body_line == BYTE.NULL else body_line[:-1]

        return Frame(command, headers, body)

    @staticmethod
    def marshall(command, headers, body):
        payload = f'{Frame(command, headers, body)}{BYTE.NULL}'
        payload = payload.encode('unicode_escape').decode('utf-8')
        return payload.replace('\\\\', '\\')
