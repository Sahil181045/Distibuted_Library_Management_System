import xmlrpc.client
from os import getpid

manager_counter = 0


def calc_req_recv_timestamp(recv_timestamp, counter):
    return max(recv_timestamp, counter)+1


def send_addBook_request(proxy, pid):
    global manager_counter
    manager_counter += 1

    title = input("Enter title of the book: ")
    author = input("Enter name of author: ")
    quantity = int(input("Enter number of copies: "))

    timestamp = proxy.addBook(title, author, quantity, pid, manager_counter)
    manager_counter = calc_req_recv_timestamp(timestamp, manager_counter)

    # print("\nAdd Book request sent from Manager Process:",
    #       pid, "at Lamport Timestamp:", manager_counter)
    # print()


def send_viewBooks_request(proxy, pid):
    global manager_counter
    manager_counter += 1

    books, timestamp = proxy.viewBooks(pid, manager_counter)
    manager_counter = calc_req_recv_timestamp(timestamp, manager_counter)

    # print("View Books request sent from Manager Process:",
    #       pid, "at Lamport Timestamp:", manager_counter)
    # print()

    print("Available books:")
    for book in books:
        print(book, end="\n")
    print()


def send_deleteBook_request(proxy, pid):
    send_viewBooks_request(proxy, pid)

    global manager_counter
    manager_counter += 1

    title = input("Enter title of book to delete: ")

    timestamp = proxy.deleteBook(title, pid, manager_counter)
    manager_counter = calc_req_recv_timestamp(timestamp, manager_counter)

    # print("\nDelete Book request sent from Manager Process:",
    #       pid, "at Lamport Timestamp:", manager_counter)
    # print()


def main():

    # Define a proxy to use it to invoke the function
    proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")

    pid = getpid()
    choice = 0

    while True:
        print()
        print("--------Menu---------")
        print("|1: Add Book        |")
        print("|2: Delete Book     |")
        print("|3: View Books      |")
        print("|4: Exit            |")
        print("---------------------")
        choice = int(input("\nEnter your choice: "))
        print()

        if choice == 1:
            send_addBook_request(proxy, pid)

        elif choice == 2:
            send_deleteBook_request(proxy, pid)

        elif choice == 3:
            send_viewBooks_request(proxy, pid)

        elif choice == 4:
            break

        else:
            print("Invalid Input")


if __name__ == "__main__":
    main()
