from enum import Enum


class TokenType(Enum):
    SELECT = "SELECT"
    FROM = "FROM"
    WHERE = "WHERE"
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
    GEQ = "GEQ"
    LEQ = "LEQ"
    ASTRIC = "ASTRIC"
    PLUS = "PLUS"
    MINUS = "MINUS"
    STRING = "STRING"
    NUMBER = "NUMBER"
    LITERAL = "LITERAL"
    SOURCE = "SOURCE"


class Token:
    def __init__(self, type: TokenType, value, index: int):
        self.type = type
        self.value: int | str = value
        self.index = index

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value}, index={self.index})"


class Tokenizer:
    def __init__(self):
        self.tokens: list[Token] = []
        self.index: int = 0

    def tokenize(self, query: str) -> list[Token]:
        pass

    def next_token(self):
        pass


# TODO move it to class modify the tokenize function to handle strings like 'this string'
def tokenize(query):
    rtokens = []
    tokens = query.split(" ")
    for i in range(len(tokens)):
        match tokens[i].casefold():
            case "select":
                rtokens.append(Token(TokenType.SELECT, "select", i))
            case "from":
                rtokens.append(Token(TokenType.FROM, "from", i))
            case "where":
                rtokens.append(Token(TokenType.WHERE, "where", i))
            case "order":
                if i + 1 < len(tokens) and tokens[i + 1].casefold() == "by":
                    rtokens.append(Token(TokenType.ORDER_BY, "order by", i))
                else:
                    raise RuntimeError(f"did you mean 'order by' ? at {i}")
            case "limit":
                rtokens.append(Token(TokenType.LIMIT, "limit", i))
            case "asc":
                rtokens.append(Token(TokenType.ASC, "asc", i))
            case "desc":
                rtokens.append(Token(TokenType.DESC, "desc", i))
            case "and":
                rtokens.append(Token(TokenType.AND, "and", i))
            case "or":
                rtokens.append(Token(TokenType.OR, "or", i))
            case "not":
                rtokens.append(Token(TokenType.NOT, "not", i))
            case "<":
                rtokens.append(Token(TokenType.LESS, "<", i))
            case ">":
                rtokens.append(Token(TokenType.GREATER, ">", i))
            case "=":
                rtokens.append(Token(TokenType.EQUAL, "=", i))
            case "<=":
                rtokens.append(Token(TokenType.LEQ, "<=", i))
            case ">=":
                rtokens.append(Token(TokenType.GEQ, ">=", i))
            case "*":
                rtokens.append(Token(TokenType.ASTRIC, "*", i))
            case _:
                if tokens[i].startswith("'") and tokens[i].endswith("'"):
                    rtokens.append(Token(TokenType.STRING, tokens[i][1:-1], i))
                elif tokens[i].isdigit():
                    rtokens.append(Token(TokenType.NUMBER, int(tokens[i]), i))
                elif "." in tokens[i]:
                    rtokens.append(Token(TokenType.SOURCE, tokens[i], i))
                else:
                    if tokens[i][-1] == ",":
                        rtokens.append(Token(TokenType.LITERAL, tokens[i][:-1], i))
                    else:
                        rtokens.append(Token(TokenType.LITERAL, tokens[i], i))

    return rtokens


# query = "select title, label, user from repo.user.issues where status = 'merged' and value = 3 order by value desc limit 5"

# tokens = tokenize(query)

# for token in tokens:
#     print(token)
