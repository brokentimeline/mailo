#!/usr/bin/env python3

import json
import sys
import time
import urllib.request
import urllib.error
from typing import Optional, List, Dict, Any, Tuple

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

def color(text: str, fg: str = "", bold: bool = False, dim: bool = False) -> str:
    codes = []
    if bold:
        codes.append(Style.BOLD)
    if dim:
        codes.append(Style.DIM)
    if fg:
        codes.append(getattr(Style, fg.upper(), ""))
    codes.append(text)
    codes.append(Style.RESET)
    return "".join(codes)

API_BASE = "https://api.guerrillamail.com/ajax.php"
USER_AGENT = "mailo-terminal/3.0"

def api_request(params: Dict[str, str]) -> Optional[Any]:
    if "action" in params:
        params["f"] = params.pop("action")
    url = f"{API_BASE}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data) if data else None
    except Exception as e:
        print(color(f"API error: {e}", fg="red"))
        return None

def generate_email() -> Optional[Tuple[str, str, str, str]]:
    params = {"action": "get_email_address"}
    result = api_request(params)
    if result and isinstance(result, dict):
        email = result.get("email_addr")
        sid = result.get("sid_token")
        if email and sid:
            login, domain = email.split("@", 1)
            return login, domain, email, sid
    print(color("Failed to generate email address.", fg="red"))
    return None

def fetch_messages(sid: str) -> List[Dict]:
    params = {"action": "get_email_list", "sid_token": sid, "offset": "0"}
    result = api_request(params)
    if result and isinstance(result, dict):
        return result.get("list", [])
    return []

def fetch_message(sid: str, email_id: int) -> Optional[Dict]:
    params = {"action": "fetch_email", "sid_token": sid, "email_id": str(email_id)}
    result = api_request(params)
    return result if isinstance(result, dict) else None

def html_to_text(html: str) -> str:
    if not html:
        return ""
    import re
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<(br|p|div|h[1-6]|li)[^>]*>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"<[^>]+>", "", html)
    html = html.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    html = re.sub(r"\n\s*\n", "\n\n", html)
    return html.strip()

def print_banner() -> None:
    banner = r"""
╔════════════════════════════════════════════════════════╗
║               M   A   I   L   O                        ║
║           Temporary Email Client for Terminal          ║
║                Powered by Guerrilla Mail               ║
║             made by @govsmail on Telegram              ║
╚════════════════════════════════════════════════════════╝
"""
    print(color(banner, fg="magenta", bold=True))

def print_menu() -> None:
    menu = r"""
╔════════════════════════════════════════════════════════════════╗
║                         M A I L O   M E N U                    ║
╠════════════════════════════════════════════════════════════════╣
║  ➤  1   |  Generate a new temporary email address              ║
║  ➤  2   |  View inbox (full list)                              ║
║  ➤  3   |  Read an email (by number)                           ║
║  ➤  4   |  Auto-refresh inbox (every 10 seconds)               ║
║  ➤  5   |  Copy current address to clipboard                   ║
║  ➤  6   |  Show inbox summary (total / new)                    ║
║  ➤  99  |  Exit                                                ║
╚════════════════════════════════════════════════════════════════╝
"""
    print(color(menu, fg="cyan"))

def print_inbox_table(messages: List[Dict]) -> None:
    if not messages:
        print(color("\n  Inbox is empty. Waiting for emails...", fg="yellow"))
        return

    rows = []
    for idx, msg in enumerate(messages, 1):
        msg_id = msg.get("mail_id", msg.get("id", "?"))
        from_addr = msg.get("mail_from", msg.get("from", "Unknown"))[:35]
        subject = (msg.get("mail_subject", msg.get("subject", "(No subject)")) or "(No subject)")[:45]
        date = msg.get("mail_date", msg.get("date", "Unknown"))[:19]
        rows.append((idx, msg_id, from_addr, subject, date))

    idx_w = max(len(str(r[0])) for r in rows)
    id_w = max(len(str(r[1])) for r in rows)
    from_w = max(len(r[2]) for r in rows)
    subj_w = max(len(r[3]) for r in rows)
    date_w = max(len(r[4]) for r in rows)

    total_w = idx_w + id_w + from_w + subj_w + date_w + 13
    print(color("┌" + "─" * total_w + "┐", fg="cyan"))
    header = f"│ {color('#', bold=True):<{idx_w}}  {color('ID', bold=True):<{id_w}}  {color('From', bold=True):<{from_w}}  {color('Subject', bold=True):<{subj_w}}  {color('Date', bold=True)} │"
    print(header)
    print(color("├" + "─" * total_w + "┤", fg="cyan"))

    for idx, msg_id, from_addr, subject, date in rows:
        line = f"│ {color(str(idx), fg='green'):<{idx_w}}  {str(msg_id):<{id_w}}  {from_addr:<{from_w}}  {subject:<{subj_w}}  {date:<{date_w}} │"
        print(line)

    print(color("└" + "─" * total_w + "┘", fg="cyan"))
    print(color(f"\n  Total messages: {len(messages)}", dim=True))

def print_email(message: Dict[str, Any]) -> None:
    subject = message.get("mail_subject", message.get("subject", "(No subject)"))
    from_addr = message.get("mail_from", message.get("from", "Unknown"))
    date = message.get("mail_date", message.get("date", "Unknown"))
    body = message.get("mail_body", message.get("body", ""))
    if not body:
        body = message.get("mail_html", message.get("html", ""))
        body = html_to_text(body)

    print(color("\n┌─────────────────────────────────────────────────────────────────┐", fg="magenta"))
    print(color(f"│  Subject:  {subject[:60]:<60}", bold=True))
    print(color(f"│  From:     {from_addr[:60]}"))
    print(color(f"│  Date:     {date[:60]}", dim=True))
    print(color("├─────────────────────────────────────────────────────────────────┤", fg="magenta"))

    if body:
        print(color("│  Content:                                                      │", bold=True))
        for line in body.splitlines():
            for chunk in [line[i:i+78] for i in range(0, len(line), 78)]:
                print(f"│  {chunk}")
    else:
        print(color("│  (No text content in this email)                               │", dim=True))

    print(color("└─────────────────────────────────────────────────────────────────┘", fg="magenta"))

def print_summary(total: int, new_count: int) -> None:
    print(color("\n╔════════════════════════════════════════════════════════════╗", fg='cyan'))
    print(color("║                     INBOX SUMMARY                          ║", fg='cyan', bold=True))
    print(color("╠════════════════════════════════════════════════════════════╣", fg='cyan'))
    print(color(f"║  Total messages:  {total:<38} ║", fg='green'))
    print(color(f"║  New messages:    {new_count:<38} ║", fg='yellow'))
    print(color("╚════════════════════════════════════════════════════════════╝", fg='cyan'))

class MailoSession:
    def __init__(self):
        self.login: Optional[str] = None
        self.domain: Optional[str] = None
        self.address: Optional[str] = None
        self.sid: Optional[str] = None
        self.messages: List[Dict] = []
        self.last_message_ids: set = set()

    def is_active(self) -> bool:
        return all([self.login, self.domain, self.address, self.sid])

    def new_address(self) -> bool:
        result = generate_email()
        if result:
            self.login, self.domain, self.address, self.sid = result
            self.messages = []
            self.last_message_ids = set()
            print(color(f"\n  New temporary email: {self.address}", fg="green"))
            time.sleep(1)
            return True
        return False

    def refresh(self, silent: bool = False) -> int:
        if not self.is_active():
            return 0
        new_msgs = fetch_messages(self.sid)
        if new_msgs is None:
            if not silent:
                print(color("  Failed to fetch inbox. Check your network.", fg="red"))
            return 0
        old_ids = self.last_message_ids.copy()
        self.messages = new_msgs
        self.last_message_ids = {m.get("mail_id", m.get("id")) for m in self.messages}
        new_count = len(self.last_message_ids - old_ids)
        if not silent and new_count > 0:
            plural = "s" if new_count > 1 else ""
            print(color(f"\n  {new_count} new message{plural} received!", fg="green"))
        elif not silent and new_count == 0:
            print(color("  No new messages.", dim=True))
        return new_count

    def show_inbox(self) -> None:
        if not self.is_active():
            print(color("No active email address. Use option 1 to create one.", fg="red"))
            return
        self.refresh(silent=True)
        print_inbox_table(self.messages)

    def read_by_number(self, num: int) -> None:
        if not self.is_active():
            print(color("No active email address.", fg="red"))
            return
        if not self.messages:
            print(color("Inbox is empty. Nothing to read.", fg="yellow"))
            return
        if num < 1 or num > len(self.messages):
            print(color(f"Invalid number. Choose 1-{len(self.messages)}.", fg="red"))
            return
        msg = self.messages[num - 1]
        msg_id = msg.get("mail_id", msg.get("id"))
        if not msg_id:
            print(color("Invalid message data.", fg="red"))
            return
        full = fetch_message(self.sid, msg_id)
        if full:
            print_email(full)
        else:
            print(color("Failed to retrieve message content.", fg="red"))

    def show_summary(self) -> None:
        if not self.is_active():
            print(color("No active email address. Use option 1 to create one.", fg="red"))
            return
        old_ids = self.last_message_ids.copy()
        new_count = self.refresh(silent=True)
        print_summary(len(self.messages), new_count)

    def auto_watch(self, interval: int = 10) -> None:
        if not self.is_active():
            print(color("No active email address. Use option 1 first.", fg="red"))
            return
        print(color(f"\n  Auto-refresh mode active (every {interval} seconds)", fg="cyan"))
        print(color("  Press Ctrl+C to stop watching.\n", dim=True))
        try:
            while True:
                self.refresh(silent=False)
                time.sleep(interval)
        except KeyboardInterrupt:
            print(color("\n  Stopped auto-refresh.", fg="yellow"))

    def copy_address(self) -> None:
        if not self.is_active():
            print(color("No active email address.", fg="red"))
            return
        if not CLIPBOARD_AVAILABLE:
            print(color("Clipboard support requires 'pyperclip'. Install it with: pip install pyperclip", fg="red"))
            return
        try:
            pyperclip.copy(self.address)
            print(color(f"  Copied '{self.address}' to clipboard!", fg="green"))
        except Exception as e:
            print(color(f"Failed to copy: {e}", fg="red"))

def main():
    print_banner()
    session = MailoSession()

    if not session.new_address():
        print(color("Cannot connect to Guerrilla Mail API. Please check your network.", fg="red"))
        sys.exit(1)

    print_menu()

    while True:
        try:
            prompt = color(f"\n  [{session.address}] > ", fg="green")
            choice = input(prompt).strip().lower()
        except KeyboardInterrupt:
            print(color("\n\n  Goodbye!", fg="yellow"))
            break
        except EOFError:
            print(color("\n\n  Goodbye!", fg="yellow"))
            break

        if not choice:
            continue

        if choice == "1":
            session.new_address()
        elif choice == "2":
            session.show_inbox()
        elif choice == "3":
            if not session.messages:
                print(color("  Inbox is empty. Nothing to read.", fg="yellow"))
                continue
            try:
                num = int(input(color("  Enter email number: ", fg="cyan")))
                session.read_by_number(num)
            except ValueError:
                print(color("  Invalid input. Please enter a number.", fg="red"))
        elif choice == "4":
            session.auto_watch()
        elif choice == "5":
            session.copy_address()
        elif choice == "6":
            session.show_summary()
        elif choice in ["99", "q", "quit", "exit"]:
            print(color("\n  Goodbye!", fg="yellow"))
            break
        else:
            print(color("  Unknown command.", fg="red"))

if __name__ == "__main__":
    main()