import os
import sys
from bot import Bot

LOGO = """
████████╗███████╗██╗     ███████╗███╗   ███╗ █████╗ ██╗     
╚══██╔══╝██╔════╝██║     ██╔════╝████╗ ████║██╔══██╗██║     
   ██║   █████╗  ██║     █████╗  ██╔████╔██║███████║██║     
   ██║   ██╔══╝  ██║     ██╔══╝  ██║╚██╔╝██║██╔══██║██║     
   ██║   ███████╗███████╗███████╗██║ ╚═╝ ██║██║  ██║███████╗
   ╚═╝   ╚══════╝╚══════╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝
    Telegram Bot Control Toolkit
    
"""


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

    print(LOGO)

    if not token:
        token = input("[+] Enter bot token > ")
        remove_last_lines()

    TelegramBot = Bot(token)

    print("[Main Menu]\n")

    print(
        f"[+] Bot {TelegramBot.first_name} ({TelegramBot.username}) loaded successfully."
    )

    if TelegramBot.chat_count > 1:
        print(f"\033[1m[!] Bot is part of {TelegramBot.chat_count} channels\033[0m\n")

        for i, chat in enumerate(TelegramBot.chat_list):
            print(f"{i+1}. Go to channel : {chat.split(' > ')[0]}")

        print(f"{TelegramBot.chat_count + 1}. Get channels updates.")
        print("0. Exit.\n")

        case = input(">>> ")

        if case == "0":
            sys.exit(0)
        elif case.isdigit() and int(case) <= TelegramBot.chat_count:
            chat_id = TelegramBot.chat_list[int(case) - 1].split(" > ")[1]
            chat_name = TelegramBot.chat_list[int(case) - 1].split(" > ")[0]
            channel_menu(TelegramBot, chat_id, chat_name)
        elif case == str(TelegramBot.chat_count + 1):
            if TelegramBot.update():
                print("[+] Channels updated successfully.")
            else:
                print("[-] No updates found.")
        else:
            print("[!] Invalid option.")
    else:
        print(f"\n1. Go to channel: {TelegramBot.chat_list[0].split(' > ')[0]}")
        print("0. Exit.")

        case = input("\n>>> ")

        if case == "1":
            channel_menu(TelegramBot)
        elif case == "0":
            sys.exit(0)

    input("\n[+] Press any key to go back...")

    main_menu(token)


def print_channel_informations(bot: Bot, chat_id):
    invite_link, permissions, admins = bot.get_chat_information(chat_id)

    for index, permission in enumerate(permissions):
        if permission in ["can_send_messages", "can_delete_messages"]:
            permissions[index] = f"\033[1m{permission}\033[0m"

    print(f"[+] Channel ID: {chat_id}")
    print(f"[+] Invite Link: {invite_link}")

    print(f"[+] Permissions:", end=" ")
    print(*permissions, sep=", ")

    print(f"\n[+] Users: {bot.get_user_count(chat_id)}")

    print(f"[+] Administrators: {len(admins)}")
    for admin in admins:
        print(f"    - {admin}")


def channel_menu(bot: Bot, chat_id=None, chat_name=None):
    clear_screen()

    if not chat_id:
        chat_id = bot.chat_list[0].split(" > ")[1]

    if not chat_name:
        chat_name = bot.chat_list[0].split(" > ")[0]

    print(LOGO)

    if not bot.is_in_channel(chat_id):
        print(f"[Channel: {chat_name}] - Bot is not in the channel anymore.\n")

        print(f"[+] Channel ID: {chat_id}\n")

        print("1. List all messages.")
        print("2. Download files.")
        print("3. Export all text messages.")
        print("0. Go back.")

        case = input("\n>>> ")
        print()

        if case == "1":
            chat_history(bot, chat_id)

            input("\n[+] Press any key to go back...")
        elif case == "2":
            file_menu(bot, chat_id, chat_name)
        elif case == "3":
            print("Not implemented yet.")
        elif case == "0":
            main_menu(bot.token)
        else:
            print("[!] Invalid option.")
            input("[+] Press any key to go back...")

    else:
        print(f"[Channel: {chat_name}]\n")

        print_channel_informations(bot, chat_id)

        print("")

        print("1. List all messages.")
        print("2. Send a message.")
        print("3. Send a file.")
        print("4. Download files.")
        print("5. Delete all messages.")
        print("6. Export all text messages.")
        print("7. Leave channel.")
        print("0. Go back.")

        case = input("\n>>> ")

        if case == "1":
            chat_history(bot, chat_id)

            input("\n[+] Press any key to go back...")
        elif case == "2":
            print("Not implemented yet.")
        elif case == "3":
            print("Not implemented yet.")
        elif case == "4":
            file_menu(bot, chat_id, chat_name)
        elif case == "5":
            print("Not implemented yet.")
        elif case == "6":
            print("Not implemented yet.")
        elif case == "7":
            bot.leave_channel(chat_id)

            input("\n[+] Press any key to go back...")
        elif case == "0":
            main_menu(bot.token)
        else:
            print("[!] Invalid option.")
            input("[+] Press any key to go back...")

    channel_menu(bot, chat_id, chat_name)


def file_menu(bot: Bot, chat_id, chat_name):
    clear_screen()

    print(LOGO)

    print(f"[File Download Menu] - Channel: {chat_name}\n")

    file_count_dict, document_extensions = bot.get_file_count(chat_id)

    file_count = sum(file_count_dict.values())

    print(f"[+] Files Count: {file_count}")

    if file_count == 0:
        print("[-] No files found.\n")
        input("[+] Press any key to go back...")
        return channel_menu(bot, chat_id, chat_name)

    print("[+] File Types:")
    for file_type, count in file_count_dict.items():
        if count > 0:
            print(f"    - {file_type.capitalize()}: {count}")

    if document_extensions:
        print("[+] Document Extensions:")
        for extension, count in document_extensions.items():
            print(f"    - {extension}: {count}")

    print("")
    print("1. Download all files.")

    if document_extensions:
        print("2. Download all documents.")
        if file_count_dict["photo"] > 0 or file_count_dict["video"] > 0:
            print("3. Download all media.")
            print("0. Go back.")

            case = input("\n>>> ")

            if case == "1":
                bot.download_all_files(chat_id)
            elif case == "2":
                bot.download_all_files(chat_id, "document")
            elif case == "3":
                bot.download_all_files(chat_id, "media")
            elif case == "0":
                channel_menu(bot, chat_id, chat_name)
            else:
                print("[!] Invalid option.")
        else:
            print("0. Go back.")

            case = input("\n>>> ")

            if case == "1":
                bot.download_all_files(chat_id)
            elif case == "2":
                bot.download_all_files(chat_id, "document")
            elif case == "0":
                channel_menu(bot, chat_id, chat_name)
            else:
                print("[!] Invalid option.")

    elif file_count_dict["photo"] > 0 or file_count_dict["video"] > 0:
        print("2. Download all media.")
        print("0. Go back.")

        case = input("\n>>> ")

        if case == "1":
            bot.download_all_files(chat_id)
        elif case == "2":
            bot.download_all_files(chat_id, "media")
        elif case == "0":
            channel_menu(bot, chat_id, chat_name)
        else:
            print("[!] Invalid option.")

    input("[+] Press any key to go back...")
    file_menu(bot, chat_id, chat_name)


main_menu()
