import os
import sys
import requests

from Channel import Channel


class Bot:

    token = ""
    first_name = ""
    username = ""
    json_updates = []
    chat_count = 0
    chat_list = []
    commands = []
    channels = {}

    def __init__(self, token):
        self.token = token
        self.first_name, self.username = self.get_me(token)
        self.json_updates = self.get_updates(token)
        self.chat_count = len(self.get_chats())
        self.chat_list = self.get_chats()
        self.commands = []
        self.channels = {}

    def get_me(self, token):
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url)

        if not response.json()["ok"]:
            print("[!] Error: Couldn't get bot information. Token might be invalid.")
            sys.exit(1)

        first_name = response.json()["result"]["first_name"]
        username = response.json()["result"]["username"]

        return first_name, username

    def get_updates(self, token):
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        response = requests.get(url)
        return response.json()

    def update(self):
        new_json_updates = self.get_updates(self.token)
        if new_json_updates == self.json_updates:
            return False
        else:
            self.json_updates = new_json_updates
            return True

    def get_chats(self) -> list[str]:
        if not self.json_updates["ok"]:
            print("[-] Error: Couldn't load chat history.")
            return [""]

        chats = []

        for chat in self.json_updates["result"]:
            if "message" not in chat:
                continue

            chats.append(
                f'{chat["message"]["chat"].get("title") or "Private Chat"} > {chat["message"]["chat"]["id"]}'
            )

        chats = sorted(set(chats), key=lambda x: x.split(" > ")[0])

        for chat in chats:
            self.add_channel(chat.split(" > ")[1])

        return chats

    def add_channel(self, chat_id):
        if self.is_in_channel(chat_id) and chat_id not in self.channels:
            self.channels[chat_id] = Channel(chat_id, self.token)
            return True
        else:
            return False

    def leave_channel(self, chat_id):
        url = f"https://api.telegram.org/bot{self.token}/leaveChat?chat_id={chat_id}"
        response = requests.get(url)

        if response.json()["ok"]:
            print("[+] Successfully left the chat.")
        else:
            print("[-] Couldn't leave the chat.")

    def is_in_channel(self, chat_id):

        url = f"https://api.telegram.org/bot{self.token}/getChat?chat_id={chat_id}"
        response = requests.get(url)
        if response.json()["result"]["type"] == "private":
            return True

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

        self.channels[chat_id].get_messages()
        messages = self.channels[chat_id].all_messages

        for chat in messages:

            if "photo" in chat["result"]:
                file_count_dict["photo"] += 1

            elif "animation" in chat["result"]:
                file_count_dict["gif"] += 1

            elif "document" in chat["result"]:
                file_count_dict["document"] += 1
                extension = chat["result"]["document"]["file_name"].split(".")[-1]

                if extension in document_extensions:
                    document_extensions[extension] += 1
                else:
                    document_extensions[extension] = 1

            elif "voice" in chat["result"]:
                file_count_dict["voice-message"] += 1

            elif "sticker" in chat["result"]:
                file_count_dict["sticker"] += 1

            elif "video" in chat["result"]:
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

    def download_all_files(self, chat_id, file_type=None):

        file_informations = []

        self.channels[chat_id].get_messages()
        messages = self.channels[chat_id].all_messages

        for chat in messages:

            if file_type == "documents":

                if "photo" in chat["result"]:
                    continue

                elif "animation" in chat["result"]:
                    continue

                elif "voice" in chat["result"]:
                    continue

                elif "video" in chat["result"]:
                    continue

                elif "document" in chat["result"]:
                    document = chat["result"]["document"]
                    file_informations.append(
                        [document["file_id"], document["file_name"], None]
                    )

            elif file_type == "media":
                if "photo" in chat["result"]:
                    photo = chat["result"]["photo"][-1]
                    file_informations.append(
                        [photo["file_id"], photo["file_unique_id"], "png"]
                    )

                elif "animation" in chat["result"]:
                    continue

                elif "voice" in chat["result"]:
                    voice = chat["result"]["voice"]
                    file_informations.append(
                        [voice["file_id"], voice["file_unique_id"], "mp3"]
                    )

                elif "video" in chat["result"]:
                    video = chat["result"]["video"]
                    file_informations.append(
                        [video["file_id"], video["file_unique_id"], "mp4"]
                    )

            else:
                if "photo" in chat["result"]:
                    photo = chat["result"]["photo"][-1]
                    file_informations.append(
                        [photo["file_id"], photo["file_unique_id"], "png"]
                    )

                elif "animation" in chat["result"]:
                    continue

                elif "voice" in chat["result"]:
                    voice = chat["result"]["voice"]
                    file_informations.append(
                        [voice["file_id"], voice["file_unique_id"], "mp3"]
                    )

                elif "video" in chat["result"]:
                    video = chat["result"]["video"]
                    file_informations.append(
                        [video["file_id"], video["file_unique_id"], "mp4"]
                    )

                elif "document" in chat["result"]:
                    document = chat["result"]["document"]
                    file_informations.append(
                        [document["file_id"], document["file_name"], None]
                    )

        for file_information in file_informations:
            self.download_file(file_information, chat_id)

    def send_message(self, chat_id, message):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={chat_id}&text={message}"
        response = requests.get(url)

        return response.json()["ok"]

    def delete_message(self, chat_id, message_id):
        url = f"https://api.telegram.org/bot{self.token}/deleteMessage?chat_id={chat_id}&message_id={message_id}"
        response = requests.get(url)

        if not response.json()["ok"]:
            print(f"[-] Couldn't delete message: {message_id}")
            return False

        return response.json()["ok"]

    def delete_all_messages(self, chat_id):
        messages = self.channels[chat_id].get_messages()
        message_count = 0
        for message in messages:
            message_count += 1
            self.delete_message(chat_id, message["message_id"])

        return message_count

    def send_file(self, chat_id, file_path):
        url = f"https://api.telegram.org/bot{self.token}/sendDocument?chat_id={chat_id}"
        files = {"document": open(file_path, "rb")}
        response = requests.post(url, files=files)

        return response.json()["ok"]

    def export_text_messages(self, chat_id):
        self.channels[chat_id].get_messages()

        messages = self.channels[chat_id].parsed_messages

        if not messages:
            return False

        if not os.path.exists(chat_id):
            os.makedirs(chat_id)

        with open(f"./{chat_id}/messages.txt", "w") as file:
            for message in messages:
                file.write(message)

        return True
