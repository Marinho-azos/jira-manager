# Jira Integration - Setup and Examples

## Installation

```bash
pip install jira
```

## Environment Variables Configuration

Create a `.env` file or configure in your shell:

```bash
export JIRA_SERVER=https://your-jira.atlassian.net
export JIRA_EMAIL=your-email@example.com
export JIRA_API_TOKEN=your-api-token-here
```

## How to Get API Token

1. Visit: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy the generated token

## Usage Examples

### Create Story
```bash
python scripts/jira_manager.py story \
  "Implement POST /v1/preonboarding endpoint" \
  --project PROJ \
  --description "Endpoint for account verification in preonboarding process" \
  --assignee your-email@example.com \
  --labels "backend" "api" \
  --priority High
```

### Create Epic
```bash
python scripts/jira_manager.py epic \
  "Domain Account Improvements" \
  --project PROJ \
  --description "Epic with general improvements for domain-account service" \
  --epic-name "Domain Account Improvements"
```

### Create Subtask
```bash
python scripts/jira_manager.py subtask \
  "Document POST /v1/preonboarding endpoint" \
  --project PROJ \
  --parent PROJ-123 \
  --description "Create documentation following existing pattern" \
  --assignee your-email@example.com
```

### Edit Issue
```bash
python scripts/jira_manager.py edit PROJ-123 \
  --summary "New concise summary" \
  --description "Updated description" \
  --priority High \
  --labels backend api
```

### Delete Issue
```bash
python scripts/jira_manager.py delete PROJ-123
```

## Improved Script with Template

You can create a wrapper script to make it even easier:

```bash
#!/bin/bash
# scripts/create_jira_story.sh

python scripts/jira_manager.py story "$1" \
  --project PROJ \
  --description "$2" \
  --assignee $(git config user.email) \
  --labels "backend"
```

Usage:
```bash
./scripts/create_jira_story.sh "Title" "Description"
```

## Git Hooks Integration

You can create a hook that automatically creates a story when creating a branch:

```bash
#!/bin/bash
# .git/hooks/post-checkout

if [[ "$1" != "0000000000000000000000000000000000000000" ]]; then
  BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
  if [[ "$BRANCH_NAME" == feature/* ]]; then
    python scripts/jira_manager.py story \
      "$BRANCH_NAME" \
      --project PROJ \
      --description "Work related to branch $BRANCH_NAME"
  fi
fi
```

## Troubleshooting

### Error: "customfield_10011"
The Epic Name field may vary. To discover:
```python
from jira import JIRA
jira = JIRA(server='...', basic_auth=('...', '...'))
issue = jira.issue('PROJ-123')
print(issue.raw['fields'].keys())  # See all fields
```

### Authentication Error
- Check if the email is correct
- Check if the API token is valid
- Make sure to use API token, not password