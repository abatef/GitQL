import time
import logging
from beautifultable import BeautifulTable
from context import Context
from parser import Parser
from tokenizer import Tokenizer, TokenType
from expression import Expression
from pygments.lexers.sql import SqlLexer
from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from pygments.styles import get_style_by_name
from prompt_toolkit.styles.pygments import style_from_pygments_cls


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GitQL:
    def __init__(self):
        self.tokenizer: Tokenizer = Tokenizer()
        self.parser: Parser = Parser()
        self.ctx: Context = Context()
        self.session: PromptSession = PromptSession(
            lexer=PygmentsLexer(SqlLexer),
            style=style_from_pygments_cls(get_style_by_name("manni")),
        )

        logger.info("GitQL initialized.")

    def initialize(self, query: str):
        logger.debug(f"Initializing with query: {query}")
        self.tokenizer.tokenize(query)
        while self.tokenizer.has_next():
            token = self.tokenizer.current_token()
            logger.debug(f"Current token: {token}")
            if token.type == TokenType.SELECT:
                self.tokenizer.next_token()
                if self.tokenizer.current_token().type == TokenType.ASTERISK:
                    self.tokenizer.next_token()
                while self.tokenizer.current_token().type == TokenType.COLUMN_PH:
                    self.ctx.add_selected_column(self.tokenizer.next_token().value)
            elif token.type == TokenType.SOURCE:
                logger.info(f"Set source: {self.tokenizer.current_token().value}")
                self.ctx.set_sources(self.tokenizer.next_token())
            elif token.type == TokenType.LIMIT:
                self.tokenizer.next_token()  # Skip LIMIT keyword
                limit_value = int(self.tokenizer.next_token().value)
                self.ctx.set_limit(limit_value)
            elif token.type == TokenType.WHERE:
                self.tokenizer.next_token()  # Skip WHERE keyword
                logger.debug("Processing WHERE clause.")
                while (
                    self.tokenizer.has_next()
                    and self.tokenizer.current_token().type != TokenType.LIMIT
                ):
                    self.parser.add_token(self.tokenizer.next_token())
            else:
                self.tokenizer.next_token()

    def reset(self):
        logger.info("Resetting GitQL state.")
        self.tokenizer.reset()
        self.parser.reset()
        self.ctx = Context()

    def print(self, time):
        logger.debug("Printing query results.")
        table: BeautifulTable = BeautifulTable(maxwidth=200)
        if len(self.ctx.selected_columns) > 0:
            table.columns.header = self.ctx.selected_columns
            for result in self.ctx.query_results:
                row: list = []
                for col in self.ctx.selected_columns:
                    row.append(result[col])
                table.rows.append(row)
        elif self.ctx.query_results:
            table.columns.header = self.ctx.query_results[0].keys()
            for result in self.ctx.query_results:
                table.rows.append(result.values())

        print("\nQuery Results:")
        print(table)
        print(f"\nTotal Rows Fetched: {self.ctx.current_read}")
        print(f"\nTotal Rows: {len(table.rows)}")
        print(f"Total Time: {time}s")

        logger.info(f"Query executed in {time}s with {len(table.rows)} rows.")

    def run(self):
        logger.info("GitQL execution started.")
        while True:
            try:
                query: str = self.session.prompt("GitQL> ")
                if len(query) == 0:
                    logger.info("Exiting GitQL.")
                    break

                s_time = time.time()
                logger.debug("Processing query.")
                self.initialize(query)
                expr: Expression = self.parser.parse()
                self.ctx.populate()
                while not self.ctx.done():
                    can_select: bool = expr.eval(self.ctx) if expr != None else True
                    if can_select:
                        self.ctx.select_current()
                    else:
                        self.ctx.advance()

                self.print(time.time() - s_time)
                self.reset()
            except (KeyboardInterrupt, EOFError):
                logger.info("Exiting GitQL.")
                break


# Start the GitQL instance
gQL: GitQL = GitQL()

gQL.run()
