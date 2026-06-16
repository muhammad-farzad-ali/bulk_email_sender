# Bulk Email Sender

A Python CLI tool for sending bulk emails from a TSV file with progress tracking, error handling, and Discord notifications.

## Features

- **Interactive & CLI modes** - Use prompts or command-line arguments
- **TSV-based input** - Simple tab-separated file with id, email, subject, body, status
- **Status tracking** - Automatically updates status to `sent` or `error`
- **Progress display** - Rich terminal UI with progress bar and summary table
- **Discord notifications** - Send completion stats to a Discord webhook
- **Batch processing** - Send in batches, continue or close after each
- **Rate limiting** - Configurable delay between emails
- **Cross-platform** - Works on Windows and Linux

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure credentials

Copy `.env.example` to `.env` and fill in your SMTP credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL
```

### 3. Prepare your TSV file

Create a tab-separated file with these columns:

| Column  | Description                    |
|---------|--------------------------------|
| id      | Unique identifier              |
| email   | Recipient email address        |
| subject | Email subject line             |
| body    | Email body text                |
| status  | `pending`, `sent`, or `error`  |

Example `emails.tsv`:

```
id	email	subject	body	status
1	alice@example.com	Welcome	Hi Alice, welcome!	pending
2	bob@example.com	Hello	Hi Bob	this is a test	pending
```

## Usage

### Interactive mode

```bash
python -m src
```

Follow the prompts to configure your send batch.

### CLI mode

```bash
python -m src --file emails.tsv --count 10 --no-interactive
```

### All options

```
-f, --file PATH           Path to TSV file (required in CLI mode)
-c, --count N             Number of emails to send (default: all pending)
-a, --after ACTION        Post-batch action: 'close' or 'continue'
    --delay SECONDS       Delay between emails (default: 0)
    --no-discord          Skip Discord notification
    --no-interactive      Disable interactive prompts
    --env-file PATH       Path to .env file (default: .env)
    --test-connection     Test SMTP connection and exit
```

### Examples

```bash
# Send all pending emails
python -m src -f emails.tsv --no-interactive

# Send 50 emails with 1-second delay
python -m src -f emails.tsv -c 50 --delay 1 --no-interactive

# Test your SMTP connection
python -m src --test-connection

# Send and auto-close
python -m src -f emails.tsv -a close --no-interactive

# Send and prompt for next batch
python -m src -f emails.tsv -a continue --no-interactive
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Project Structure

```
bulk_email_sender/
├── .env.example          # Template for credentials
├── requirements.txt      # Dependencies
├── src/
│   ├── __main__.py      # Entry point
│   ├── app.py           # Main orchestrator
│   ├── cli.py           # Argument parsing & interactive prompts
│   ├── config.py        # .env loading & validation
│   ├── discord_webhook.py  # Discord notifications
│   ├── email_sender.py  # SMTP sending logic
│   ├── progress.py      # Rich terminal UI
│   └── tsv_manager.py   # TSV file operations
└── tests/               # Unit tests
```
