from commitizen.cz.base import BaseCommitizen
from commitizen.defaults import Questions


class PcJiraCz(BaseCommitizen):
    def questions(self) -> Questions:
        """Questions regarding the commit message."""
        questions: Questions = [
            {
                "type": "input",
                "name": "jira_ticket",
                "message": "'BSR' or Jira ticket number. e.g. PC-XXXX",
            },
            {
                "type": "list",
                "name": "affected_repository",
                "message": "Select the repository affected by the change you are committing",
                "choices": [
                    {"value": "API", "name": "API"},
                    {"value": "PRO", "name": "PRO"},
                    {"value": "ADAGE", "name": "ADAGE"},
                    {"value": "BO", "name": "BO"},
                    {"value": "", "name": "None of the above"},
                ],
            },
            {
                "type": "list",
                "name": "change_type",
                "message": "Select the type of changes you are committing",
                "choices": [
                    {"value": "fix", "name": "fix: A bug fix"},
                    {"value": "feat", "name": "feat: A new feature"},
                    {"value": "docs", "name": "docs: Documentation only changes"},
                    {"value": "script", "name": "script: A one-time only script"},
                    {
                        "value": "style",
                        "name": "style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)",
                    },
                    {
                        "value": "refactor",
                        "name": "refactor: A code change that neither fixes a bug nor adds a feature",
                    },
                    {"value": "perf", "name": "perf: A code change that improves performance"},
                    {"value": "test", "name": "test: Adding missing or correcting existing tests"},
                    {
                        "value": "build",
                        "name": "build: Changes that affect the build system or external dependencies (example scopes: pip, docker, npm)",
                    },
                    {
                        "value": "ci",
                        "name": "ci: Changes to our CI configuration files and scripts (example scopes: GitLabCI)",
                    },
                    {"value": "bump", "name": "bump: Dependencies version bump"},
                    {"value": "revert", "name": "revert: Revert a commit"},
                    {"value": "chore", "name": "chore: A maintenance task to be done periodically"},
                ],
            },
            {
                "type": "input",
                "name": "message",
                "message": "Commit message:",
            },
        ]
        return questions

    def message(self, answers: dict) -> str:
        """Generate the commit message with the given answers."""
        message_template = "({jira_ticket}){repository} {change_type}: {message}"
        repository = f"[{answers['affected_repository']}]" if answers["affected_repository"] else ""

        return message_template.format(
            jira_ticket=answers["jira_ticket"],
            repository=repository,
            change_type=answers["change_type"],
            message=answers["message"],
        )

    def example(self) -> str:
        """Provide an example to help understand the style (OPTIONAL)"""
        return "(PC-88888)[API] feat: this is such a great commit"

    def schema(self) -> str:
        """Show the schema used (OPTIONAL)"""
        return "(<jira_ticket>)[<affected_repository>] <change_type>: <message>"

    def schema_pattern(self) -> str:
        """Schema regex pattern used for validation (OPTIONAL)"""
        return r"\((PC-\d+|BSR)\)(\[(API|PRO|ADAGE|BO)\])? ?(build|ci|docs|feat|fix|perf|refactor|script|style|test|chore|revert|bump)(\[[\w\s]+\])?:[\w\s]+"

    def info(self) -> str:
        """Explanation of the commit rules. (OPTIONAL)"""
        return "Commits should follow the pattern: (Jira ticket)[Repository] type: message"
