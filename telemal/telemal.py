import os
import sys
from bot import Bot


def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def remove_last_lines(n=1):
    for _ in range(n):
        sys.stdout.write("\033[F")  # Cursor up one line
        sys.stdout.write("\033[K")  # Clear to the end of the line


def list_chats(bot: Bot):
    chats = bot.chat_list

    if len(chats) > 1:
        print("[+] Multiple chats found. Please specify a chat id :")
        for chat in chats:
            print(f"    - {chat}")

        chat_id = str(input("Chat ID > "))

        while chat_id not in [chat.split(" > ")[1] for chat in chats]:
            print("[-] Error: Invalid chat ID.")
            chat_id = str(input("Chat ID > "))

    else:
        chat_id = chats[0]

    chat_name = [
        chat.split(" > ")[0] for chat in chats if chat.split(" > ")[1] == chat_id
    ][0]

    channel_menu(bot, chat_id, chat_name)


def chat_history(bot: Bot, chat_id):
    all_messages = bot.parse_messages(chat_id)

    for message in all_messages:
        print(message)


def main_menu(token=None):
    clear_screen()
    logo = """
████████╗███████╗██╗     ███████╗███╗   ███╗ █████╗ ██╗     
╚══██╔══╝██╔════╝██║     ██╔════╝████╗ ████║██╔══██╗██║     
   ██║   █████╗  ██║     █████╗  ██╔████╔██║███████║██║     
   ██║   ██╔══╝  ██║     ██╔══╝  ██║╚██╔╝██║██╔══██║██║     
   ██║   ███████╗███████╗███████╗██║ ╚═╝ ██║██║  ██║███████╗
   ╚═╝   ╚══════╝╚══════╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝
    Telegram Bot Control Toolkit
    
    """

    print(logo)

    if not token:
        token = input("[+] Enter bot token > ")
        remove_last_lines()

    TelegramBot = Bot(token)

    print("[Main Menu]\n")

    print(f"[+] Bot {TelegramBot.first_name} loaded successfully.")

    if TelegramBot.chat_count > 1:
        print(f"\033[1m[!] Bot is part of {TelegramBot.chat_count} channels\033[0m\n")

        print("1. List all channels the bot is in.")
        print("2. Enter a chat id.")
        print("0. Exit.")

        case = input("\n>>> ")

        if case == "1":
            list_chats(TelegramBot)
        elif case == "2":
            print("Not implemented yet.")
        elif case == "0":
            sys.exit(0)
    else:
        channel_menu(TelegramBot)

    input("\n[+] Press any key to go back...")

    main_menu(token)


def print_channel_informations(bot: Bot, chat_id):
    invite_link, permissions, users = bot.get_chat_information(chat_id)

    for index, permission in enumerate(permissions):
        if permission in ["can_send_messages", "can_delete_messages"]:
            permissions[index] = f"\033[1m{permission}\033[0m"

    print(f"[+] Chat ID: {chat_id}")
    print(f"[+] Invite Link: {invite_link}")

    print(f"[+] Permissions:", end=" ")
    print(*permissions, sep=", ")

    print(f"\n[+] Users: {len(users)}")
    for user in users:
        print(f"    - {user}")


def channel_menu(bot: Bot, chat_id=None, chat_name=None):
    clear_screen()

    if not chat_id:
        chat_id = bot.chat_list[0].split(" > ")[1]

    if not chat_name:
        chat_name = bot.chat_list[0].split(" > ")[0]

    logo = """
████████╗███████╗██╗     ███████╗███╗   ███╗ █████╗ ██╗     
╚══██╔══╝██╔════╝██║     ██╔════╝████╗ ████║██╔══██╗██║     
   ██║   █████╗  ██║     █████╗  ██╔████╔██║███████║██║     
   ██║   ██╔══╝  ██║     ██╔══╝  ██║╚██╔╝██║██╔══██║██║     
   ██║   ███████╗███████╗███████╗██║ ╚═╝ ██║██║  ██║███████╗
   ╚═╝   ╚══════╝╚══════╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝
    Telegram Bot Control Toolkit
    
    """

    print(logo)

    print(f"[Channel: {chat_name}]\n")

    print_channel_informations(bot, chat_id)

    print("")

    print("1. List all messages.")
    print("2. Send a message.")
    print("3. Send a file.")
    print("3. Download files.")
    print("4. Delete all messages.")
    print("5. Export all text messages.")
    print("6. Leave channel.")
    print("0. Go back.")

    case = input("\n>>> ")
    print()

    if case == "1":
        chat_history(bot, chat_id)

        input("\n[+] Press any key to go back...")
    elif case == "2":
        print("Not implemented yet.")
    elif case == "3":
        print("Not implemented yet.")
    elif case == "4":
        print("Not implemented yet.")
    elif case == "5":
        print("Not implemented yet.")
    elif case == "6":
        bot.leave_channel(chat_id)

        input("\n[+] Press any key to go back...")
    elif case == "0":
        main_menu(bot.token)
    else:
        print("[!] Invalid option.")
        input("[+] Press any key to go back...")

    channel_menu(bot, chat_id, chat_name)


main_menu()
