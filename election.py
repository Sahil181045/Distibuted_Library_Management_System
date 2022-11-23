class Process:
    def __init__(self, id, active_status) -> None:
        self.id = id
        self.active_status = active_status


class Ring:
    def __init__(self) -> None:
        self.n = int(input("Enter no of processes: "))
        self.processes = []
        for i in range(self.n):
            self.processes.append(Process(i, True))

    def get_max_idx(self):
        max, max_idx = -1, -1

        for i in range(self.n):
            cur = self.processes[i]
            if cur.active_status and cur.id > max:
                max = cur.id
                max_idx = i

        return max_idx

    def perform_election(self):
        max_idx = self.get_max_idx()

        self.processes[max_idx].active_status = False
        print(f"\nProcess no. {self.processes[max_idx].id} fails\n")

        initiator_proc = int(input("Election initiated by: "))
        while initiator_proc == self.processes[max_idx].id:
            print(
                f"Process {self.processes[max_idx].id} has failed. Please input another process!")
            initiator_proc = int(input("\nElection initiated by: "))

        cur = initiator_proc
        next = (cur+1) % self.n
        active_list = []
        active_list_set = set()
        count = 0

        while True:
            if self.processes[cur].id not in active_list_set:
                active_list.append(self.processes[cur].id)
                active_list_set.add(self.processes[cur].id)

            if self.processes[next].active_status:
                print(
                    f"\nProcess {self.processes[cur].id} passes Election message to {self.processes[next].id}")
                print("Active list:", active_list)
                cur = next

            else:
                print(
                    f"\nProcess {self.processes[cur].id} passes Election message to {self.processes[next].id}")
                print("Active list:", active_list)

            count += 1
            next = (next+1) % self.n

            if cur == initiator_proc and count > 1:
                break

        max_idx = self.get_max_idx()
        coordinator = self.processes[max_idx].id
        print(f"\nProcess {coordinator} becomes coodinator\n")

        cur = coordinator
        next = (cur+1) % self.n
        count = 0

        while True:
            if self.processes[next].active_status:
                print(
                    f"Process {self.processes[cur].id} passes Coordinator({coordinator}) message to process {self.processes[next].id}")
                cur = next

            count += 1
            next = (next+1) % self.n

            if cur == coordinator and count > 1:
                print("\nEnd of election")
                break


def main():
    r = Ring()
    r.perform_election()


if __name__ == "__main__":
    main()
