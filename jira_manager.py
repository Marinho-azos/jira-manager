#!/usr/bin/env python3
"""
Command-line tool to manage Jira issues: create, edit, and delete stories, epics, and subtasks.

Usage:
    python jira_manager.py story "Title" --project PROJ
    python jira_manager.py epic "Epic name" --project PROJ
    python jira_manager.py subtask "Title" --parent PROJ-123 --project PROJ
    python jira_manager.py edit PROJ-123 --description "New description"
    python jira_manager.py delete PROJ-123
"""

import os
import sys
import argparse
from typing import Optional, Dict, Any
from jira import JIRA, JIRAError


class JiraManager:
    def __init__(self, server: str, email: str, api_token: str):
        """Initialize Jira connection."""
        self.jira = JIRA(
            server=server,
            basic_auth=(email, api_token)
        )

    def create_story(
        self,
        project: str,
        summary: str,
        description: str = "",
        assignee: Optional[str] = None,
        labels: Optional[list] = None,
        priority: Optional[str] = None
    ) -> str:
        """Create a Story in Jira."""
        fields: Dict[str, Any] = {
            'project': {'key': project},
            'summary': summary,
            'description': description,
            'issuetype': {'name': 'Story'}
        }

        if assignee:
            fields['assignee'] = {'name': assignee}
        if labels:
            fields['labels'] = labels
        if priority:
            fields['priority'] = {'name': priority}

        issue = self.jira.create_issue(fields=fields)
        return issue.key

    def create_epic(
        self,
        project: str,
        summary: str,
        description: str = "",
        epic_name: Optional[str] = None
    ) -> str:
        """Create an Epic in Jira."""
        epic_field = self._get_epic_name_field(project)

        fields: Dict[str, Any] = {
            'project': {'key': project},
            'summary': summary,
            'description': description,
            'issuetype': {'name': 'Epic'}
        }

        if epic_field:
            fields[epic_field] = epic_name or summary

        issue = self.jira.create_issue(fields=fields)
        return issue.key

    def create_subtask(
        self,
        project: str,
        parent_key: str,
        summary: str,
        description: str = "",
        assignee: Optional[str] = None
    ) -> str:
        """Create a subtask in Jira."""
        fields: Dict[str, Any] = {
            'project': {'key': project},
            'summary': summary,
            'description': description,
            'issuetype': {'name': 'Sub-task'},
            'parent': {'key': parent_key}
        }

        if assignee:
            fields['assignee'] = {'name': assignee}

        issue = self.jira.create_issue(fields=fields)
        return issue.key

    def edit_issue(
        self,
        issue_key: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        assignee: Optional[str] = None,
        labels: Optional[list] = None,
        priority: Optional[str] = None
    ) -> str:
        """Edit an existing Jira issue."""
        issue = self.jira.issue(issue_key)
        fields: Dict[str, Any] = {}

        if summary is not None:
            fields['summary'] = summary
        if description is not None:
            fields['description'] = description
        if assignee is not None:
            fields['assignee'] = {'name': assignee}
        if labels is not None:
            fields['labels'] = labels
        if priority is not None:
            fields['priority'] = {'name': priority}

        if fields:
            issue.update(fields=fields)

        return issue.key

    def delete_issue(self, issue_key: str) -> None:
        """Delete a Jira issue."""
        issue = self.jira.issue(issue_key)
        issue.delete()

    def _get_epic_name_field(self, project: str) -> Optional[str]:
        """Get the Epic Name customfield ID."""
        try:
            issue_types = self.jira.issue_types()
            for issue_type in issue_types:
                if issue_type.name == 'Epic':
                    return 'customfield_10011'
        except Exception:
            pass
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Manage Jira issues: create, edit, and delete'
    )

    parser.add_argument(
        'type',
        choices=['story', 'epic', 'subtask', 'edit', 'delete'],
        help='Action to perform'
    )
    parser.add_argument(
        'issue_key_or_summary',
        nargs='?',
        help='Issue key (for edit/delete) or summary (for create)'
    )
    parser.add_argument(
        '--project', '-p',
        help='Project key (ex: PROJ)'
    )
    parser.add_argument(
        '--description', '-d',
        default='',
        help='Issue description'
    )
    parser.add_argument(
        '--assignee', '-a',
        help='Assignee email'
    )
    parser.add_argument(
        '--labels', '-l',
        nargs='+',
        help='Labels separated by space'
    )
    parser.add_argument(
        '--priority',
        choices=['Highest', 'High', 'Medium', 'Low', 'Lowest'],
        help='Priority'
    )
    parser.add_argument(
        '--parent',
        help='Parent issue key (for subtasks)'
    )
    parser.add_argument(
        '--epic-name',
        help='Epic name (for epics)'
    )
    parser.add_argument(
        '--summary',
        help='Issue summary (for edit)'
    )

    args = parser.parse_args()

    jira_server = os.getenv('JIRA_SERVER')
    jira_email = os.getenv('JIRA_EMAIL')
    jira_token = os.getenv('JIRA_API_TOKEN')

    if not all([jira_server, jira_email, jira_token]):
        print("Error: Configure environment variables:")
        print("  export JIRA_SERVER=https://seu-jira.atlassian.net")
        print("  export JIRA_EMAIL=seu-email@exemplo.com")
        print("  export JIRA_API_TOKEN=seu-token")
        sys.exit(1)

    try:
        manager = JiraManager(jira_server, jira_email, jira_token)

        if args.type == 'story':
            if not args.project or not args.issue_key_or_summary:
                print("Error: --project and summary are required for story")
                sys.exit(1)

            key = manager.create_story(
                project=args.project,
                summary=args.issue_key_or_summary,
                description=args.description,
                assignee=args.assignee,
                labels=args.labels,
                priority=args.priority
            )
            print(f"? Story created: {key}")

        elif args.type == 'epic':
            if not args.project or not args.issue_key_or_summary:
                print("Error: --project and summary are required for epic")
                sys.exit(1)

            key = manager.create_epic(
                project=args.project,
                summary=args.issue_key_or_summary,
                description=args.description,
                epic_name=args.epic_name
            )
            print(f"? Epic created: {key}")

        elif args.type == 'subtask':
            if not args.project or not args.issue_key_or_summary:
                print("Error: --project and summary are required for subtask")
                sys.exit(1)
            if not args.parent:
                print("Error: --parent is required for subtasks")
                sys.exit(1)

            key = manager.create_subtask(
                project=args.project,
                parent_key=args.parent,
                summary=args.issue_key_or_summary,
                description=args.description,
                assignee=args.assignee
            )
            print(f"? Subtask created: {key}")

        elif args.type == 'edit':
            if not args.issue_key_or_summary:
                print("Error: Issue key is required for edit")
                sys.exit(1)

            key = manager.edit_issue(
                issue_key=args.issue_key_or_summary,
                summary=args.summary,
                description=args.description,
                assignee=args.assignee,
                labels=args.labels,
                priority=args.priority
            )
            print(f"? Issue updated: {key}")

        elif args.type == 'delete':
            if not args.issue_key_or_summary:
                print("Error: Issue key is required for delete")
                sys.exit(1)

            manager.delete_issue(args.issue_key_or_summary)
            print(f"? Issue deleted: {args.issue_key_or_summary}")

    except JIRAError as e:
        print(f"? Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
