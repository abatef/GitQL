from tokenizer import TokenType, Token, tokenize
from enum import Enum


class Select:
    def __init__(self):
        self.columns: list[str] = []

    def add_column(self, column: str):
        self.columns.append(column)

    def __repr__(self):
        return f"select(columns={self.columns})"


class SourceType(Enum):
    USER = "user"
    REPO = "repo"


class From:
    def __init__(
        self,
        user: str,
        repo: str = None,
        source: str = None,
        type: SourceType = None,
    ):
        self.user: str = user
        self.repo: str = repo
        self.source: str = source
        self.type: SourceType = type

    def __repr__(self):
        if self.type == SourceType.REPO and self.repo:
            return f"from(user={self.user}, repo={self.repo}, source={self.source})"
        return f"from(user={self.user}, source={self.source})"


inner_entities = {
    "issues": [
        "label",
        "status",
        "title",
        "author",
        "assignee",
        "description",
        "created_at",
        "updated_at",
        "milestone",
    ],
    "pull request": [
        "status",
        "author",
        "assignee",
        "title",
        "created_at",
        "updated_at",
        "merged_at",
        "milestone",
    ],
    "user": ["repos", "name", "contributions"],
    "repo": [
        "issues",
        "pull_requests",
        "contributors",
        "languages",
        "commits",
        "title",
        "created_at",
        "updated_at",
    ],
    "commit": ["message", "author", "date", "hash"],
}


def can_select_from(token: str, source: str):
    entities: list[str] | None = inner_entities.get(source)
    if entities == None:
        return False

    return token in entities


# parse tokens starting from token after 'from' token
def parse_from(tokens: list[Token]):
    if len(tokens) == 3:
        if can_select_from(tokens[2].value, "repo"):
            return From(
                user=tokens[0].value,
                repo=tokens[1].value,
                source=tokens[2].value,
                type=SourceType.REPO,
            )
        raise RuntimeError(
            f"Parse Error: can't select {tokens[2].value} from repo {tokens[1].value}"
        )
    if len(tokens) == 2:
        if can_select_from(tokens[1].value, "user"):
            return From(
                user=tokens[0].value, source=tokens[1].value, type=SourceType.USER
            )
        raise RuntimeError(
            f"Parse Error: can't select {tokens[1].value} from user {tokens[0].value}"
        )
    raise ValueError("Invalid number of tokens for parsing 'FROM' statement.")


# parse tokens starting from the token after 'select' token
def parse_select(tokens: list[Token]):
    select: Select = Select()
    i = 0
    while i < len(tokens) and tokens[i].type == TokenType.LITERAL:
        select.add_column(tokens[i].value)
        i += 1

    return select


def parse_tokens(tokens: list[Token]):
    select_stmt: Select | None = None
    from_stmt: From = None
    for i in range(len(tokens)):
        if tokens[i].type == TokenType.SELECT:
            select_stmt = parse_select(tokens[i + 1 :])
            print(select_stmt)
        elif tokens[i].type == TokenType.FROM:
            sources: list[Token] = []
            i += 1
            while i < len(tokens) and tokens[i].type == TokenType.SOURCE:
                sources.append(tokens[i])
                i += 1
            from_stmt = parse_from(sources)
            print(from_stmt)

    for column in select_stmt.columns:
        if can_select_from(column, from_stmt.source):
            print(f"select(column={column}, from={from_stmt.source})")
        else:
            raise RuntimeError(
                f"Parse Error: can't select {column} from {from_stmt.source}"
            )


query = "select title, label, user from redis.redis.issues where status = 'merged' and value = 3 order by value desc limit 5"

tokens = tokenize(query)

parse_tokens(tokens)
