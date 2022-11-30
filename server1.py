import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
import pymongo

PORT = 8000
proxy = xmlrpc.client.ServerProxy("http://localhost:8001/")

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
dlms = myclient["dlms"]
books = dlms["bookData"]
borrowedBooks = dlms["borrowedBooks"]

server_counter = 0
request_queue = []
cur_critical_section_proc = None


def calc_req_recv_timestamp(recv_timestamp, counter):
    return max(recv_timestamp, counter)+1


def update_server_counter(timestamp):
    global server_counter
    server_counter += 1
    server_counter = calc_req_recv_timestamp(timestamp, server_counter)


def requestCS(pid):
    global request_queue, cur_critical_section_proc
    print(f"\nRECEIVED CRITICAL SECTION REQUEST FROM PROCESS {pid}")

    if not cur_critical_section_proc:
        cur_critical_section_proc = pid
        print("GRANTED PERMISSION")
        return "OK"
    else:
        print(
            f"WAITING FOR PROCESS {cur_critical_section_proc} IN ITS CRITICAL SECTION TO COMPLETE EXECUTING IT'S CRITICAL SECTION...")
        print(f"APPENDING REQUEST FROM PROCESS {pid} in REQUEST QUEUE")
        request_queue.append(pid)
        print("REQUEST QUEUE:", request_queue)
        cur_critical_section_proc = request_queue.pop(0)
        return "WAIT"


def releaseCS(pid):
    global cur_critical_section_proc
    print(f"\nPROCESS {pid} COMPLETED IT'S CRITICAL SECTION")
    cur_critical_section_proc = None


def addBook(title, author, quantity, pid, timestamp):
    update_server_counter(timestamp)

    newEntry = {"title": title, "author": author, "quantity": quantity}
    books.insert_one(newEntry)
    msg = "Book data inserted by Process: {} at Lamport Timestamp: {}".format(
        pid, server_counter)
    # print(msg)
    proxy.addBookServer(title, author, quantity, pid, timestamp)
    return server_counter


def addBookServer(title, author, quantity, pid, timestamp):
    update_server_counter(timestamp)

    newEntry = {"title": title, "author": author, "quantity": quantity}
    books.insert_one(newEntry)
    msg = "Book data inserted by Process: {} at Lamport Timestamp: {}".format(
        pid, server_counter)
    # print(msg)
    return server_counter


def deleteBook(title, pid, timestamp):
    update_server_counter(timestamp)

    bookQuery = {"title": title}
    books.delete_one(bookQuery)
    msg = "Book data deleted by Process: {} at Lamport Timestamp: {}".format(
        pid, server_counter)
    # print(msg)
    proxy.deleteBookServer(title, pid, timestamp)
    return server_counter


def deleteBookServer(title, pid, timestamp):
    update_server_counter(timestamp)

    bookQuery = {"title": title}
    books.delete_one(bookQuery)
    msg = "Book data deleted by Process: {} at Lamport Timestamp: {}".format(
        pid, server_counter)
    # print(msg)
    return server_counter


def viewBooks(pid, timestamp):
    update_server_counter(timestamp)

    li = []
    for item in books.find():
        li.append(str(item))
    msg = "Viewed books for Process: {} at Lamport Timestamp: {}".format(
        pid, server_counter)
    # print(msg)
    return li, server_counter


def viewBorrowedBooks(username, pid, timestamp):
    update_server_counter(timestamp)

    li = []
    for item in borrowedBooks.find({"userName": username}):
        li.append(str(item))
    msg = "Viewed borrowed books for Process: {} at Lamport Timestamp: {}".format(
        pid, server_counter)
    # print(msg)
    return li, server_counter


def borrowBook(issueTitle, userName, pid, timestamp):
    update_server_counter(timestamp)

    issueQuery = {"title": issueTitle}
    currentEntry = books.find_one(issueQuery)
    currentQuantity = 0

    if currentEntry:
        currentQuantity = currentEntry["quantity"]

    if currentQuantity == 0:
        msg = "Borrow book transaction failed by Process: {} at Lamport Timestamp: {}".format(
            pid, server_counter)
        # print(msg)
        return "FAILURE", server_counter

    updateQuantityQuery = {"$set": {"quantity": int(currentQuantity) - 1}}
    books.update_one(issueQuery, updateQuantityQuery)
    borrowedBooks.insert_one(
        {"title": issueTitle, "userName": userName, "timeStamp": server_counter})

    msg = "Borrowed book by Process: {} at Lamport Timestamp: {}".format(
        pid, server_counter)
    # print(msg)
    proxy.borrowBookServer(issueTitle, userName, pid, timestamp)
    return "SUCCESS", server_counter


def borrowBookServer(issueTitle, userName, pid, timestamp):
    update_server_counter(timestamp)

    issueQuery = {"title": issueTitle}
    currentEntry = books.find_one(issueQuery)
    currentQuantity = 0

    if currentEntry:
        currentQuantity = currentEntry["quantity"]

    if currentQuantity == 0:
        msg = "Borrow book transaction failed by Process: {} at Lamport Timestamp: {}".format(
            pid, server_counter)
        # print(msg)
        return "FAILURE", server_counter

    updateQuantityQuery = {"$set": {"quantity": int(currentQuantity) - 1}}
    books.update_one(issueQuery, updateQuantityQuery)
    borrowedBooks.insert_one(
        {"title": issueTitle, "userName": userName, "timeStamp": server_counter})

    msg = "Borrowed book by Process: {} at Lamport Timestamp: {}".format(
        pid, server_counter)
    # print(msg)
    return "SUCCESS", server_counter


def returnBook(returnTitle, pid, timestamp):
    update_server_counter(timestamp)

    returnBookQuery = {"title": returnTitle}
    currentEntry = books.find_one(returnBookQuery)

    if not currentEntry:
        msg = "Return book transaction failed by Process: {} at Lamport Timestamp: {}".format(
            pid, server_counter)
        # print(msg)
        return server_counter

    borrowedBooks.delete_one(returnBookQuery)

    currentQuantity = currentEntry["quantity"]
    updateQuantityQuery = {"$set": {"quantity": int(currentQuantity) + 1}}
    books.update_one(returnBookQuery, updateQuantityQuery)

    msg = "Returned book by Process: {} at Lamport Timestamp: {}".format(
        pid, server_counter)
    # print(msg)
    proxy.returnBookServer(returnTitle, pid, timestamp)
    return server_counter


def returnBookServer(returnTitle, pid, timestamp):
    update_server_counter(timestamp)

    returnBookQuery = {"title": returnTitle}
    currentEntry = books.find_one(returnBookQuery)

    if not currentEntry:
        msg = "Return book transaction failed by Process: {} at Lamport Timestamp: {}".format(
            pid, server_counter)
        # print(msg)
        return server_counter

    borrowedBooks.delete_one(returnBookQuery)

    currentQuantity = currentEntry["quantity"]
    updateQuantityQuery = {"$set": {"quantity": int(currentQuantity) + 1}}
    books.update_one(returnBookQuery, updateQuantityQuery)

    msg = "Returned book by Process: {} at Lamport Timestamp: {}".format(
        pid, server_counter)
    # print(msg)
    return server_counter


def main():
    global PORT

    # Define local XML RPC server
    server = SimpleXMLRPCServer(("localhost", PORT), allow_none=True)

    # Registering the function to the server
    server.register_function(addBook)
    server.register_function(addBookServer)
    server.register_function(deleteBook)
    server.register_function(deleteBookServer)
    server.register_function(viewBooks)
    server.register_function(viewBorrowedBooks)
    server.register_function(borrowBook)
    server.register_function(borrowBookServer)
    server.register_function(returnBook)
    server.register_function(returnBookServer)
    server.register_function(requestCS)
    server.register_function(releaseCS)

    try:
        print(f"Listening on port {PORT}...")
        print("Press Ctrl + C to exit.")
        server.serve_forever()

    except:
        print("Exit successful.")


if __name__ == "__main__":
    main()
