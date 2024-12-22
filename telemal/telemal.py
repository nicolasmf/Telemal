import os
import sys
import pickle
import platform

from .Bot import Bot

if "android" in platform.platform():
    LOGO = """
▗▄▄▄▖▗▄▄▄▖▗▖   ▗▄▄▄▖▗▖  ▗▖ ▗▄▖ ▗▖   
  █  ▐▌   ▐▌   ▐▌   ▐▛▚▞▜▌▐▌ ▐▌▐▌   
  █  ▐▛▀▀▘▐▌   ▐▛▀▀▘▐▌  ▐▌▐▛▀▜▌▐▌   
  █  ▐▙▄▄▖▐▙▄▄▖▐▙▄▄▖▐▌  ▐▌▐▌ ▐▌▐▙▄▄▖ V1.2.21
  Telegram Bot Control Toolkit  
                            
"""
else:
    LOGO = """
████████╗███████╗██╗     ███████╗███╗   ███╗ █████╗ ██╗     
╚══██╔══╝██╔════╝██║     ██╔════╝████╗ ████║██╔══██╗██║     
   ██║   █████╗  ██║     █████╗  ██╔████╔██║███████║██║     
   ██║   ██╔══╝  ██║     ██╔══╝  ██║╚██╔╝██║██╔══██║██║     
   ██║   ███████╗███████╗███████╗██║ ╚═╝ ██║██║  ██║███████╗
   ╚═╝   ╚══════╝╚══════╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝ V1.2.21
    Telegram Bot Control Toolkit
    
"""


def write_cache(bot: Bot):

    id = bot.token.split(":")[0]

    if not os.path.exists(f"{id}_cache"):
        os.makedirs(f"{id}_cache")

    with open(f"{id}_cache/bot.pkl", "wb") as file:
        pickle.dump(bot, file)

    with open(f"{id}_cache/channels.pkl", "wb") as file:
        pickle.dump(bot.channels, file)


def read_cache(token: str):

    id = token.split(":")[0]

    if os.path.exists(f"{id}_cache"):
        with open(f"{id}_cache/bot.pkl", "rb") as file:
            bot = pickle.load(file)

        with open(f"{id}_cache/channels.pkl", "rb") as file:
            bot.channels = pickle.load(file)

        # Check if bot still exists
        bot.get_me(token)

        return bot


def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def remove_last_lines(n=1):
    for _ in range(n):
        sys.stdout.write("\033[F")  # Cursor up one line
        sys.stdout.write("\033[K")  # Clear to the end of the line


def chat_history(bot: Bot, chat_id: str):
    messages = bot.channels[chat_id].get_messages()
    for message in messages:
        print(message)


def main_menu(token: str | None = None, bot: Bot | None = None):
    clear_screen()

    print(LOGO)

    if not token:
        token = input("[+] Enter bot token > ")
        remove_last_lines()

        bot = read_cache(token)

    if not bot:
        bot = Bot(token)

    print("[Main Menu]\n")

    print(f"[+] Bot {bot.first_name} ({bot.username}) loaded successfully.")

    bot.update()

    if bot.chat_count > 1:
        print(f"\033[1m[!] Bot is part of {bot.chat_count} channels\033[0m\n")

        for i, chat in enumerate(bot.chat_list):
            print(f"{i+1}. Go to channel : {chat.split('$$$$$')[0]}")

        print(f"{bot.chat_count + 1}. Enter a channel ID.")
        print(f"{bot.chat_count + 2}. Get channels updates.")
        print("0. Exit and write cache.\n")

        case = input(">>> ")

        if case == "0":
            write_cache(bot)
            sys.exit(0)
        elif case.isdigit() and int(case) <= bot.chat_count:
            chat_id = bot.chat_list[int(case) - 1].split("$$$$$")[1]
            chat_name = bot.chat_list[int(case) - 1].split("$$$$$")[0]
            channel_menu(bot, chat_id, chat_name)
        elif case == str(bot.chat_count + 1):
            chat_id = input("[+] Enter channel ID > ")
            if not bot.is_in_channel(chat_id):
                print("[-] Error: Bot is not in this channel.")
            else:
                channel_menu(bot, chat_id)
        elif case == str(bot.chat_count + 2):
            if bot.update():
                print("[+] Channels updated successfully.")
            else:
                print("[-] No updates found.")
        else:
            print("[!] Invalid option.")
    elif bot.chat_count == 1:
        print(f"\n1. Go to channel: {bot.chat_list[0].split('$$$$$')[0]}")
        print("2. Enter a channel ID.")
        print("3. Get channels updates.")
        print("0. Exit and write cache.")

        case = input("\n>>> ")

        if case == "1":
            channel_menu(bot)
        elif case == "2":
            chat_id = input("[+] Enter channel ID > ")
            if not bot.is_in_channel(chat_id):
                print("[-] Error: Bot is not in this channel.")
            else:
                channel_menu(bot, chat_id)
        elif case == "3":
            if bot.update():
                print("[+] Channels updated successfully.")
            else:
                print("[-] No updates found.")
        elif case == "0":
            write_cache(bot)
            sys.exit(0)

    else:
        print("[-] Couldn't find any channel.\n")

        print("1. Enter a channel ID.")
        print("2. Get channels updates.")
        print("0. Exit and write cache.")

        case = input("\n>>> ")

        if case == "0":
            write_cache(bot)
            sys.exit(0)
        elif case == "1":
            chat_id = input("[+] Enter channel ID > ")
            if not bot.is_in_channel(chat_id):
                print("[-] Error: Bot is not in this channel.")
            else:
                channel_menu(bot, chat_id)
        elif case == "2":
            if bot.update():
                print("[+] Channels updated successfully.")
            else:
                print("[-] No updates found.")
        else:
            print("[!] Invalid option")

    input("\n[+] Press any key to go back...")

    main_menu(token, bot)


def print_channel_informations(bot: Bot, chat_id: str):

    invite_link = bot.channels[chat_id].invite_link
    permissions = bot.channels[chat_id].bot_permissions
    admins = bot.channels[chat_id].admins

    for index, permission in enumerate(permissions):
        if permission in ["can_send_messages", "can_delete_messages"]:
            permissions[index] = f"\033[1m{permission}\033[0m"

    print(f"[+] Channel ID: {chat_id}")
    print(f"[+] Invite Link: {invite_link}")

    print(f"[+] Permissions:", end=" ")
    print(*permissions, sep=", ")

    print(f"\n[+] Users: {bot.channels[chat_id].user_count}")

    print(f"[+] Administrators: {len(admins)}")
    for admin in admins:
        print(f"    - {admin}")


def channel_menu(bot: Bot, chat_id: str | None = None, chat_name: str | None = None):
    clear_screen()

    if not chat_id:
        chat_id = bot.chat_list[0].split("$$$$$")[1]

    bot.add_channel(chat_id)

    if not chat_name:
        chat_name = bot.channels[chat_id].name

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
            print("Not implemented yet.")

        elif case == "2":
            print("Not implemented yet.")

        elif case == "3":
            print("Not implemented yet.")

        elif case == "0":
            main_menu(bot.token, bot)

        else:
            print("[!] Invalid option.")

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

        elif case == "2":
            message = input("[+] Enter message > ")

            if bot.send_message(chat_id, message):
                print("[+] Message sent successfully.")
            else:
                print("[-] Error: Message could not be sent.")

        elif case == "3":
            try:
                file_path = input("Enter the path of the file to send > ")
                if bot.send_file(chat_id, file_path):
                    print("[+] File sent successfully.")
                else:
                    print("[-] Error: File could not be sent.")
            except FileNotFoundError:
                print("[-] Error: File not found.")

        elif case == "4":
            file_menu(bot, chat_id, chat_name)

        elif case == "5":
            print(
                "[?] This will only delete messages sent less than 48 hours ago, because of Telegram's limitations."
            )

            messages_count = bot.delete_all_messages(chat_id)
            remove_last_lines()

            if messages_count == 0:
                print("[-] No messages deleted.")
            else:
                print(f"[+] {messages_count} messages deleted.")

        elif case == "6":
            bot.export_text_messages(chat_id)
            print(
                f"[+] Messages exported to ./{chat_id.replace('-', '')}/messages.txt."
            )

        elif case == "7":
            if bot.leave_channel(chat_id):
                print("[+] Successfully left the chat.")
            else:
                print("[-] Couldn't leave the chat.")

        elif case == "0":
            main_menu(bot.token, bot)

        else:
            print("[!] Invalid option.")

    input("\n[+] Press any key to go back...")

    channel_menu(bot, chat_id, chat_name)


def file_menu(bot: Bot, chat_id: str, chat_name: str):
    clear_screen()

    print(LOGO)

    print(f"[File Download Menu] - Channel: {chat_name}\n")

    file_count_dict, document_extensions = bot.get_file_count(chat_id)

    file_count = sum(file_count_dict.values())

    if file_count == 0:
        print("[-] No files found.\n")
        input("[+] Press any key to go back...")
        return channel_menu(bot, chat_id, chat_name)

    print(f"[+] Files Count: {file_count}")

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
                bot.download_all_files(chat_id, "documents")
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
                bot.download_all_files(chat_id, "documents")
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


def main():
    try:
        main_menu()
    except KeyboardInterrupt or EOFError:
        print("\n[-] Exiting...")
        sys.exit(0)
