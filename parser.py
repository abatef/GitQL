from expression import *


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens: list[Token] = tokens
        self.index: int = 0
        self.precedence: dict[str, int] = {
            "OR": 1,
            "AND": 2,
            "NOT": 3,
            "EQUAL": 4,
            "LESS": 4,
            "GREATER": 4,
            "LEQ": 4,
            "GEQ": 4,
        }

    def advance(self) -> Token:
        token: Token = self.tokens[self.index]
        self.index += 1
        return token

    def current_token(self) -> Token:
        return self.tokens[self.index]

    def get_precedence(self, type: TokenType) -> int:
        return self.precedence[type.value]

    def nud(self, token: Token) -> Expression:
        if token.type == TokenType.LITERAL:
            return ValueExpression(token.value, ExpressionType.STR)
        elif token.type == TokenType.NOT:
            right = self.parse(self.get_precedence(TokenType.NOT))
            return UnaryExpression(token.type, right)
        elif token.type == TokenType.NUMBER:
            return ValueExpression(token.value, ExpressionType.INT)
        elif token.type == TokenType.STRING:
            return ValueExpression(token.value, ExpressionType.STR)
        else:
            raise RuntimeError(f"Unexpected token in nud: {token.type}")

    def led(self, token: Token, left: Expression) -> Expression:
        precedence = self.get_precedence(token.type)
        right: Expression = self.parse(precedence)
        return BinaryExpression(left, token.type, right)

    def parse(self, rbp: int = 0) -> Expression:
        token: Token = self.advance()
        left: Expression = self.nud(token)

        while self.index < len(self.tokens) and rbp < self.get_precedence(
            self.current_token().type
        ):
            token = self.advance()
            left = self.led(token, left)

        return left


# for each row fetch col1 and col2 then put them in the query then execute it
# it it return true include that row else do not include it
query = "col2 = 'col' and row2 = 'row one'"
# query = "col2 = 'something' and col2 = 'something else'"


tokens = tokenize(query)

# for token in tokens:
#     print(token)

parser = Parser(tokens)

left = parser.parse()

print(left.eval())
