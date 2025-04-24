from streaming_json_parser.StreamingJsonParser import StreamingJsonParser
import json
import pytest

def test_partial_key():
    parser = StreamingJsonParser()
    parser.consume('{"test": "hello", "worl')
    result = parser.get()
    assert(str(result) == "{'test': 'hello'}")

def test_partial_value():
    parser = StreamingJsonParser()
    parser.consume('{"test": "hello", "country": "Switzerl')
    result = parser.get()
    assert(json.dumps(result) == '{"test": "hello", "country": "Switzerl"}')
    parser.consume('and"')
    result = parser.get()
    assert(json.dumps(result) == '{"test": "hello", "country": "Switzerland"}')

def test_partial_object():
    parser = StreamingJsonParser()
    parser.consume('{"user": {')
    parser.consume('"id": 1041, "name": "Alice",')
    parser.consume('"profile": { "age": 29, "bio": "Cybersecurity')
    result = parser.get()
    assert(json.dumps(result) == '{"user": {"id": 1041, "name": "Alice", "profile": {"age": 29, "bio": "Cybersecurity"}}}')

def test_complete_object():
    parser = StreamingJsonParser()
    parser.consume('{"user": {')
    parser.consume('"id": 1041, "name": "Alice",')
    parser.consume('"profile": { "age": 29, "bio": "Cybersecurity')
    parser.consume(' enthusiast",')
    parser.consume('"location": { "city": "Zurich", "zip": 8')
    parser.consume('001 }')
    parser.consume('} } ,')
    parser.consume('"sett')
    parser.consume('ings": { "theme": "dark",')
    parser.consume('"notifications": { "email": true, "sms": false,')
    parser.consume('"frequency": { "daily": 1, "weekly": 0 }')
    parser.consume('} } ,')
    parser.consume('"stats": { "logins": 145,')
    parser.consume('"lastLogin": { "day": "Monday", "hour": 14 }')
    parser.consume('} }')
    result = parser.get()
    assert(json.dumps(result) == '{"user": {"id": 1041, "name": "Alice", "profile": {"age": 29, "bio": "Cybersecurity enthusiast", "location": {"city": "Zurich", "zip": 8001}}}, "settings": {"theme": "dark", "notifications": {"email": true, "sms": false, "frequency": {"daily": 1, "weekly": 0}}}, "stats": {"logins": 145, "lastLogin": {"day": "Monday", "hour": 14}}}')

def test_syntax_error_bracket():
    with pytest.raises(SyntaxError):
        parser = StreamingJsonParser()
        parser.consume('{"test": "hello"} }')