from expression import *
from tokenizer import *


# pratt parser to parse expressions
class Parser:
    def __init__(self):
        self.tokens: list[Token] = []
        self.index: int = 0
        self.precedence: dict[str, int] = {
            "NUMBER": 0,
            "STRING": 0,
            "OR": 1,
            "AND": 2,
            "NOT": 3,
            "EQUAL": 4,
            "LESS": 4,
            "GREATER": 4,
            "LEQ": 4,
            "GEQ": 4,
        }

    def add_token(self, token: Token):
        self.tokens.append(token)

    def advance(self) -> Token:
        token: Token = self.tokens[self.index]
        self.index += 1
        return token

    def reset(self):
        self.tokens.clear()
        self.index = 0

    def current_token(self) -> Token:
        return self.tokens[self.index]

    def get_precedence(self, type: TokenType) -> int:
        return self.precedence[type.value]

    # for prefix operators (e.g. not) and literals
    def nud(self, token: Token) -> Expression:
        if token.type == TokenType.COLUMN_PH:
            return LiteralExpression(token.value, ExpressionType.CPH)
        elif token.type == TokenType.NOT:
            right = self.parse(self.get_precedence(TokenType.NOT))
            return UnaryExpression(token.type, right)
        elif token.type == TokenType.NUMBER:
            return LiteralExpression(token.value, ExpressionType.INT)
        elif token.type == TokenType.STRING:
            return LiteralExpression(token.value, ExpressionType.STR)
        else:
            raise RuntimeError(f"Unexpected token in nud: {token.type}")

    # for infix operators (and, or, =, +, -, *, /)
    def led(self, token: Token, left: Expression) -> Expression:
        precedence = self.get_precedence(token.type)
        right: Expression = self.parse(precedence)
        return BinaryExpression(left, token.type, right)

    # rbp (Right Binding Power aka. Precedence)
    def parse(self, rbp: int = 0) -> Expression:
        if len(self.tokens) == 0:
            return None
        token: Token = self.advance()
        left: Expression = self.nud(token)

        while self.index < len(self.tokens) and rbp < self.get_precedence(
            self.current_token().type
        ):
            token = self.advance()
            left = self.led(token, left)

        return left


# for each row fetch col1 and col2 then put them in the query then execute it
# if it return true include that row else do not include it
# query = "10 > 12 or 11 >= 11"
# # query = "col2 = 'something' and col2 = 'something else'"


# tokenizer: Tokenizer = Tokenizer(query)
# tokenizer.tokenize()

# tokens: list[Token] = []

# parser: Parser = Parser()

# while tokenizer.has_next():
#     parser.add_token(tokenizer.next_token())


# left = parser.parse()

# print(left.eval())
