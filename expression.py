from enum import Enum
from tokenizer import TokenType, Token, tokenize


class ExpressionType(Enum):
    STR = 0
    INT = 1


class Expression:
    def __init__(self, type: ExpressionType):
        self.type: ExpressionType = type
        pass

    def eval(self):
        pass


class ValueExpression(Expression):
    def __init__(self, value: str | int, type: ExpressionType):
        self.value = value
        self.type = type

    def eval(self):
        return self.value


class UnaryExpression(Expression):
    def __init__(self, operator: TokenType, right: Expression):
        self.operator: TokenType = operator
        self.right: Expression = right

    def eval(self):
        if self.operator == TokenType.NOT:
            return not self.right.eval()


class BinaryExpression(Expression):
    def __init__(self, left: Expression, operator: TokenType, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

    def eval(self):
        l: int = self.left.eval()
        r: int = self.right.eval()
        if type(l) != type(r):
            raise RuntimeError("both operands must be of type int")
        match self.operator:
            case TokenType.GREATER:
                return l > r
            case TokenType.LESS:
                return l < r
            case TokenType.GEQ:
                return l >= r
            case TokenType.LEQ:
                return l <= r
            case TokenType.EQUAL:
                return l == r
            case TokenType.PLUS:
                return l + r
            case TokenType.MINUS:
                return l - r
            case TokenType.ASTRIC:
                return l * r
            case TokenType.OR:
                return l or r
            case TokenType.AND:
                return l and r
            case _:
                return None
