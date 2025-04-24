from enum import Enum

# Define possible parsing states during JSON stream parsing
class ParsingState(Enum):
    NONE = 0,           # Parsing has not begun yet
    KEY_BEGIN = 1       # Beginning of a key
    KEY = 2,            # Reading key characters
    COLON = 4,          # Expecting a colon after key
    VALUE_BEGIN = 5,    # Beginning of a value
    VALUE_STRING = 6,   # Reading a quoted string value
    VALUE = 7,          # Reading a non-string value (e.g., number, true/false, null)
    END_DELIMITER = 10  # After completing a key-value pair

# Define types of values that can be parsed
class ValueType(Enum):
    INVALID = 1, # Unrecognized value
    NUMBER = 2,  # Numeric value
    BOOL = 3,    # Boolean value
    NULL = 4,    # Null value

class StreamingJsonParser:
    def __init__(self):
        self.parsed = {}                # Root object to store parsed JSON
        self.open_brackets = 0          # Count of '{' encountered
        self.closed_brackets = 0        # Count of '}' encountered
        self.current_key = ""           # Key currently being parsed
        self.current_value = None       # Value currently being parsed
        self.current_path = []          # Current path in the nested JSON
        self.state = ParsingState.NONE  # Initial parsing state

    # Helper method to retrieve the object at the current parsing path
    def __get_current_obj(self):
        obj = self.parsed
        for node in self.current_path:
            obj = obj[node]
        return obj

    # Check if the current key already exists in the current object
    def __is_key_defined(self):
        obj = self.__get_current_obj()
        return self.current_key in obj

    # Set the value for the current key in the current object
    def __set_value(self, value):
        obj = self.__get_current_obj()
        obj[self.current_key] = value

    # Determine the type of the current value
    def __get_value_type(self):
        if self.current_value in "true" or self.current_value in "false":
            return ValueType.BOOL
        elif self.current_value.isnumeric():
            return ValueType.NUMBER
        elif self.current_value in "null":
            return ValueType.NULL
        else:
            return ValueType.INVALID
            
    # Cast the current value to its correct Python type
    def __get_casted_value(self):
        match self.__get_value_type():
            case ValueType.NUMBER:
                return int(self.current_value)
            case ValueType.BOOL:
                return self.current_value == "true"
            case ValueType.NULL:
                return None
            case _:
                raise SyntaxError(f"Syntax error: Invalid identifier {self.current_value}")

    # Consume a buffer string, character by character, and parse it into the internal data structure
    def consume(self, buffer: str):
        for c in buffer:
            if c == '"':
                # Handle transitions around string delimiters
                match self.state:
                    case ParsingState.KEY_BEGIN:
                        self.state = ParsingState.KEY
                        self.current_key = ""
                    case ParsingState.VALUE_BEGIN:
                        self.state = ParsingState.VALUE_STRING
                        self.current_value = ""
                    case ParsingState.KEY:
                        self.state = ParsingState.COLON
                        if self.__is_key_defined():
                            raise SyntaxError("Syntax error: key already defined")
                        self.__set_value(None)
                    case ParsingState.VALUE_STRING:
                        self.state = ParsingState.END_DELIMITER
                        self.__set_value(self.current_value)
                    case _:
                        raise SyntaxError("Syntax error: unexpected '\"'")
            if c == ':':
                # Transition to expecting a value after a key
                match self.state:
                    case ParsingState.COLON:
                        self.state = ParsingState.VALUE_BEGIN
                    case _:
                        raise SyntaxError("Syntax error: unexpected ':'")
            if c == ',':
                # End of a key-value pair; prepare for next key
                match self.state:
                    case ParsingState.END_DELIMITER:
                        self.state = ParsingState.KEY_BEGIN
                    case ParsingState.VALUE:
                        self.state = ParsingState.KEY_BEGIN
                        self.__set_value(self.__get_casted_value())
                    case _:
                        raise SyntaxError("Syntax error: unexpected ','")
            elif c.isalnum():
                # Handle alphanumeric characters inside keys or values
                match self.state:
                    case ParsingState.KEY:
                        self.current_key += c
                    case ParsingState.VALUE_STRING | ParsingState.VALUE:
                        self.current_value += c
                    case ParsingState.VALUE_BEGIN:
                        self.state = ParsingState.VALUE
                        self.current_value = c
                    case _:
                        raise SyntaxError(f"Syntax error: unexpected character {c}")
            elif c == ' ':
                # Handle space characters inside keys or values
                match self.state:
                    case ParsingState.VALUE_STRING:
                        self.current_value += c
                    case ParsingState.VALUE:
                        self.state = ParsingState.END_DELIMITER
                        self.__set_value(self.__get_casted_value())
                    case ParsingState.KEY:
                        self.state = ParsingState.COLON
                    case _:
                        continue
            if c == '{':
                # Start of a new object
                match self.state:
                    case ParsingState.VALUE_BEGIN | ParsingState.NONE:
                        self.open_brackets += 1
                        if self.state == ParsingState.VALUE_BEGIN:
                            self.__set_value({})
                            self.current_path.append(self.current_key)
                        self.state = ParsingState.KEY_BEGIN
                    case _:
                        raise SyntaxError("Syntax error: unexpected '{'")
            if c == '}':
                # End of an object
                match self.state:
                    case ParsingState.VALUE | ParsingState.END_DELIMITER:
                        self.closed_brackets += 1
                        if self.open_brackets > self.closed_brackets:
                            if self.state == ParsingState.VALUE:
                                self.__set_value(self.__get_casted_value())
                            self.current_path.pop()
                        if self.open_brackets < self.closed_brackets:
                            raise SyntaxError("Syntax error: depth mismatch")
                        self.state = ParsingState.END_DELIMITER
                    case _:
                        raise SyntaxError("Syntax error: unexpected '}'")

    # Finalize parsing and return the parsed object
    def get(self):
        # Finalize any uncommitted value
        if self.state == ParsingState.VALUE_STRING:
            self.__set_value(self.current_value)
        if self.state == ParsingState.VALUE:
            self.__set_value(self.__get_casted_value())
        return self.parsed
