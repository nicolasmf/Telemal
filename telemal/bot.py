import os
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

        users_informations = response.json()["result"]

        admins = []

        for user in users_informations:
            admins.append(
                User(
                    id=user["user"]["id"],
                    is_bot=user["user"]["is_bot"],
                    status=user["status"],
                    first_name=user["user"]["first_name"],
                    username=user["user"].get("username"),
                    is_anonymous=user["is_anonymous"],
                )
            )

        return (invite_link, sorted(permissions), admins)

    def get_user_count(self, chat_id):
        url = f"https://api.telegram.org/bot{self.token}/getChatMembersCount?chat_id={chat_id}"
        response = requests.get(url)

        return response.json()["result"]

    def leave_channel(self, chat_id):
        url = f"https://api.telegram.org/bot{self.token}/leaveChat?chat_id={chat_id}"
        response = requests.get(url)

        if response.json()["ok"]:
            print("[+] Successfully left the chat.")
        else:
            print("[-] Couldn't leave the chat.")

    def is_in_channel(self, chat_id):
        url = f"https://api.telegram.org/bot{self.token}/getChatAdministrators?chat_id={chat_id}"
        response = requests.get(url)

        if response.json()["ok"]:
            return True
        else:
            return False

    def get_file_count(self, chat_id):
        file_count_dict = {
            "gif": 0,
            "photo": 0,
            "video": 0,
            "sticker": 0,
            "document": 0,
            "voice-message": 0,
        }

        document_extensions = {}

        for chat in self.json_updates["result"]:

            if "message" not in chat:
                continue

            if str(chat["message"]["chat"]["id"]) != chat_id:
                continue

            if "photo" in chat["message"]:
                file_count_dict["photo"] += 1

            elif "animation" in chat["message"]:
                file_count_dict["gif"] += 1

            elif "document" in chat["message"]:
                file_count_dict["document"] += 1
                extension = chat["message"]["document"]["file_name"].split(".")[-1]

                if extension in document_extensions:
                    document_extensions[extension] += 1
                else:
                    document_extensions[extension] = 1

            elif "voice" in chat["message"]:
                file_count_dict["voice-message"] += 1

            elif "sticker" in chat["message"]:
                file_count_dict["sticker"] += 1

            elif "video" in chat["message"]:
                file_count_dict["video"] += 1

        return file_count_dict, document_extensions

    def download_file(self, file_information, chat_id):

        file_id = file_information[0]
        file_name = file_information[1]
        if file_information[2]:
            file_name = f"{file_name}.{file_information[2]}"

        url = f"https://api.telegram.org/bot{self.token}/getFile?file_id={file_id}"
        response = requests.get(url)

        if not response.json()["ok"]:
            print("[-] File exceeded maximum size.")
            return

        file_path = response.json()["result"]["file_path"]

        download_url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"

        if not os.path.exists(chat_id):
            os.makedirs(chat_id)

        try:
            response = requests.get(download_url)
            response.raise_for_status()

            with open(f"./{chat_id}/{file_name}", "wb") as file:
                file.write(response.content)
            print(f"File downloaded successfully: {file_name}")
        except Exception as e:
            print(f"Error downloading file: {e}")

    def download_all_files(self, chat_id):

        file_informations = []

        for chat in self.json_updates["result"]:

            if "message" not in chat:
                continue

            if str(chat["message"]["chat"]["id"]) != chat_id:
                continue

            if "photo" in chat["message"]:
                photo = chat["message"]["photo"][-1]
                file_informations.append(
                    [photo["file_id"], photo["file_unique_id"], "png"]
                )

            elif "animation" in chat["message"]:
                continue

            elif "document" in chat["message"]:
                document = chat["message"]["document"]
                file_informations.append(
                    [document["file_id"], document["file_name"], None]
                )

            elif "voice" in chat["message"]:
                voice = chat["message"]["voice"]
                file_informations.append(
                    [voice["file_id"], voice["file_unique_id"], "mp3"]
                )

            elif "video" in chat["message"]:
                video = chat["message"]["video"]
                file_informations.append(
                    [video["file_id"], video["file_unique_id"], "mp4"]
                )

        for file_information in file_informations:
            self.download_file(file_information, chat_id)
