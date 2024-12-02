import logging
from functools import lru_cache
from github import NamedUser, Repository, Github, UnknownObjectException, Auth
from globals import inner_entities
from enum import Enum
from tokenizer import Token
import os
from datetime import datetime


# Replace GH_TOKEN with your GitHub token
auth: Auth = Auth.Token(os.getenv("GH_TOKEN"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("context.log"),  # Log to a file
        logging.StreamHandler(),  # Log to the console
    ],
)
logger = logging.getLogger(__name__)


class SourceType(Enum):
    USER = 0
    REPO = 1
    ISSUES = 2
    PULL_REQUESTS = 3
    COMMITS = 4
    USER_REPOS = 5


class Context:
    def __init__(self):
        self.user: str = None
        self.repo: str = None
        self.source: str = ""
        self.source_type: SourceType = None
        self.selected_columns: list[str] = []
        self.git_records: list[dict] = []
        self.query_results: list[dict] = []
        self.limit: int = 1
        self.max_limit: int = 1
        self.current_read: int = 0
        self.current_row: int = 0
        self.git: Github = Github(auth=auth)
        self.total_populates: int = 0

    def _can_select(self, s: str) -> bool:
        return s in inner_entities.get(self.source)

    def get_value(self, key: str):
        if self.current_row >= len(self.git_records):
            self.repopulate()
        return self.git_records[self.current_row].get(key)

    def select_current(self):
        self.query_results.append(self.git_records[self.current_row])
        self.advance()

    def advance(self):
        self.current_row += 1
        if (
            self.current_row >= len(self.git_records)
            and len(self.query_results) < self.limit
        ):
            self.repopulate()

    def repopulate(self):
        logger.debug("Repopulating git records")
        self.git_records.clear()
        self.current_row = 0
        self.populate()

    def done(self):
        if self.limit is None:
            logger.error("Limit is not set.")
            raise RuntimeError("Limit is not set.")
        return len(self.query_results) >= self.limit

    def set_limit(self, limit: int):
        logger.info(f"Setting query limit to {limit}")
        self.limit = limit

    def set_max_limit(self, limit: int):
        logger.info(f"Setting max limit to {limit}")
        self.max_limit = limit

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
                    logger.error(f"Unknown source type: {source_tree[2]}")
                    raise RuntimeError("Unknown source")
            self.source_type = source_type
            repo_str: str = f"{source_tree[0]}/{source_tree[1]}"
            try:
                self.get_repo(repo_str)
            except UnknownObjectException:
                logger.error(f"Invalid repository: {repo_str}")
                raise
            self.user = source_tree[0]
            self.repo = source_tree[1]

        if self.source:
            for col in self.selected_columns:
                if not self._can_select(col):
                    raise RuntimeError(f"can't select {col} from {self.source}")

    def add_selected_column(self, column: str):
        self.selected_columns.append(column)

    @lru_cache(maxsize=128)
    def get_repo(self, repo_str: str) -> Repository:
        logger.info(f"Fetching repository: {repo_str}")
        return self.git.get_repo(repo_str)

    @lru_cache(maxsize=128)
    def get_user(self, username: str) -> NamedUser:
        logger.info(f"Fetching user: {username}")
        return self.git.get_user(username)

    def populate(self):
        self.total_populates += 1
        logger.debug(f"Populating data for source type: {self.source_type}")
        try:
            match self.source_type:
                case SourceType.ISSUES | SourceType.PULL_REQUESTS | SourceType.COMMITS:
                    repo = self.get_repo(f"{self.user}/{self.repo}")
                    if self.source_type == SourceType.ISSUES:
                        for issue in repo.get_issues(state="all")[
                            self.current_read : self.current_read + self.max_limit
                        ]:
                            logger.debug(f"Processing issue ID: {issue.id}")
                            self.git_records.append(
                                {
                                    "id": issue.id,
                                    "number": issue.number,
                                    "title": issue.title,
                                    "state": issue.state,
                                    "milestone": issue.milestone,
                                    "labels": issue.labels,
                                    "user": issue.user.login,
                                    "created_at": issue.created_at.strftime(
                                        "%Y-%m-%d %H:%M:%S"
                                    ),
                                    "closed_at": (
                                        issue.closed_at.strftime("%Y-%m-%d %H:%M:%S")
                                        if issue.state == "closed"
                                        else "N/A"
                                    ),
                                    "closed_by": (
                                        issue.closed_by.login
                                        if issue.closed_by != None
                                        else "N/A"
                                    ),
                                }
                            )
                            self.current_read += 1
                    elif self.source_type == SourceType.COMMITS:
                        for commit in repo.get_commits()[
                            self.current_read : self.current_read + self.max_limit
                        ]:
                            logger.debug(f"Processing commit SHA: {commit.sha}")
                            self.git_records.append(
                                {
                                    "sha": commit.sha,
                                    "author": commit.author.login,
                                    "files": commit.files,
                                }
                            )
                            self.current_read += 1
                    elif self.source_type == SourceType.PULL_REQUESTS:
                        for pr in repo.get_pulls(state="all")[
                            self.current_read : self.current_read + self.max_limit
                        ]:
                            logger.debug(f"Processing pull request ID: {pr.id}")
                            self.git_records.append(
                                {
                                    "id": pr.id,
                                    "number": pr.number,
                                    "title": pr.title,
                                    "state": pr.state,
                                    "milestone": pr.milestone,
                                    "user": pr.user.login,
                                    "changed_files": pr.changed_files,
                                    "created_at": pr.created_at.strftime(
                                        "%Y-%m-%d %H:%M:%S"
                                    ),
                                    "merged": "true" if pr.merged else "false",
                                    "merged_at": (
                                        (pr.merged_at.strftime("%Y-%m-%d %H:%M:%S"))
                                        if pr.merged
                                        else "N/A"
                                    ),
                                    "merged_by": (
                                        pr.merged_by.login if pr.merged else "None"
                                    ),
                                }
                            )
                            self.current_read += 1
                case SourceType.USER_REPOS:
                    user = self.get_user(self.user)
                    for repo in user.get_repos()[
                        self.current_read : self.current_read + self.max_limit
                    ]:
                        logger.debug(f"Processing repository ID: {repo.id}")
                        self.git_records.append(
                            {
                                "id": repo.id,
                                "name": repo.name,
                                "open_issues_count": repo.open_issues_count,
                                "private": repo.private,
                                "created_at": repo.created_at.strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                                "description": repo.description,
                                "forks_count": repo.forks_count,
                                "full_name": repo.full_name,
                                "languages": repo.get_languages(),
                                "topics": repo.topics,
                            }
                        )
                        self.current_read += 1
                case _:
                    logger.error("Unknown source type encountered.")
                    raise RuntimeError("Unknown source type")
        except Exception as e:
            logger.exception(f"Error while populating records: {e}")
            raise
