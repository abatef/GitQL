from context import Context
from parser import Parser
from tokenizer import Tokenizer, TokenType
from expression import Expression
import time
from beautifultable import BeautifulTable

# Query to process
query = (
    "select * from redis.redis.issues where state = 'open' and user = 'guybe7' limit 3"
)

# Initialize timing and context
start_time = time.time_ns()
tokenizing_start = time.time_ns()

# Tokenizing phase
tokenizer = Tokenizer(query)
tokenizing_end = time.time_ns()

# Initialize parser and context
parser = Parser()
ctx = Context()

# Record tokenizing time
timings = {"Tokenizing Time": tokenizing_end - tokenizing_start}

# Parsing phase
parsing_start = time.time_ns()

while tokenizer.has_next():
    token = tokenizer.current_token()
    if token.type == TokenType.SOURCE:
        source_start = time.time_ns()
        ctx.set_sources(tokenizer.next_token())
        timings["Setting Source Time"] = time.time_ns() - source_start
    elif token.type == TokenType.LIMIT:
        limit_start = time.time_ns()
        tokenizer.next_token()  # Skip LIMIT keyword
        ctx.set_limit(int(tokenizer.next_token().value))
        timings["Setting Limit Time"] = time.time_ns() - limit_start
    elif token.type == TokenType.WHERE:
        where_start = time.time_ns()
        tokenizer.next_token()  # Skip WHERE keyword
        while (
            tokenizer.has_next() and tokenizer.current_token().type != TokenType.LIMIT
        ):
            parser.add_token(tokenizer.next_token())
        timings["Tokens to Parser Time"] = time.time_ns() - where_start
    else:
        tokenizer.next_token()

parsing_end = time.time_ns()
timings["Total Token Parsing Time"] = parsing_end - parsing_start

# Expression parsing phase
expression_start = time.time_ns()
expression = parser.parse()
timings["Expression Parsing Time"] = time.time_ns() - expression_start

# Initial population phase
populate_start = time.time_ns()
ctx.populate()
timings["Initial Population Time"] = time.time_ns() - populate_start

# Evaluation phase
eval_start = time.time_ns()
total_eval_time = 0
eval_count = 0

while not ctx.done():
    eval_cycle_start = time.time_ns()
    can_select = expression.eval(ctx)
    eval_cycle_time = time.time_ns() - eval_cycle_start

    total_eval_time += eval_cycle_time
    eval_count += 1

    if can_select:
        ctx.select_current()
    else:
        ctx.advance()

timings["Total Evaluation Time"] = total_eval_time
timings["Total Run Time"] = time.time_ns() - eval_start
timings["Average Evaluation Time"] = total_eval_time / eval_count if eval_count else 0

# Total execution time
end_time = time.time_ns()
timings["Total Execution Time"] = end_time - start_time

# Print query results
print(ctx.query_results)

# Display timing metrics in a table
table = BeautifulTable()
table.columns.header = ["Stage", "Time (ns)"]

# Add general timing metrics to the table
for stage, time_ns in timings.items():
    table.rows.append([stage, time_ns])

# Display timing results
print("\nTiming Results:")
print(table)
