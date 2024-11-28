from context import Context
from parser import Parser
from tokenizer import Tokenizer, TokenType
from expression import Expression
import time
from beautifultable import BeautifulTable


class GitQL:
    def __init__(self):
        self.tokenizer: Tokenizer = Tokenizer()
        self.parser: Parser = Parser()
        self.ctx: Context = Context()

    def initialize(self, query: str):
        self.tokenizer.tokenize(query)
        while self.tokenizer.has_next():
            token = self.tokenizer.current_token()
            if token.type == TokenType.SOURCE:
                self.ctx.set_sources(self.tokenizer.next_token())
            elif token.type == TokenType.LIMIT:
                self.tokenizer.next_token()  # Skip LIMIT keyword
                self.ctx.set_limit(int(self.tokenizer.next_token().value))
            elif token.type == TokenType.WHERE:
                self.tokenizer.next_token()  # Skip WHERE keyword
                while (
                    self.tokenizer.has_next()
                    and self.tokenizer.current_token().type != TokenType.LIMIT
                ):
                    self.parser.add_token(self.tokenizer.next_token())
            else:
                self.tokenizer.next_token()

    def reset(self):
        self.tokenizer.reset()
        self.parser.reset()
        self.ctx = Context()

    def print(self, time):
        table: BeautifulTable = BeautifulTable(maxwidth=4000)
        if self.ctx.query_results:
            table.columns.header = self.ctx.query_results[0].keys()

            for result in self.ctx.query_results:
                table.rows.append(result.values())

        print("\nQuery Results:")
        print(table)
        print(f"\nTotal Rows: {len(table.rows)}")
        print(f"Total Time: {time}s")

    def run(self):
        while True:
            query: str = input("GitQL> ")
            if len(query) == 0:
                break

            s_time = time.time()
            self.initialize(query)
            expr: Expression = self.parser.parse()
            self.ctx.populate()
            while not self.ctx.done():
                can_select: bool = expr.eval(self.ctx)
                if can_select:
                    self.ctx.select_current()
                else:
                    self.ctx.advance()

            self.print(time.time() - s_time)
            self.reset()


gQL: GitQL = GitQL()

gQL.run()
