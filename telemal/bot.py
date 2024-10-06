import sys
import requests

from User import User


class Bot:
    def __init__(self, token):
        self.token = token
        self.first_name = self.get_me(token)
        self.json_updates = self.get_updates(token)
        self.chat_count = len(self.get_chats())
        self.chat_list = self.get_chats()

    def get_me(self, token):
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url)

        if not response.json()["ok"]:
            print("[!] Error: Couldn't get bot information. Token might be invalid.")
            sys.exit(1)

        first_name = response.json()["result"]["first_name"]

        return first_name

    def get_updates(self, token):
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        response = requests.get(url)
        return response.json()

    def get_chats(self) -> str:
        if not self.json_updates["ok"]:
            print("[-] Error: Couldn't load chat history.")
            return

        chats = []

        for chat in self.json_updates["result"]:
            if "message" not in chat:
                continue

            chats.append(
                f'{chat["message"]["chat"].get("title") or "Private Conversation"} > {chat["message"]["chat"]["id"]}'
            )

        chats = sorted(set(chats), key=lambda x: x.split(" > ")[0])

        return chats

    def parse_messages(self, chat_id):
        if not self.json_updates["ok"]:
            print("[-] Error: Couldn't load chat history.")
            return

        all_messages = []

        for chat in self.json_updates["result"]:
            if "message" not in chat:
                continue

            if str(chat["message"]["chat"]["id"]) != chat_id:
                continue

            username = chat["message"]["from"].get("username") or chat["message"][
                "from"
            ].get("first_name")
            text = chat["message"].get("text")

            if "new_chat_member" in chat["message"]:
                all_messages.append(
                    f'[+] {chat["message"]["new_chat_member"]["first_name"]} joined the chat.'
                )

            elif "left_chat_member" in chat["message"]:
                left_username = chat["message"]["left_chat_member"].get(
                    "username"
                ) or chat["message"]["left_chat_member"].get("first_name")

                if username != left_username:
                    all_messages.append(
                        f"[+] {username} removed {left_username} from the chat."
                    )
                else:
                    all_messages.append(f"[+] {username} left the chat.")

            elif "photo" in chat["message"]:
                all_messages.append(
                    f'{username}: [Photo] {chat["message"].get("caption") or ""}'
                )

            elif "animation" in chat["message"]:
                all_messages.append(f"{username}: [GIF]")

            elif "document" in chat["message"]:
                all_messages.append(
                    f'{username}: [{chat["message"]["document"]["file_name"]}] {chat["message"].get("caption") or ""}'
                )

            elif "voice" in chat["message"]:
                all_messages.append(
                    f"{username}: [Voice Message - {chat['message']['voice']['duration']}s]"
                )

            elif "sticker" in chat["message"]:
                all_messages.append(f"{username}: [Sticker]")

            elif "video" in chat["message"]:
                all_messages.append(
                    f"{username}: [Video - {chat['message']['video']['duration']}s]"
                )

            else:
                if chat["message"]["from"]["is_bot"]:
                    all_messages.append(f"[bot] {username}: {text}")
                else:
                    all_messages.append(f"{username}: {text}")

        return all_messages

    def get_chat_information(self, chat_id):
        url = f"https://api.telegram.org/bot{self.token}/getChat?chat_id={chat_id}"
        response = requests.get(url)

        permissions = []

        invite_link = response.json()["result"].get("invite_link") or "N/A"
        all_permissions = response.json()["result"].get("permissions")

        for permission in all_permissions:
            if all_permissions[permission]:
                permissions.append(permission)

        url = f"https://api.telegram.org/bot{self.token}/getChatAdministrators?chat_id={chat_id}"
        response = requests.get(url)

        bot_status = response.json()["result"][0]

        for key in bot_status:
            if key.startswith("can_") and bot_status[key]:
                permissions.append(key)

        users_informations = response.json()["result"][1:]

        users = []

        for user in users_informations:
            users.append(
                User(
                    id=user["user"]["id"],
                    is_bot=user["user"]["is_bot"],
                    status=user["status"],
                    first_name=user["user"]["first_name"],
                    username=user["user"].get("username"),
                    is_anonymous=user["is_anonymous"],
                )
            )

        return (invite_link, sorted(permissions), users)

    def leave_channel(self, chat_id):
        url = f"https://api.telegram.org/bot{self.token}/leaveChat?chat_id={chat_id}"
        response = requests.get(url)

        if response.json()["ok"]:
            print("[+] Successfully left the chat.")
        else:
            print("[-] Couldn't leave the chat.")

    def is_in_channel(self, chat_id):
        url = f"https://api.telegram.org/bot{self.token}/getChatMember?chat_id={chat_id}&user_id={self.id}"
        response = requests.get(url)

        if response.json()["ok"]:
            return True
        else:
            return False
