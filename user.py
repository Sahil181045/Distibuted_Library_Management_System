import xmlrpc.client
from os import getpid

user_counter = 0


def send_load_balancer_request(proxy):
    return proxy.round_robin()


def calc_req_recv_timestamp(recv_timestamp, counter):
    return max(recv_timestamp, counter)+1


def send_viewBooks_request(proxy, pid):
    global user_counter
    user_counter += 1

    books, timestamp = proxy.viewBooks(pid, user_counter)
    user_counter = calc_req_recv_timestamp(timestamp, user_counter)

    # print("View Books request sent from User Process:",
    #       pid, "at Lamport Timestamp:", user_counter)
    # print()

    print("Available books:")
    for book in books:
        print(book, end="\n")
    print()


def send_viewBorrowedBooks_request(proxy, pid):
    global user_counter
    user_counter += 1

    userName = input("Enter your name: ")

    books, timestamp = proxy.viewBorrowedBooks(userName, pid, user_counter)
    user_counter = calc_req_recv_timestamp(timestamp, user_counter)

    # print("View Borrowed Books request sent from User Process:",
    #       pid, "at Lamport Timestamp:", user_counter)
    # print()

    print("Borrowed books:")
    for book in books:
        print(book, end="\n")
    print()


def send_borrowBook_request(proxy, pid):
    # response = proxy.requestCS(pid)

    # if response != "OK":
    #     print("\nWaiting...\n")
    #     while response != "OK":
    #         sleep(10)
    #         response = proxy.requestCS(pid)

    global user_counter
    user_counter += 1

    send_viewBooks_request(proxy, pid)

    issueTitle = input("Enter title of book you want to borrow: ")
    userName = input("Enter your name: ")

    result, timestamp = proxy.borrowBook(
        issueTitle, userName, pid, user_counter)
    user_counter = calc_req_recv_timestamp(timestamp, user_counter)

    # print("\nBorrow Book request sent from User Process:",
    #       pid, "at Lamport Timestamp:", user_counter)
    # print()

    if result == "SUCCESS":
        print("Borrowed book successfully!")
    else:
        print("Failed to borrow book")

    # proxy.releaseCS(pid)


def send_returnBook_request(proxy, pid):
    send_viewBorrowedBooks_request(proxy, pid)

    global user_counter
    user_counter += 1

    returnTitle = input("Enter title of book you want to return: ")

    timestamp = proxy.returnBook(returnTitle, pid, user_counter)
    user_counter = calc_req_recv_timestamp(timestamp, user_counter)

    # print("\nReturn Book request sent from User Process:",
    #       pid, "at Lamport Timestamp:", user_counter)
    # print()


def main():

    # Define a proxy to use it to invoke the function
    load_balancer = xmlrpc.client.ServerProxy("http://localhost:9000/")
    proxy = []
    proxy.append(xmlrpc.client.ServerProxy("http://localhost:8000/"))
    proxy.append(xmlrpc.client.ServerProxy("http://localhost:8001/"))
    proxy.append(xmlrpc.client.ServerProxy("http://localhost:8002/"))
    proxy.append(xmlrpc.client.ServerProxy("http://localhost:8003/"))

    pid = getpid()
    choice = 0

    while True:
        print()
        print("--------User Menu---------")
        print("|1: Borrow Book          |")
        print("|2: Return Book          |")
        print("|3: View Books           |")
        print("|4: View Borrowed Books  |")
        print("|5: Exit                 |")
        print("--------------------------")
        choice = int(input("\nEnter your choice: "))

        if choice == 1:
            index = send_load_balancer_request(load_balancer)
            print("Sending request to Sever with port number:", (8000+index))
            send_borrowBook_request(proxy[index], pid)

        elif choice == 2:
            index = send_load_balancer_request(load_balancer)
            print("Sending request to Sever with port number:", (8000+index))
            send_returnBook_request(proxy[index], pid)

        elif choice == 3:
            index = send_load_balancer_request(load_balancer)
            print("Sending request to Sever with port number:", (8000+index))
            send_viewBooks_request(proxy[index], pid)

        elif choice == 4:
            index = send_load_balancer_request(load_balancer)
            print("Sending request to Sever with port number:", (8000+index))
            send_viewBorrowedBooks_request(proxy[index], pid)

        elif choice == 5:
            break

        else:
            print("Invalid Input")


if __name__ == "__main__":
    main()
