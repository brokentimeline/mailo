# Mailo - Temporary Email Client for Terminal

Mailo is a lightweight, disposable email client that runs entirely in your terminal. It generates a temporary email address and allows you to receive, read, and manage emails without any registration.

Powered by the [Guerrilla Mail](https://www.guerrillamail.com/) API.

Made by [@govsmail](https://t.me/govsmail) on Telegram.

[Click here for the Mailo Telegram Channel](https://t.me/mailotemp)

## Features

- Generate random temporary email addresses
- View inbox as a formatted table
- Read full email content (plain text and HTML converted)
- Auto-refresh inbox every few seconds
- Copy email address to clipboard (optional)
- Debug mode to inspect raw API responses
- Works on Linux, Windows (Python), Termux (Android), and iSH (iOS)

## Requirements

- Python 3.6 or higher
- Internet connection
- Optional: `pyperclip` for clipboard support

## Installation & Setup Tutorials

### 1. Termux (Android)

1. Open Termux and update packages:
```

pkg update && pkg upgrade

```

2. Install Python and git:
```

pkg install python git

```

3. Clone the repository:
```

git clone https://github.com/brokentimeline/mailo.git
cd mailo

```

4. (Optional) Install clipboard support:
```

pip install pyperclip

```

5. Run Mailo:
```

python mailo.py

```

### 2. iSH Shell (iOS)

1. Open iSH. Update Alpine packages:
```

apk update

```

2. Install Python and git:
```

apk add python3 git

```

3. Clone the repository:
```

git clone https://github.com/brokentimeline/mailo.git
cd mailo

```

4. (Optional) Install clipboard support:
```

pip3 install pyperclip

```

*Note: Clipboard may not work on iSH due to iOS limitations – the script will still run fine.*

5. Run Mailo:
```

python3 mailo.py

```

### 3. Linux (Debian/Ubuntu, Fedora, Arch, etc.)

**Debian/Ubuntu:**
```

sudo apt update
sudo apt install python3 git
git clone https://github.com/brokentimeline/mailo.git
cd mailo
pip3 install pyperclip   # optional
python3 mailo.py

```

**Fedora:**
```

sudo dnf install python3 git
git clone https://github.com/brokentimeline/mailo.git
cd mailo
pip3 install pyperclip   # optional
python3 mailo.py

```

**Arch Linux:**
```

sudo pacman -S python git
git clone https://github.com/brokentimeline/mailo.git
cd mailo
pip install pyperclip    # optional
python mailo.py

```

### 4. Windows (Native Python)

1. Download and install Python from [python.org](https://python.org) (check "Add Python to PATH").

2. Open Command Prompt or PowerShell.

3. Install git (if not already installed) from [git-scm.com](https://git-scm.com) or download the repository as ZIP.

4. Clone the repository:
```

git clone https://github.com/brokentimeline/mailo.git
cd mailo

```

5. (Optional) Install clipboard support:
```

pip install pyperclip

```

6. Run Mailo:
```

python mailo.py

```

### 5. Windows (WSL - Windows Subsystem for Linux)

1. Install WSL and a Linux distribution (e.g., Ubuntu) from Microsoft Store.

2. Open WSL terminal and follow the Linux instructions above.

## Usage

After starting Mailo, you will see a modern banner and an arrow‑style menu:

```

┌─────────────────────────────────────────────────┐
│                    MAILO                       │
├─────────────────────────────────────────────────┤
│  ➤ 1  | New email address                     │
│  ➤ 2  | View inbox                            │
│  ➤ 3  | Read email (by number)                │
│  ➤ 4  | Auto-refresh (10s)                    │
│  ➤ 5  | Copy address to clipboard             │
│  ➤ 6  | Help                                  │
│  ➤ 99 | Exit                                  │
└─────────────────────────────────────────────────┘

```

Type the number or letter and press Enter.

- **1** – Generates a new temporary email address. The old address will no longer work.
- **2** – Shows the inbox with a list of received emails (ID, sender, subject, date).
- **3** – Reads an email. You will be asked to enter the number from the inbox list.
- **4** – Automatically refreshes the inbox every 10 seconds. Press Ctrl+C to stop.
- **5** – Copies the current email address to your clipboard (requires `pyperclip`).
- **6** – Displays the help menu again.
- **d** – Debug mode: prints the raw JSON response from the API. Useful to see if emails are arriving when the inbox appears empty.
- **99** – Exits the program.

## Troubleshooting

### SSL / certificate errors on iSH or Termux
Install CA certificates:
- iSH: `apk add ca-certificates && update-ca-certificates`
- Termux: `pkg install ca-certificates`

### "Failed to generate email address"
- Check your internet connection (`ping 1.1.1.1`)
- Guerrilla Mail API may be temporarily down – wait a few minutes and retry

### Inbox stays empty even after sending an email
- Wait 5–10 seconds – email delivery is not instant.
- Use the **debug command** (`d`) to see the raw API response. If the response shows `"list": []`, the email may have been blocked or the address is invalid. Try generating a new address (option 1) and send the email again.
- Some services block disposable email domains – try a different recipient service.

### Clipboard not working
- Install `pyperclip` (`pip install pyperclip`) – if it still fails, your terminal environment may not support clipboard. The rest of Mailo works without it.

### Python not found
- Make sure Python is installed and the command matches your system (`python` vs `python3`).

## Credits

- Developed by [@govsmail](https://t.me/govsmail) on Telegram
- Powered by Guerrilla Mail API

## License

MIT License – free to use, modify, and distribute.