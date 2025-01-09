import os
import sys
import requests

from .Channel import Channel


class Bot:
    """
    Bot class to interact with Telegram Bot API.

    Attributes:
        token (str): Bot token.
        first_name (str): Bot's first name.
        username (str): Bot's username.
        json_updates (dict): JSON response from getUpdates.
        chat_count (int): Number of chats bot is part of.
        chat_list (list): List of chats bot is part of.
        commands (list): List of commands.
        channels (dict): Dictionary of channels bot is part of.

    Methods:
        get_me: Get bot information.
        get_updates: Get updates from bot.
        update: Update bot's JSON updates.
        get_chats: Get list of chats bot is part of.
        add_channel: Add channel to bot's channels.
        leave_channel: Leave a channel.
        is_in_channel: Check if bot is part of a channel.
        get_file_count: Get file count in a channel.
        download_file: Download a file from a channel.
        download_all_files: Download all files from a channel.
        send_message: Send a message to a channel.
        delete_message: Delete a message from a channel.
        delete_all_messages: Delete all messages from a channel.
        send_file: Send a file to a channel.
        export_text_messages: Export text messages from a channel.
    """

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

        self.get_me(token)
        self.get_chats()

    def get_me(self, token: str):
        """
        Get bot information.

        Args:
            token (str): Bot token.
        """

        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url)

        if not response.json()["ok"]:
            print("[!] Error: Couldn't get bot information. Token might be invalid.")
            sys.exit(1)

        first_name = response.json()["result"]["first_name"]
        username = response.json()["result"]["username"]

        self.first_name = first_name
        self.username = username

    def get_updates(self, token: str) -> dict:
        """
        Get updates from bot.

        Args:
            token (str): Bot token.

        Returns:
            response.json(): JSON response from getUpdates.
        """

        url = f"https://api.telegram.org/bot{token}/getUpdates"
        response = requests.get(url)

        return response.json()

    def update(self) -> bool:
        """
        Update bot's JSON updates.

        Returns:
            True: If updates are found.
            False: If no updates are found.
        """

        new_json_updates = self.get_updates(self.token)
        if new_json_updates == self.json_updates:
            return False
        else:
            self.json_updates = new_json_updates
            self.get_chats()
            return True

    def get_chats(self):
        """
        Get list of chats bot is part of.
        """
        try:
            if not self.json_updates["ok"]:
                print("[-] Error: Couldn't load chat history.")
                return [""]
        except TypeError:
            return [""]

        chats = []
        left_chats = []

        for chat in self.json_updates["result"]:
            if "message" not in chat:
                continue

            chats.append(
                f'{chat["message"]["chat"].get("title") or "Private Chat"}$$$$${chat["message"]["chat"]["id"]}'
            )

            if "left_chat_member" in chat["message"]:
                left_chats.append(
                    f'{chat["message"]["chat"].get("title") or "Private Chat"}$$$$${chat["message"]["chat"]["id"]}'
                )

        chats = sorted(set(chats), key=lambda x: x.split("$$$$$")[0])
        for chat in left_chats:
            if chat in chats:
                chats.remove(chat)

        for chat in chats:
            self.add_channel(chat.split("$$$$$")[1])

        self.chat_list = chats
        self.chat_count = len(chats)

    def add_channel(self, chat_id: str) -> bool:
        """
        Add channel to bot's channels.

        Args:
            chat_id (str): Chat ID.

        Returns:
            True: If channel is added successfully.
            False: If channel is already in bot's channels.
        """

        if self.is_in_channel(chat_id) and chat_id not in self.channels:
            self.channels[chat_id] = Channel(chat_id, self.token)
            return True
        else:
            return False

    def leave_channel(self, chat_id: str) -> bool:
        """
        Leave a channel.

        Args:
            chat_id (str): Chat ID.

        Returns:
            True: If channel is left successfully.
            False: If not.
        """

        url = f"https://api.telegram.org/bot{self.token}/leaveChat?chat_id={chat_id}"
        response = requests.get(url)

        if response.json()["ok"]:
            return True
        else:
            return False

    def is_in_channel(self, chat_id: str) -> bool:
        """
        Check if bot is part of a channel.

        Args:
            chat_id (str): Chat ID.

        Returns:
            True: If bot is part of the channel.
            False: If not.
        """

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

    def get_file_count(self, chat_id: str) -> tuple[dict, dict]:
        """
        Get file count in a channel.

        Args:
            chat_id (str): Chat ID.

        Returns:
            file_count_dict (dict): Dictionary of file counts.
        """

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

    def download_file(self, file_information: tuple[str, str, str], chat_id: str):
        """
        Download a file from a channel.

        Args:
            file_information (tuple): File information.
            chat_id (str): Chat ID.
        """

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

        if not os.path.exists(chat_id.replace("-", "")):
            os.makedirs(chat_id.replace("-", ""))

        try:
            response = requests.get(download_url)
            response.raise_for_status()

            with open(f"./{chat_id.replace('-', '')}/{file_name}", "wb") as file:
                file.write(response.content)
            print(
                f"File downloaded successfully: ./{chat_id.replace('-', '')}/{file_name}"
            )
        except Exception as e:
            print(f"Error downloading file: {e}")

    def download_all_files(self, chat_id: str, file_type: str | None = None):
        """
        Download all files from a channel.

        Args:
            chat_id (str): Chat ID.
            file_type (str): File type.
        """

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

    def send_message(self, chat_id: str, message: str) -> bool:
        """
        Send a message to a channel.

        Args:
            chat_id (str): Chat ID.
            message (str): Message.

        Returns:
            True: If message is sent successfully.
            False: If not.
        """

        url = f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={chat_id}&text={message}"
        response = requests.get(url)

        return response.json()["ok"]

    def delete_message(self, chat_id: str, message_id: str) -> bool:
        """
        Delete a message from a channel.

        Args:
            chat_id (str): Chat ID.
            message_id (str): Message ID.

        Returns:
            True: If message is deleted successfully.
            False: If not.
        """

        url = f"https://api.telegram.org/bot{self.token}/deleteMessage?chat_id={chat_id}&message_id={message_id}"
        response = requests.get(url)

        return response.json()["ok"]

    def delete_all_messages(self, chat_id: str) -> int:
        """
        Delete all messages from a channel.

        Args:
            chat_id (str): Chat ID.

        Returns:
            message_count (int): Number of messages deleted.
        """

        self.channels[chat_id].get_messages()
        print("[+] Deleting all messages...")

        message_count = 0
        for message in self.channels[chat_id].all_messages_ids:
            if self.delete_message(chat_id, message):
                message_count += 1

        return message_count

    def send_file(self, chat_id: str, file_path: str) -> bool:
        """
        Send a file to a channel.

        Args:
            chat_id (str): Chat ID.
            file_path (str): File path.

        Returns:
            True: If file is sent successfully.
            False: If not.
        """

        url = f"https://api.telegram.org/bot{self.token}/sendDocument?chat_id={chat_id}"
        files = {"document": open(file_path, "rb")}
        response = requests.post(url, files=files)

        return response.json()["ok"]

    def export_text_messages(self, chat_id: str) -> bool:
        """
        Export text messages from a channel.

        Args:
            chat_id (str): Chat ID.

        Returns:
            True: If messages are exported successfully.
            False: If not.
        """

        self.channels[chat_id].get_messages()

        messages = self.channels[chat_id].parsed_messages

        if not messages:
            return False

        if not os.path.exists(chat_id.replace("-", "")):
            os.makedirs(chat_id.replace("-", ""))

        with open(
            f"./{chat_id.replace('-', '')}/messages.txt", "w", encoding="utf-8"
        ) as file:
            for message in messages:
                file.write(message + "\n")

        return True
