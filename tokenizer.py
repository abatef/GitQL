from enum import Enum
from exceptions import TokenizationException


# Enum representing the types of tokens the tokenizer can recognize
class TokenType(Enum):
    SELECT = "SELECT"
    FROM = "FROM"
    WHERE = "WHERE"
    ORDER = "ORDER"
    BY = "BY"
    ORDER_BY = "ORDER BY"
    LIMIT = "LIMIT"
    ASC = "ASC"
    DESC = "DESC"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    GREATER = "GREATER"
    LESS = "LESS"
    EQUAL = "EQUAL"
    GEQ = "GEQ"  # Greater than or equal to
    LEQ = "LEQ"  # Less than or equal to
    PLUS = "PLUS"
    MINUS = "MINUS"
    ASTERISK = "ASTERISK"  # Multiplication operator (*)
    DIV = "DIV"  # Division operator (/)
    STRING = "STRING"  # String literal
    NUMBER = "NUMBER"  # Numeric literal
    COLUMN_PH = "COLUMN PH"  # Column placeholder (e.g., identifiers like column names)
    SOURCE = "SOURCE"  # Source name (e.g., table or database)
    SEMI_COLON = "SEMI_COLON"  # Semicolon (end of query)
    UNSPEC = ""  # Unspecified type for initial token processing


# Token class representing a unit of the query with type, position, and optional value
class Token:
    def __init__(self, type: TokenType, index: int, value: str | int | None = None):
        self.type: TokenType = type  # Type of the token
        self.index: int = index  # Position of the token in the query
        self.value: int | str | None = value  # Value of the token (if applicable)

    # Equality operator (==)
    def __eq__(self, other):
        if not isinstance(other, Token):
            return NotImplemented
        return (
            self.type == other.type
            and self.value == other.value
            and self.index == other.index
        )

    # Inequality operator (!=)
    def __ne__(self, other):
        if not isinstance(other, Token):
            return NotImplemented
        return not self.__eq__(other)

    def __repr__(self):
        if self.value:
            return f"Token(type={self.type}, value={self.value}, index={self.index})"
        return f"Token(type={self.type}, index={self.index})"


# Tokenizer class for breaking down a query into tokens
class Tokenizer:
    def __init__(self, query: str | None = None):
        self.tokens: list[Token] = []  # List of generated tokens
        self.index: int = 0  # Current position in the token list
        self.query: str | None = query  # SQL-like query to be tokenized

    # Create a single atomic token from a string and add it to the token list
    def _make_atomic_token(
        self, token: str | int, st_idx: int, type: TokenType = TokenType.UNSPEC
    ):
        if len(token) == 0:
            return  # Ignore empty tokens
        if type == TokenType.UNSPEC:
            # Case-insensitive matching for keywords and symbols
            match token.casefold():
                case "select":
                    self.tokens.append(Token(TokenType.SELECT, st_idx))
                case "from":
                    self.tokens.append(Token(TokenType.FROM, st_idx))
                case "where":
                    self.tokens.append(Token(TokenType.WHERE, st_idx))
                case "order":
                    self.tokens.append(Token(TokenType.ORDER, st_idx))
                case "by":
                    self.tokens.append(Token(TokenType.BY, st_idx))
                case "limit":
                    self.tokens.append(Token(TokenType.LIMIT, st_idx))
                case "asc":
                    self.tokens.append(Token(TokenType.ASC, st_idx))
                case "desc":
                    self.tokens.append(Token(TokenType.DESC, st_idx))
                case "and":
                    self.tokens.append(Token(TokenType.AND, st_idx))
                case "or":
                    self.tokens.append(Token(TokenType.OR, st_idx))
                case "not":
                    self.tokens.append(Token(TokenType.NOT, st_idx))
                case ">":
                    self.tokens.append(Token(TokenType.GREATER, st_idx))
                case "<":
                    self.tokens.append(Token(TokenType.LESS, st_idx))
                case "=":
                    self.tokens.append(Token(TokenType.EQUAL, st_idx))
                case "+":
                    self.tokens.append(Token(TokenType.PLUS, st_idx))
                case "-":
                    self.tokens.append(Token(TokenType.MINUS, st_idx))
                case "/":
                    self.tokens.append(Token(TokenType.DIV, st_idx))
                case "*":
                    self.tokens.append(Token(TokenType.ASTERISK, st_idx))
                case ";":
                    self.tokens.append(Token(TokenType.SEMI_COLON, st_idx))
                case _:
                    # Handle column placeholders and trailing commas
                    if token.endswith(","):
                        self.tokens.append(
                            Token(TokenType.COLUMN_PH, st_idx, value=token[:-1])
                        )
                    else:
                        self.tokens.append(
                            Token(TokenType.COLUMN_PH, st_idx, value=token)
                        )
        elif type == TokenType.STRING or type == TokenType.NUMBER:
            # Add a token with a specified type and value
            self.tokens.append(Token(type=type, index=st_idx, value=token))
        else:
            # Raise an exception for unrecognized tokens
            raise TokenizationException(f"Unrecognized token at {st_idx}")

    # Combine atomic tokens into meaningful composite tokens
    def _combine_atomics(self):
        tokens: list[Token] = []
        sz: int = len(self.tokens)
        i: int = 0
        while i < sz:
            if self.tokens[i].type == TokenType.ORDER:
                if i + 1 < sz and self.tokens[i + 1].type == TokenType.BY:
                    # Combine 'ORDER BY' into a single token
                    tokens.append(Token(TokenType.ORDER_BY, self.tokens[i].index))
                    i += 2
                    continue
                else:
                    raise TokenizationException(
                        f"Token 'ORDER' must be followed by 'BY' at {self.tokens[i].index}"
                    )
            elif self.tokens[i].type == TokenType.GREATER:
                if i + 1 < sz and self.tokens[i + 1].type == TokenType.EQUAL:
                    # Combine '>=' into a single token
                    tokens.append(Token(TokenType.GEQ, self.tokens[i].index))
                    i += 2
                    continue
                else:
                    tokens.append(self.tokens[i])
            elif self.tokens[i].type == TokenType.LESS:
                if i + 1 < sz and self.tokens[i + 1].type == TokenType.EQUAL:
                    # Combine '<=' into a single token
                    tokens.append(Token(TokenType.LEQ, self.tokens[i].index))
                    i += 2
                    continue
                else:
                    tokens.append(self.tokens[i])
            elif (
                i - 1 >= 0
                and self.tokens[i].type == TokenType.COLUMN_PH
                and self.tokens[i - 1].type == TokenType.FROM
            ):
                # Treat column placeholders after 'FROM' as sources
                self.tokens[i].type = TokenType.SOURCE
                tokens.append(self.tokens[i])
            else:
                tokens.append(self.tokens[i])
            i += 1

        self.tokens.clear()
        self.tokens = tokens.copy()

    # Tokenize a given query string into a list of tokens
    def tokenize(self, query: str | None = None) -> None:
        token: str = ""
        i: int = 0
        if self.query == None and query == None or (query != None and len(query) == 0):
            raise TokenizationException("Unspecified query")
        if query == None:
            query = self.query
        st_index: int = 0
        while i <= len(query):
            if (
                i == len(query)
                or query[i] == " "
                or query[i] == "\n"
                or query[i] == ";"
            ):
                # Finalize the current token
                if token.isdigit():
                    self._make_atomic_token(token, st_index, TokenType.NUMBER)
                elif token == ">=" or token == "<=":
                    self._make_atomic_token(token[0], st_index)
                    self._make_atomic_token(token[1], st_index)
                else:
                    self._make_atomic_token(token, st_index)

                # Add semicolon as a separate token
                if i < len(query) and query[i] == ";":
                    self._make_atomic_token(query[i], i)
                token = ""
                i += 1
                st_index = i
                continue
            if query[i] == "'":
                # Handle string literals enclosed in single quotes
                i += 1
                st_idx = i
                while i < len(query) and query[i] != "'":
                    token += query[i]
                    i += 1
                if i == len(query) or query[i] != "'":
                    raise TokenizationException(f"Unterminated string at {st_idx}")
                self._make_atomic_token(token, st_idx, TokenType.STRING)
                token = ""
            else:
                token += query[i]
            i += 1
        self._combine_atomics()

    # Retrieve the next token from the token list
    def next_token(self) -> Token | None:
        if self.index < len(self.tokens):
            rt: Token = self.tokens[self.index]
            self.index += 1
            return rt
        raise IndexError("No tokens left")

    # Check if there are more tokens to process
    def has_next(self) -> bool:
        return self.index < len(self.tokens)

    # Look ahead at a specific position in the token list
    def look_ahead(self, offset: int) -> Token:
        if self.index + offset < len(self.tokens):
            return self.tokens[self.index + offset]
        raise IndexError(f"No tokens left after lookahead index {self.index + offset}")


# query = "select title, label, user from repo.user.issues where status = 'merged' and value >= 3 order by value desc limit 5;"
# # print(len(query))

# tokenizer: Tokenizer = Tokenizer(query)

# tokenizer.tokenize()

# while tokenizer.has_next():
#     print(tokenizer.next_token())
