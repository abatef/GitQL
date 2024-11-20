import unittest
from tokenizer import Tokenizer, Token, TokenType
from exceptions import TokenizationException


class TestTokenizer(unittest.TestCase):
    def setUp(self):
        self.tokenizer = Tokenizer()
        self.maxDiff = None

    def test_simple_query(self):
        query = "SELECT column1 FROM table1;"
        self.tokenizer.tokenize(query)
        expected_tokens = [
            Token(TokenType.SELECT, 0),
            Token(TokenType.COLUMN_PH, 7, "column1"),
            Token(TokenType.FROM, 15),
            Token(TokenType.SOURCE, 20, "table1"),
            Token(TokenType.SEMI_COLON, 26),
        ]
        self.assertEqual(self.tokenizer.tokens, expected_tokens)

    def test_order_by_combination(self):
        query = "SELECT column1 FROM table1 ORDER BY column2;"
        self.tokenizer.tokenize(query)
        expected_tokens = [
            Token(TokenType.SELECT, 0),
            Token(TokenType.COLUMN_PH, 7, "column1"),
            Token(TokenType.FROM, 15),
            Token(TokenType.SOURCE, 20, "table1"),
            Token(TokenType.ORDER_BY, 27),
            Token(TokenType.COLUMN_PH, 36, "column2"),
            Token(TokenType.SEMI_COLON, 43),
        ]
        self.assertEqual(self.tokenizer.tokens, expected_tokens)

    def test_comparison_operators(self):
        query = "SELECT * FROM table1 WHERE column1 >= 10 AND column2 <= 20;"
        self.tokenizer.tokenize(query)
        expected_tokens = [
            Token(TokenType.SELECT, 0),
            Token(TokenType.ASTERISK, 7),
            Token(TokenType.FROM, 9),
            Token(TokenType.SOURCE, 14, "table1"),
            Token(TokenType.WHERE, 21),
            Token(TokenType.COLUMN_PH, 27, "column1"),
            Token(TokenType.GEQ, 35),
            Token(TokenType.NUMBER, 38, "10"),
            Token(TokenType.AND, 41),
            Token(TokenType.COLUMN_PH, 45, "column2"),
            Token(TokenType.LEQ, 53),
            Token(TokenType.NUMBER, 56, "20"),
            Token(TokenType.SEMI_COLON, 58),
        ]
        self.assertEqual(self.tokenizer.tokens, expected_tokens)

    def test_string_literals(self):
        query = "SELECT column1 FROM table1 WHERE column2 = 'test_string';"
        self.tokenizer.tokenize(query)
        expected_tokens = [
            Token(TokenType.SELECT, 0),
            Token(TokenType.COLUMN_PH, 7, "column1"),
            Token(TokenType.FROM, 15),
            Token(TokenType.SOURCE, 20, "table1"),
            Token(TokenType.WHERE, 27),
            Token(TokenType.COLUMN_PH, 33, "column2"),
            Token(TokenType.EQUAL, 41),
            Token(TokenType.STRING, 44, "test_string"),
            Token(TokenType.SEMI_COLON, 56),
        ]
        self.assertEqual(self.tokenizer.tokens, expected_tokens)

    def test_invalid_string_literal(self):
        query = "SELECT column1 FROM table1 WHERE column2 = 'unterminated_string"
        with self.assertRaises(TokenizationException) as context:
            self.tokenizer.tokenize(query)
        self.assertIn("Unterminated string", str(context.exception))

    def test_order_without_by(self):
        query = "SELECT column1 FROM table1 ORDER column2;"
        with self.assertRaises(TokenizationException) as context:
            self.tokenizer.tokenize(query)
        self.assertIn("Token 'ORDER' must be followed by 'BY'", str(context.exception))

    def test_next_token_and_has_next(self):
        query = "SELECT column1 FROM table1;"
        self.tokenizer.tokenize(query)
        self.assertTrue(self.tokenizer.has_next())
        self.assertEqual(self.tokenizer.next_token(), Token(TokenType.SELECT, 0))
        self.assertTrue(self.tokenizer.has_next())
        self.assertEqual(
            self.tokenizer.next_token(), Token(TokenType.COLUMN_PH, 7, "column1")
        )

    def test_look_ahead(self):
        query = "SELECT column1 FROM table1;"
        self.tokenizer.tokenize(query)
        self.assertEqual(self.tokenizer.look_ahead(0), Token(TokenType.SELECT, 0))
        self.assertEqual(
            self.tokenizer.look_ahead(1), Token(TokenType.COLUMN_PH, 7, "column1")
        )
        with self.assertRaises(IndexError):
            self.tokenizer.look_ahead(10)

    def test_tokenize_empty_query(self):
        with self.assertRaises(TokenizationException) as context:
            self.tokenizer.tokenize("")
        self.assertIn("Unspecified query", str(context.exception))

    def test_trailing_comma(self):
        query = "SELECT column1, column2 FROM table1;"
        self.tokenizer.tokenize(query)
        expected_tokens = [
            Token(TokenType.SELECT, 0),
            Token(TokenType.COLUMN_PH, 7, "column1"),
            Token(TokenType.COLUMN_PH, 16, "column2"),
            Token(TokenType.FROM, 24),
            Token(TokenType.SOURCE, 29, "table1"),
            Token(TokenType.SEMI_COLON, 35),
        ]
        self.assertEqual(self.tokenizer.tokens, expected_tokens)


if __name__ == "__main__":
    unittest.main()
