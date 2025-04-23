import json

class StreamingJsonParser:
    def __init__(self):
        self.stack = [{}]
        self.key_stack = []
        self.buffer = ""
        self.state = "idle"
        self.in_string = False
        self.escape = False
        self.temp_key = ""
        self.current_key = None
        self.current_value = ""

    def _commit_value(self, value):
        if self.current_key is not None:
            self.stack[-1][self.current_key] = value
            self.current_key = None

    def consume(self, buffer: str):
        self.buffer += buffer
        i = 0
        while i < len(self.buffer):
            char = self.buffer[i]

            if self.state == "idle":
                if char == '{':
                    self.stack = [{}]
                    self.key_stack = []
                    self.state = "key"
                    i += 1
                    continue
                elif char.isspace():
                    i += 1
                    continue
                else:
                    break

            elif self.state == "key":
                if char.isspace() and not self.in_string:
                    i += 1
                    continue
                if char == '"':
                    if not self.in_string:
                        self.in_string = True
                        self.temp_key = ""
                    elif not self.escape:
                        self.in_string = False
                        self.current_key = self.temp_key
                        self.state = "colon"
                    else:
                        self.temp_key += char
                    i += 1
                    continue
                elif self.in_string:
                    if char == '\\' and not self.escape:
                        self.escape = True
                    else:
                        self.temp_key += char
                        self.escape = False
                    i += 1
                    continue
                else:
                    break

            elif self.state == "colon":
                if char.isspace():
                    i += 1
                    continue
                if char == ':':
                    self.state = "value"
                    i += 1
                    continue
                else:
                    break

            elif self.state == "value":
                if char.isspace():
                    i += 1
                    continue
                if char == '"':
                    self.in_string = True
                    self.current_value = ""
                    self.state = "string"
                    i += 1
                    continue
                elif char == '{':
                    self.stack.append({})
                    self.key_stack.append(self.current_key)
                    self.current_key = None
                    self.state = "key"
                    i += 1
                    continue
                else:
                    break

            elif self.state == "string":
                if char == '"' and not self.escape:
                    self.in_string = False
                    self._commit_value(self.current_value)
                    self.current_value = ""
                    self.state = "key_or_end"
                    i += 1
                    continue
                elif char == '\\' and not self.escape:
                    self.escape = True
                else:
                    self.current_value += char
                    self.escape = False
                i += 1
                continue

            elif self.state == "key_or_end":
                if char.isspace():
                    i += 1
                    continue
                if char == ',':
                    self.state = "key"
                    i += 1
                    continue
                elif char == '}':
                    finished = self.stack.pop()
                    if self.key_stack:
                        self.current_key = self.key_stack.pop()
                        self._commit_value(finished)
                        self.state = "key_or_end"
                    else:
                        self.stack = [finished]
                        self.state = "complete"
                    i += 1
                    continue
                else:
                    break

            elif self.state == "complete":
                if char.isspace():
                    i += 1
                else:
                    break

        self.buffer = self.buffer[i:]

    def get(self):
        def merge_stacks(stack, keys):
            result = stack[0].copy()
            current = result
            for depth, key in enumerate(keys):
                if key not in current or not isinstance(current[key], dict):
                    current[key] = {}
                current = current[key]
                current.update(stack[depth + 1])
            return result

        result = merge_stacks(self.stack, self.key_stack)

        if self.state == "string" and self.current_key is not None:
            target = result
            for k in self.key_stack:
                target = target.setdefault(k, {})
            target[self.current_key] = self.current_value

        return result


# Example test cases
if __name__ == '__main__':
    def test_streaming_json_parser():
        parser = StreamingJsonParser()
        parser.consume('{"foo": "bar"}')
        assert parser.get() == {"foo": "bar"}

    def test_chunked_streaming_json_parser():
        parser = StreamingJsonParser()
        parser.consume('{"foo":')
        parser.consume('"bar"}')
        assert parser.get() == {"foo": "bar"}

    def test_partial_streaming_json_parser():
        parser = StreamingJsonParser()
        parser.consume('{"foo": "bar')
        assert parser.get() == {"foo": "bar"}

    def test_partial_key():
        parser = StreamingJsonParser()
        parser.consume('{"test": "hello", "worl')
        result = parser.get()
        assert result == {"test": "hello"}

    def test_complete_then_partial():
        parser = StreamingJsonParser()
        parser.consume('{"a": "b"}')
        parser.consume(', "incomplete')
        result = parser.get()
        assert result == {"a": "b"}

    def test_whitespace_handling():
        parser = StreamingJsonParser()
        parser.consume('{  "name"  :    "value"   }')
        assert parser.get() == {"name": "value"}

    def test_partial_object():
        parser = StreamingJsonParser()
        parser.consume('{"user": {')
        parser.consume('"id": "1041", "name": "Alice",')
        parser.consume('"profile": { "age": "29", "bio": "Cybersecurity')
        result = parser.get()
        expected = {
            "user": {
                "id": "1041",
                "name": "Alice",
                "profile": {
                    "age": "29",
                    "bio": "Cybersecurity"
                }
            }
        }
        assert result == expected

    test_streaming_json_parser()
    test_chunked_streaming_json_parser()
    test_partial_streaming_json_parser()
    test_partial_key()
    test_complete_then_partial()
    test_whitespace_handling()
    test_partial_object()
    print("All tests passed.")
