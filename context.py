from github import (
    NamedUser,
    Repository,
    Github,
    UnknownObjectException,
    Auth,
)
from globals import inner_entities
from enum import Enum
from tokenizer import Token
import os


auth: Auth = Auth.Token(os.getenv("GH_TOKEN"))


class SourceType(Enum):
    USER = 0
    REPO = 1
    ISSUES = 2
    PULL_REQUESTS = 3
    COMMITS = 4
    USER_REPOS = 5


class Context:
    def __init__(self):
        self.user: NamedUser = None
        self.repo: Repository = None
        self.source: str = ""
        self.source_type: SourceType = None
        self.selected_columns: list[str] = []
        self.git_records: list[dict] = []
        self.query_results: list[dict] = []
        self.limit: int = 1
        self.max_limit: int = 100
        self.current_read: int = 0
        self.current_row: int = 0
        self.git: Github = Github(auth=auth)
        self.total_populates: int = 0

    def _can_select(self, s: str, f: str) -> bool:
        return s in inner_entities.get(f)

    def get_value(self, key: str):
        if self.current_row >= len(self.git_records):
            self.repopulate()
        return self.git_records[self.current_row].get(key)

    def select_current(self):
        self.query_results.append(self.git_records[self.current_row])
        self.current_row += 1

    def advance(self):
        self.current_row += 1
        if (
            self.current_row >= len(self.git_records)
            and len(self.query_results) < self.limit
        ):
            self.repopulate()

    def repopulate(self):
        self.git_records.clear()
        self.current_row = 0
        self.populate()

    def done(self):
        if self.limit is None:
            raise RuntimeError("Limit is not set.")
        return len(self.query_results) >= self.limit

    def set_limit(self, limit: int):
        self.limit = limit

    def set_max_limit(self, limit: int):
        self.max_limit = limit

    # user.repos
    # user.repo. { issues | pull_requests | commits }
    def set_sources(self, source_token: Token):
        source_tree: list[str] = source_token.value.split(".")
        if len(source_tree) == 2:
            if source_tree[1] == "repos":
                self.source_type = SourceType.USER_REPOS
                self.source = source_tree[0]
                self.user = self.source
        elif len(source_tree) == 3:
            source_type: SourceType = None
            match source_tree[2]:
                case "issues":
                    source_type = SourceType.ISSUES
                case "pull_requests":
                    source_type = SourceType.PULL_REQUESTS
                case "commits":
                    source_type = SourceType.COMMITS
                case _:
                    raise RuntimeError("unknown source")
            self.source_type = source_type
            repo_str: str = f"{source_tree[0]}/{source_tree[1]}"
            try:
                self.git.get_repo(repo_str)
            except UnknownObjectException:
                print("wrong username or repo name")
                raise
            self.user = source_tree[0]
            self.repo = source_tree[1]

    def add_selected_column(self, column: str):
        assert self.source and self._can_select(column, self.source)
        self.selected_columns.append(column)

    def populate(self):
        self.total_populates += 1
        match self.source_type:
            case SourceType.ISSUES | SourceType.PULL_REQUESTS | SourceType.COMMITS:
                repo = self.git.get_repo(f"{self.user}/{self.repo}")
                if self.source_type == SourceType.ISSUES:
                    for issue in repo.get_issues()[
                        self.current_read : self.current_read + self.max_limit
                    ]:
                        iss: dict = {
                            "id": issue.id,
                            "title": issue.title,
                            "state": issue.state,
                            "milestone": issue.milestone,
                            "labels": issue.labels,
                            "user": issue.user.login,
                            "closed_at": issue.closed_at,
                            "closed_by": issue.closed_by,
                        }
                        self.git_records.append(iss)
                        self.current_read += 1
                elif self.source_type == SourceType.COMMITS:
                    for commit in repo.get_commits()[
                        self.current_read : self.current_read + self.max_limit
                    ]:
                        com: dict = {
                            "author": commit.author.login,
                            "files": commit.files,
                            "sha": commit.sha,
                        }
                        self.git_records.append(com)
                        self.current_read += 1
                elif self.source_type == SourceType.PULL_REQUESTS:
                    for pr in repo.get_pulls()[
                        self.current_read : self.current_read + self.max_limit
                    ]:
                        pull: dict = {
                            "assignee": pr.user.login,
                            "changed_files": pr.changed_files,
                            "closed_at": pr.closed_at,
                            "state": pr.state,
                            "milestone": pr.milestone,
                            "title": pr.title,
                            "created_at": pr.created_at,
                        }
                        self.git_records.append(pull)
                        self.current_read += 1
                else:
                    raise RuntimeError("unknown source")
            case SourceType.USER:
                user = self.git.get_user(self.user)
                for repo in user.get_repos()[
                    self.current_read : self.current_read + self.max_limit
                ]:
                    rp: dict = {
                        "id": repo.id,
                        "name": repo.name,
                        "open_issues_count": repo.open_issues_count,
                        "private": repo.private,
                        "created_at": repo.created_at,
                        "description": repo.description,
                        "forks_count": repo.forks_count,
                        "full_name": repo.full_name,
                        "languages": repo.get_languages(),
                        "topics": repo.topics,
                    }
                    self.git_records.append(rp)
                    self.current_read += 1
