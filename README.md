# GitQL

GitQL is a SQL-like language designed for querying data from GitHub repositories. It enables users to perform advanced queries on users, organizations, repositories, issues, pull requests, contributors, releases, milestones, and more, by leveraging a familiar SQL syntax.

## Example Usage
![GitQL](assets/gitql.gif)


## Features

- **SQL-like syntax** for querying GitHub data.
- Supports querying **users**, **organizations**, **repositories**, **issues**, **pull requests**, **contributors**, **releases**, **milestones**, **teams**, and **labels**.
- **Filtering options** for various fields such as `status`, `title`, `author`, `date`, and more.
- **Sorting** and **limiting** results with `ORDER BY` and `LIMIT`.
- Supports **multiple conditions** in queries using logical operators like `AND`, `OR`, and `NOT`.

## Query Syntax

GitQL follows a simple SQL-like query syntax:

```sql
SELECT <column> [, <column> ...]
FROM { user | org } . { repos | stars | projects | info } 
   | repo . { issues | pull_requests | contributors | languages | commits | title | updated_at | description | milestones | labels | releases | collaborators | projects | teams }
[WHERE <condition>]
[ORDER BY { <column> | <expr> } [ASC | DESC]]
[LIMIT <row_limit>]
```

### Keywords Supported:
- `SELECT`
- `FROM`
- `WHERE`
- `ORDER BY`
- `ASC`, `DESC`
- `IN`
- Logical operators: `AND`, `OR`, `NOT`
- Comparison operators: `GREATER`, `LESS`, `EQUAL`, `GEQ`, `LEQ`

## Supported Entities and Fields

GitQL supports querying data from several entities and their respective fields. Below are the available entities and fields:

### **Users and Organizations** (`user | org`)
- `repos`, `stars`, `projects`, `info`, `followers`, `following`

### **Repositories** (`repo`)
- `issues`, `pull_requests`, `contributors`, `languages`, `commits`, `title`, `updated_at`, `description`, `milestones`, `labels`, `releases`, `collaborators`, `projects`, `teams`

### **Issues** (`repo.issues`)
- `status`, `label`, `author`, `assignee`, `title`, `description`, `created_at`, `updated_at`, `comments`, `milestone`

### **Pull Requests** (`repo.pull_requests`)
- `status`, `author`, `assignee`, `title`, `created_at`, `updated_at`, `merged_at`, `milestone`

### **Commits** (`repo.commits`)
- `author`, `date`, `message`, `hash`


## Example Queries

Here are some example queries you can run with GitQL:

1. **Select open issues with specific label and milestone:**

    ```sql
    SELECT title, label, milestone
    FROM repo.issues
    WHERE status = 'open' AND label = 'bug' AND milestone = 'v1.0'
    ORDER BY updated_at DESC
    LIMIT 10
    ```

2. **Select merged pull requests for a specific milestone:**

    ```sql
    SELECT title, assignee, merged_at, milestone
    FROM repo.pull_requests
    WHERE status = 'merged' AND milestone = 'v1.0'
    ORDER BY merged_at DESC
    LIMIT 5
    ```

3. **Select contributors with more than 100 contributions:**

    ```sql
    SELECT name, username, contributions
    FROM repo.contributors
    WHERE contributions > 100
    ORDER BY contributions DESC
    LIMIT 5
    ```


## Filtering Options

Each entity in GitQL allows filtering based on various fields like `status`, `title`, `author`, `created_at`, and more. You can use conditions like:

- `status = 'open'`
- `created_at > '2023-01-01'`
- `contributions > 100`
- `title LIKE '%bug%'`
- `assignee = 'john_doe'`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.