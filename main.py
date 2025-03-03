import time
from file_manager import process_attachments


def main():
    while True:
        process_attachments()
        print("Waiting for new emails...")
        time.sleep(60)

if __name__ == "__main__":
    main()