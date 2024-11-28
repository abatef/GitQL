from enum import Enum
from tokenizer import *
from context import Context


class ExpressionType(Enum):
    STR = 0
    INT = 1
    CPH = 2


class Expression:
    def __init__(self, type: ExpressionType):
        self.type: ExpressionType = type
        pass

    def eval(self, ctx: Context):
        pass


class LiteralExpression(Expression):
    def __init__(self, value: str | int, type: ExpressionType):
        self.value = value
        self.type = type

    def eval(self, ctx: Context):
        if self.type != ExpressionType.CPH:
            return self.value
        return ctx.get_value(self.value)


class UnaryExpression(Expression):
    def __init__(self, operator: TokenType, right: Expression):
        self.operator: TokenType = operator
        self.right: Expression = right

    def eval(self, ctx: Context):
        if self.operator == TokenType.NOT:
            return not self.right.eval(ctx)


class BinaryExpression(Expression):
    def __init__(self, left: Expression, operator: TokenType, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

    def eval(self, ctx: Context):
        l: int = self.left.eval(ctx)
        r: int = self.right.eval(ctx)
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
            case TokenType.ASTERISK:
                return l * r
            case TokenType.OR:
                return l or r
            case TokenType.AND:
                return l and r
            case _:
                return None
