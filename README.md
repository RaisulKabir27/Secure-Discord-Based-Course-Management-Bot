# Secure Discord-Based Course Management Bot

A secure and automated Discord-based course management system designed to simplify academic coordination, student verification, role assignment, announcements, and structured communication.

The bot was developed to support course coordination by connecting student registration information with Discord server roles and channels.

## Features

- Student verification using registration information
- Automatic Discord role assignment based on student information
- Course-section identification
- Role-based access control
- Automated course communication
- Structured Discord-based academic coordination
- Administrative and diagnostic commands
- Environment-variable based Discord authentication
- Local student-registration data support
- Protection of private student data from version control

## How It Works

The system connects a course registration dataset with a Discord server.

```text
Course Registration Data
          |
          v
    Load Student Data
          |
          v
   Normalize Student IDs
          |
          v
 Match Discord User Information
          |
          v
    Identify Student
          |
          v
 Determine Course / Section
          |
          v
 Assign Appropriate Discord Role
```

Once a student is successfully identified, the bot can assign the appropriate Discord role, allowing access to the relevant course communication and resources.

## Project Structure

```text
Secure-Discord-Based-Course-Management-Bot/
|
├── main.py
├── keep_alive.py
├── requirements.txt
├── pyproject.toml
├── uv.lock
├── .gitignore
├── .replit
└── README.md
```

### Main Components

#### `main.py`

Contains the main Discord bot implementation, including Discord client configuration, student-data processing, student identification, course/section mapping, role assignment, administrative commands, and diagnostic functionality.

#### `keep_alive.py`

Provides supporting keep-alive functionality used by the project deployment setup.

#### `requirements.txt`

Contains the Python dependencies required to run the bot.

#### `pyproject.toml`

Contains project configuration and Python dependency metadata.

#### `uv.lock`

Stores locked dependency versions for reproducible environments.

## Requirements

Before running the bot, make sure you have:

- Python 3.10 or newer
- A Discord account
- A Discord server where you have administrative permissions
- A Discord application/bot created through the Discord Developer Portal
- Your own course registration dataset

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/RaisulKabir27/Secure-Discord-Based-Course-Management-Bot.git
cd Secure-Discord-Based-Course-Management-Bot
```

### 2. Create a virtual environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Discord Bot Setup

Create a Discord application and bot through the Discord Developer Portal:

https://discord.com/developers/applications

From the Bot section, generate a bot token.

**Never publish the token or commit it to GitHub.**

## Environment Configuration

Create a `.env` file in the project root:

```env
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
```

The application loads the token from the environment rather than storing it directly in source code.

Do not commit `.env` to GitHub.

## Course Registration Data

The bot uses course registration information to identify students and determine their corresponding course sections.

The original registration dataset used during development contains private student information and is **not included in this repository**.

The file is intentionally excluded through `.gitignore`:

```gitignore
reg-2-26.xlsx
```

Users deploying the project should provide their own course registration dataset according to the structure expected by the application.

> **Important:** Never upload real student records, registration numbers, email addresses, or other personally identifiable information to a public repository.

## Discord Permissions and Intents

The bot needs appropriate Discord permissions to perform its course-management functions.

Depending on the configuration, these may include:

- Managing roles
- Viewing channels
- Sending messages
- Reading message history
- Managing channels

Required Discord Gateway Intents should also be enabled from the Discord Developer Portal when required by the application.

## Role Configuration

The Discord server should contain the roles used by the course-management system.

The bot must have sufficient permissions to assign those roles. The bot's highest role must be positioned above the roles it needs to assign.

Example:

```text
Administrator
    |
    ├── Course Management Bot
    ├── CSE341 Section A
    ├── CSE341 Section B
    └── CSE341 Section C
```

## Running the Bot

After configuring the environment and course data:

```bash
python main.py
```

If the configuration is correct, the bot will connect to Discord and become available in the configured server.

## Administrative and Diagnostic Commands

The project includes commands intended for testing, administration, and troubleshooting.

Examples include:

```text
!test_map
```

Tests student/course mapping functionality.

```text
!test_role
```

Tests Discord role-related functionality.

```text
!diag_id
```

Provides diagnostic information related to student identification.

```text
!assign_roles GUILD_ID CHANNEL_ID limit
```

Performs role-assignment processing for the specified Discord server/channel configuration.

> Command availability and behavior depend on the configuration in `main.py`.

## Security and Privacy

Security and privacy are important considerations because course registration information may contain personally identifiable student data.

### No student registration data in Git

The actual registration spreadsheet is excluded using `.gitignore`.

```gitignore
reg-2-26.xlsx
```

### No Discord token in source code

The Discord bot token is loaded from an environment variable rather than being stored directly in the source code.

### Local data processing

Course registration data can remain local to the deployment environment rather than being published with the source code.

### Public repository safety

The repository contains the application code but does not include the original private student dataset.

## Deployment

The project can be run locally or deployed to a suitable Python hosting environment.

For deployment:

1. Clone the repository.
2. Install the required dependencies.
3. Configure the Discord bot token as an environment variable or secret.
4. Provide the required course registration data locally.
5. Configure the Discord server and roles.
6. Start the bot.

For production deployment, use environment variables or the hosting platform's secret-management system instead of storing credentials in source files.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| Discord API | Bot and server integration |
| Discord.py | Discord bot implementation |
| Pandas | Data processing |
| OpenPyXL | Excel data processing |
| Python-dotenv | Environment-variable management |
| Git | Version control |

## Use Case

This project was developed for academic course coordination.

Instead of manually managing student access and course communication across multiple platforms, the system provides a centralized Discord-based workflow where student identity and course-section information can be used to organize server access.

The system is particularly useful for courses where:

- Students are divided into multiple sections
- Course communication occurs through Discord
- Access needs to be restricted by course/section
- Student registration information is maintained in structured datasets
- Administrative role assignment would otherwise require repetitive manual work

## Privacy Notice

This repository intentionally does **not** contain the original course registration spreadsheet used during development.

Anyone deploying this project should:

- Use their own registration dataset.
- Keep student information private.
- Never commit confidential spreadsheets to Git.
- Never publish Discord bot tokens.
- Use environment variables or a secure secret-management system for credentials.

## Future Improvements

Potential extensions include:

- Web-based administrative dashboard
- Database-backed student management
- Automated registration synchronization
- Improved authentication and verification
- Multi-course support
- Automated student onboarding
- Audit logging
- Administrative analytics
- Integration with university LMS platforms
- More granular permission management

## Author

**Raisul Kabir News**

GitHub:  
https://github.com/RaisulKabir27

## License

This project is provided for educational and academic purposes.

If you reuse or extend the project, please ensure that you do not expose private student information, credentials, or other sensitive data.
