import requests

from .User import User
from datetime import datetime


class Channel:
    """Documentation for Channel class.

    This class is used to represent a channel in Telegram.

    Attributes:
        id (str): The id of the channel.
        token (str): The token of the bot.
        bot_permissions (list): A list of all bot permissions in the channel.
        name (str): The name of the channel.
        all_messages (list): A list of all messages in the channel.
        all_messages_ids (list): A list of all message ids in the channel.
        parsed_messages (list): A list of all parsed messages in the channel.
        invite_link (str): The invite link of the channel.
        admins (list): A list of all admins in the channel.
        user_count (int): The number of users in the channel.
        last_message_id (int): The id of the last message sent in the channel.

    Methods:
        get_messages(): Gets all messages in the channel.
        parse_message(json_response): Parses a message from a json response.
        get_last_message_id(): Gets the id of the last message sent in the channel.
        delete_message(message_id): Deletes a message from the channel.
        get_chat_information(): Gets information about the channel.
        get_user_count(): Gets the number of users in the channel.

    """

    id = ""
    token = ""
    bot_permissions = []
    name = ""
    all_messages = []
    parsed_messages = []
    last_message_id = 0
    invite_link = ""
    admins = []
    user_count = 0
    all_messages_ids = []

    def __init__(
        self,
        id,
        bot_token,
    ):
        self.id = id
        self.token = bot_token
        self.invite_link, self.bot_permissions, self.admins, self.name = (
            self.get_chat_information()
        )
        self.user_count = self.get_user_count()

    def get_messages(self) -> list[str]:
        """
        Gets all messages in the channel.

        Returns:
            A list of all parsed messages in the channel.
        """

        parsed_message = []

        last_message_id = self.get_last_message_id()
        self.delete_message(last_message_id)

        if last_message_id == -1:
            print("[-] Error: Couldn't get last message id.")
            return [""]

        all_messages = []

        if last_message_id == self.last_message_id + 1:
            return self.parsed_messages

        # Get all messages using forwardMessage method
        for message_id in range(
            self.last_message_id + 1,
            last_message_id,
        ):

            percentage = int((message_id / last_message_id) * 100)
            print(
                f"[+] Loading all channel messages... [{percentage}%]",
                flush=True,
                end="\r",
            )

            # protect_content=true is used to prevent the forwarded message from being forwarded again.
            url = f"https://api.telegram.org/bot{self.token}/forwardMessage?chat_id={self.id}&from_chat_id={self.id}&message_id={message_id}&disable_notification=true&protect_content=true"
            response = requests.get(url)

            if not response.json()["ok"]:
                continue
            all_messages.append(response.json())
            self.all_messages_ids.append(message_id)

            forwarded_message_id = response.json()["result"]["message_id"]

            self.delete_message(forwarded_message_id)

            parsed_message.append(self.parse_message(response.json()))

            print(
                "                                                    ",
                flush=True,
                end="\r",
            )

        print(
            "                                                    ",
            flush=True,
            end="\r",
        )

        try:
            self.last_message_id = forwarded_message_id
        except UnboundLocalError:
            pass
        self.all_messages += all_messages
        self.parsed_messages += parsed_message

        return self.parsed_messages

    def parse_message(self, json_response) -> str:
        """
        Parses a message from a json response.

        Args:
            json_response: A json response from the Telegram API.

        Returns:
            A string representing the parsed message.
        """

        message = []

        username = (
            json_response["result"].get("forward_sender_name")
            or json_response["result"]["forward_origin"]["sender_user"].get("username")
            or json_response["result"]["forward_origin"]["sender_user"]["first_name"]
        )

        epoch_time = json_response["result"]["forward_date"]
        dt = datetime.fromtimestamp(epoch_time)
        date = dt.strftime("%Y-%m-%d %H:%M:%S")

        """ if "new_chat_member" in json_response["message"]:
            message = (
                f'[+] {chat["message"]["new_chat_member"]["first_name"]} joined the chat.'
            )

        elif "left_chat_member" in json_response["message"]:
            left_username = chat["message"]["left_chat_member"].get(
                "username"
            ) or json_response["message"]["left_chat_member"].get("first_name")

            if username != left_username:
                message = (
                    f"[+] {username} removed {left_username} from the chat."
                )
            else:
                message = (f"[+] {username} left the chat.") """

        if "photo" in json_response["result"]:
            message = f'{date} - {username}: [Photo] {json_response["result"].get("caption") or ""}'

        elif "animation" in json_response["result"]:
            message = f"{username}: [GIF]"

        elif "voice" in json_response["result"]:
            message = f"{date} - {username}: [Voice Message - {json_response['result']['voice']['duration']}s]"

        elif "sticker" in json_response["result"]:
            message = f"{date} - {username}: [Sticker]"

        elif "video" in json_response["result"]:
            message = f"{date} - {username}: [Video - {json_response['message']['video']['duration']}s]"

        elif "document" in json_response["result"]:
            message = f'{date} - {username}: [{json_response["result"]["document"]["file_name"]}] {json_response["result"].get("caption") or ""}'

        else:
            text = json_response["result"]["text"]
            message = f"{date} - {username}: {text}"

        return message

    def get_last_message_id(self) -> int:
        """
        Gets the id of the last message sent in the channel.

        Returns:
            An integer representing the id of the last message sent in the channel.
        """
        url = f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={self.id}&text=.&disable_notification=true"
        response = requests.get(url)

        if not response.json()["ok"]:
            return -1

        return response.json()["result"]["message_id"]

    def delete_message(self, message_id) -> bool:
        """
        Deletes a message from the channel.

        Args:
            message_id: An integer representing the id of the message to delete.

        Returns:
            A boolean representing whether the message was deleted successfully.
        """

        url = f"https://api.telegram.org/bot{self.token}/deleteMessage?chat_id={self.id}&message_id={message_id}"
        response = requests.get(url)

        if not response.json()["ok"]:
            print(f"[-] Couldn't delete message: {message_id}")
            return False

        return response.json()["ok"]

    def get_chat_information(self) -> tuple[str, list[str], list[User], str]:
        """
        Gets information about the channel.

        Returns:
            A tuple containing the channel's invite link, permissions, admins, and name.
        """

        url = f"https://api.telegram.org/bot{self.token}/getChat?chat_id={self.id}"
        response = requests.get(url)

        permissions = []

        invite_link = response.json()["result"].get("invite_link") or "N/A"
        all_permissions = response.json()["result"].get("permissions")

        if all_permissions:
            for permission in all_permissions:
                if all_permissions[permission]:
                    permissions.append(permission)

        chat_name = response.json()["result"].get("title") or "Private Chat"

        if chat_name == "Private Chat":
            url = f"https://api.telegram.org/bot{self.token}/getChat?chat_id={self.id}"
            response = requests.get(url)

            admin = [
                User(
                    id=response.json()["result"]["id"],
                    is_bot=False,
                    status="creator",
                    first_name=response.json()["result"]["first_name"],
                    username=None,
                    is_anonymous=False,
                )
            ]

            return (invite_link, ["None"], admin, chat_name)

        url = f"https://api.telegram.org/bot{self.token}/getChatAdministrators?chat_id={self.id}"
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

        return (invite_link, sorted(permissions), admins, chat_name)

    def get_user_count(self) -> int:
        """
        Gets the number of users in the channel.

        Returns:
            An integer representing the number of users in the channel.
        """

        url = f"https://api.telegram.org/bot{self.token}/getChatMembersCount?chat_id={self.id}"
        response = requests.get(url)

        return response.json()["result"]
