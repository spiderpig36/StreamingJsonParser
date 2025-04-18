# StreamingJsonParser

`StreamingJsonParser` is a **lightweight, character-by-character JSON object parser** designed to process a stream of JSON data in **real-time**.  
It reads and builds JSON objects without requiring the full document to be loaded into memory first — ideal for constrained environments or streaming use cases.

---

## Features

- **Streaming**: Parses JSON incrementally, character by character.
- **Basic JSON support**:
  - Objects with string keys and primitive values (strings, numbers, booleans, `null`).
  - Nested objects (arbitrary depth).
- **Type detection**: Automatically converts values to appropriate Python types (`int`, `bool`, `None`).
- **Error handling**: Raises exceptions when unexpected characters or structure inconsistencies (like mismatched brackets) are encountered.
- **Stateful design**: Maintains internal parsing state to allow incremental feeding of input (`consume(buffer: str)`).

---

## Example Usage

```python
parser = StreamingJsonParser()

# Simulating a stream of incoming data
json_stream = '{"name":"ChatGPT","active":true,"details":{"version":4,"language":"Python"}}'

for chunk in json_stream:
    parser.consume(chunk)

result = parser.get()
print(result)
```

**Output:**
```python
{
    'name': 'ChatGPT',
    'active': True,
    'details': {
        'version': 4,
        'language': 'Python'
    }
}
```

---

## Limitations

While simple and effective, `StreamingJsonParser` has some **known limitations**:

- **No array support**: Arrays (`[...]`) are not supported — only JSON objects (`{...}`) can be parsed.
- **No whitespace skipping**: Whitespace between tokens is not automatically ignored; the input must be tightly formatted.
- **No escape character handling**: Strings cannot currently contain escaped quotes (`\"`) or other escape sequences.
- **Only simple values**: Only strings (quoted), numbers, booleans (`true`/`false`), and `null` are supported as values.
- **Single chunk expectation for keys/values**: If a key or value is split across multiple `consume` calls (in extreme streaming scenarios), the parser could fail.
- **Strict format**: Unexpected characters or improperly formatted JSON will immediately raise an exception.

---
