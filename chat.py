import os
import sys

# This makes sure Python can find the brain folder
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from colorama import Fore, Style, init
from brain.query_handler import get_answer

init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print(Fore.CYAN + "=" * 60)
    print(Fore.CYAN + "   DISHA — Department Intelligent Smart Helper Assistant")
    print(Fore.CYAN + "   Your Academic Assistant")
    print(Fore.CYAN + "   Type 'quit' or 'bye' to exit")
    print(Fore.CYAN + "=" * 60)
    print()

def print_disha(text):
    print(Fore.GREEN + "🤖 DISHA : " + Style.RESET_ALL + text)
    print()

def print_user(text):
    pass  # user input is already shown by input()

def chat():
    clear_screen()
    print_banner()

    print_disha("Hello! I am DISHA, your Department Intelligent Smart Helper Assistant.")
    print_disha("I can answer questions about:")
    print(Fore.CYAN + "   • Classroom and lab locations")
    print(Fore.CYAN + "   • Faculty information and qualifications")
    print(Fore.CYAN + "   • Latest announcements and notices")
    print(Fore.CYAN + "   • Department history, facilities and placements")
    print()
    print(Fore.CYAN + "   Example questions you can ask:")
    print(Fore.CYAN + "   → Where is classroom B301?")
    print(Fore.CYAN + "   → Who is Dr. Sharma?")
    print(Fore.CYAN + "   → Any announcements?")
    print(Fore.CYAN + "   → Tell me about department placements")
    print()
    print(Fore.CYAN + "-" * 60)
    print()

    while True:
        try:
            # Get user input
            user_input = input(
                Fore.YELLOW + "🧑 You    : " + Style.RESET_ALL
            ).strip()

            # Skip empty input — just listen again
            if not user_input:
                continue

            # Exit commands
            if user_input.lower() in ["quit", "exit", "bye", "goodbye", "q"]:
                print()
                print_disha("Goodbye! Have a great day. See you soon!")
                break

            # Get answer from DISHA's brain
            answer = get_answer(user_input)

            # Print the answer
            print()
            print_disha(answer)
            print(Fore.CYAN + "-" * 60)
            print()

        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print()
            print()
            print_disha("Goodbye! Have a great day!")
            break

        except Exception as e:
            print()
            print(Fore.RED + f"[ERROR] Something went wrong: {e}")
            print(Fore.RED + "Please try asking your question again.")
            print()

if __name__ == "__main__":
    chat()