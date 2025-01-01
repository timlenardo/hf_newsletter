# Hugging Face Newsletter

This project creates an email newsletter containing trending projects from Hugging Face. It uses the official Hugging Face API to fetch trending models, formats the information into a nice HTML email, and sends it to specified recipients.

## Setup

1. Clone this repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your details:
   ```bash
   cp .env.example .env
   ```

4. Configure the `.env` file with your email credentials:
   - `SENDER_EMAIL`: Your Gmail address
   - `SENDER_PASSWORD`: Your Gmail App-Specific Password (not your regular password)
   - `RECIPIENT_EMAIL`: Email address where you want to receive the newsletter

### Postmark Setup
To send emails using Postmark:
1. Create a Postmark account at https://postmarkapp.com
2. Create a new server in Postmark
3. Get your server token from the "Credentials" tab
4. Verify your sender email address in Postmark
5. Add to your `.env` file:
   - `POSTMARK_TOKEN`: Your Postmark server token
   - `SENDER_EMAIL`: Your verified sender email
   - `RECIPIENT_EMAIL`: Email address where you want to receive the newsletter

Note: Make sure your sender email domain is verified in Postmark before sending emails.

## Usage

The newsletter system provides several command-line options:

```bash
# Send newsletter (default behavior)
python src/cli.py

# Preview newsletter in browser without sending
python src/cli.py --preview

# View database statistics
python src/cli.py --stats

# Export database to CSV
python src/cli.py --export data/history.csv

# Override recipient email
python src/cli.py --recipient user@example.com
```

### Basic Usage

Running without arguments will:
1. Fetch trending projects from Hugging Face
2. Filter for new or significantly updated models
3. Create and send the newsletter to the configured recipient

### Preview Mode

The `--preview` option allows you to review the newsletter in your browser before sending:
```bash
python src/cli.py --preview
```

### Database Statistics

View statistics about highlighted models:
```bash
python src/cli.py --stats
```

This shows:
- Total number of models highlighted
- Top 5 authors by number of models
- 5 most recent highlights
- 5 most liked models

### Data Export

Export the database to CSV for analysis:
```bash
python src/cli.py --export data/newsletter_history.csv
```

### Logging

The system maintains detailed logs in the `logs` directory:
- Daily log files (e.g., `newsletter_20240215.log`)
- Includes information about fetched projects, errors, and email status

## Deployment

The newsletter can be deployed as a systemd service that runs automatically every morning at 9 AM.

### Automatic Installation

1. Navigate to the deploy directory:
   ```bash
   cd deploy
   ```

2. Make the install script executable:
   ```bash
   chmod +x install.sh
   ```

3. Run the installation script:
   ```bash
   sudo ./install.sh
   ```

The script will:
- Copy files to `/opt/hf-newsletter/`
- Install required Python packages
- Set up systemd service and timer
- Enable automatic daily runs at 9 AM

### Managing the Service

Check service status:
```bash
systemctl status hf-newsletter.service
```

Check timer status:
```bash
systemctl status hf-newsletter.timer
```

View upcoming scheduled runs:
```bash
systemctl list-timers hf-newsletter.timer
```

View logs:
```bash
tail -f /opt/hf-newsletter/logs/service.log
```

### Manual Trigger

To run the newsletter manually:
```bash
systemctl start hf-newsletter.service
```

### Uninstallation

To remove the service:
```bash
cd deploy
chmod +x uninstall.sh
sudo ./uninstall.sh
```

## Features

- Uses the official Hugging Face API to fetch trending projects
- Includes comprehensive project information:
  - Title and author
  - Description
  - Likes and download counts
  - Tags
  - Last modified date
- Tracks previously highlighted models in SQLite database
- Only includes new or significantly updated models:
  - New models that haven't been featured before
  - Models with significant changes (content updates)
  - Models with substantial increase in popularity (20% or more increase in likes/downloads)
- Formats the data into a clean, responsive HTML email
- Sends the newsletter using Gmail SMTP

## Database

The script maintains a SQLite database (`data/newsletter.db`) to track previously highlighted models. This ensures that:
- Each model is only featured once unless it has significant updates
- You can track the history of highlighted models
- The newsletter remains fresh and relevant

The database tracks:
- Model ID and author
- Last time the model was highlighted
- Last modification date
- Likes and download counts

## Error Handling

The script includes error handling for:
- Missing environment variables
- API connection issues
- Database operations
- Email sending errors