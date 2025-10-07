# Telegram Temporary Email Bot

A simple Telegram bot that creates and manages temporary email addresses using the [Mail.tm API](https://mail.tm). Protect your privacy by generating disposable email addresses for testing, sign-ups, or avoiding spam, all within Telegram!

## Features
- **Create Temporary Emails**: Use `/nouveau` to generate a new email address instantly (valid for 24-48 hours).
- **Check Inbox**: Use `/inbox` to view received emails with sender, subject, and date.
- **Read Emails**: Click `/read_<message_id>` to view full email content with inline clickable links (e.g., verification links).
- **View Current Email**: Use `/email` to display your active email address.
- **Help Command**: Use `/aide` for a quick usage guide.
- **Persistent Storage**: User data (email, password, token) is saved in a `user_data.json` file to persist across bot restarts.
- **Secure and Private**: Emails are encrypted via the Mail.tm API, and addresses expire after 24-48 hours.

## Why This Bot?
This bot was created to make temporary email creation fast and accessible directly from Telegram. Whether you’re testing a service, signing up without sharing your personal email, or avoiding spam, this bot offers a seamless solution with a focus on privacy and ease of use.

## Prerequisites
- Python 3.8+
- A Telegram account
- A Telegram bot token (obtained via [@BotFather](https://t.me/BotFather))
- Internet connection for API requests

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/sosthene14/telegram-temp-email-bot.git
   cd telegram-temp-email-bot
   ```

2. **Install Dependencies**:
   Create a virtual environment (optional but recommended) and install required packages:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set Up Your Bot Token**:
   - Create a bot via [@BotFather](https://t.me/BotFather) on Telegram to get a token.
   - Replace `"YOUR_NEW_TOKEN_HERE"` in `temp_email_bot.py` with your bot token.

4. **Run the Bot**:
   ```bash
   python temp_email_bot.py
   ```

## Usage
1. Start the bot by messaging it on Telegram (find it via the name set in @BotFather).
2. Use the following commands:
   - `/start`: Displays a welcome message and available commands.
   - `/nouveau`: Creates a new temporary email address.
   - `/inbox`: Shows a list of received emails.
   - `/email`: Displays your current email address.
   - `/aide`: Shows a help guide.
   - `/read_<message_id>`: Reads a specific email (e.g., `/read_68e4cdbe75496447fd5ed451`).
3. Emails are stored in `user_data.json` and persist across bot restarts.

## Example
1. Send `/nouveau` to get a new email: `xyz123@tiffincrane.com`.
2. Send `/inbox` to see emails, e.g.:
   ```
   📬 Inbox: xyz123@tiffincrane.com
   1. 📧 De: noreply@appwrite.io
      Objet: Account Verification
      Date: 2025-10-07
      /read_68e4cdbe75496447fd5ed451
   ```
3. Send `/read_68e4cdbe75496447fd5ed451` to view:
   ```
   📧 Message
   De: noreply@appwrite.io
   Objet: Account Verification
   Hello styve oumba,
   ...
   ```

## Project Structure
- `temp_email_bot.py`: Main bot script with all functionality.
- `user_data.json`: Stores user email data (created automatically).
- `requirements.txt`: Lists Python dependencies.

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add YourFeature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a Pull Request.

## Security Notes
- **Bot Token**: Keep your Telegram bot token private. Never share it publicly (e.g., in GitHub commits). Use environment variables or a `.env` file for production.
- **JSON Security**: The `user_data.json` file contains sensitive data (emails, passwords, tokens). Ensure it’s not exposed in public repositories (add to `.gitignore`).
- **Regenerate Token**: If you’ve shared your token publicly, regenerate it via @BotFather immediately.

## Future Improvements
- Add email expiration cleanup (remove accounts after 48 hours).
- Support premium features (e.g., custom domains, extended validity).
- Enhance error handling for API failures.
- Add multi-language support for the bot’s interface.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
Questions or feedback? Reach out via sosthenemounsambote14@gmail.com or open an issue on GitHub!

*Created by Sosthène Mounsamboté for privacy-conscious users and tech enthusiasts!*