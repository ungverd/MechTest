import random

RETRANSLATORS = 200 # число люстр
BUF_LEN = 10 # размер кольцевого буфера
IDS = 15 # число разных возможных id
NEIGH_NUM = 1 # метрика числа cocедей у люстры, на самом деле их получается примерно NEIGH_NUM*2 + 1
              # если NEIGH_NUM = 0, то соседей 2, люстры выстроены в кольцо
TRANSMISSION_PROBABILITY = 0.9 # вероятность передачи между люстрами
MESSAGES_TO_SEND = 2000 # число сообщений, которые будут посланы за симуляцию
NEW_MESSAGE_PROBABILITY = 1 # вероятность, что Ксотар отправит новое сообщение в эту итерацию

class CircularBuffer:
    def __init__(self):
        self.buf = [None] * BUF_LEN
        self.i = 0
    def add(self, value):
        self.buf[self.i] = value
        self.i += 1
        if self.i == BUF_LEN:
            self.i = 0
    def __contains__(self, item):
        return item in self.buf

class Retranslator:
    def __init__(self, Id):
        self.buf = CircularBuffer()
        self.infinite_buf = []
        self.id = Id
        self.neighbours = set()
        self.to_send = []
    def send(self, Id, infinite_id):
        for ret in self.neighbours:
            if random.random() <= TRANSMISSION_PROBABILITY:
                ret.receive(Id, infinite_id)
    def receive(self, Id, infinite_id):
        if Id not in self.buf:
            if infinite_id in self.infinite_buf:
                print("!! false_received %d" % infinite_id)
            self.to_send.append((Id, infinite_id))
            self.buf.add(Id)
            self.infinite_buf.append(infinite_id)
        else:
            if infinite_id not in self.infinite_buf:
                print("!! false not received %d" % infinite_id)

    def send_all(self, iteration):
        for ids in self.to_send:
            self.send(*ids)
        self.to_send = []

def main():
    # для проверки, теряются ли сообщения просто из-за плохой связи
    now_messages = []

    retranslators = [Retranslator(i) for i in range(RETRANSLATORS)]
    for i in range(len(retranslators)):
        prev_i = i-1
        next_i = i+1
        if next_i == len(retranslators):
            next_i = 0
        ret = retranslators[i]
        ret.neighbours.add(retranslators[prev_i])
        ret.neighbours.add(retranslators[next_i])
        for j in range(NEIGH_NUM):
            rand = random.randint(0, len(retranslators)-1)
            if rand != i:
                randRet = retranslators[rand]
                ret.neighbours.add(randRet)
                randRet.neighbours.add(ret)
    random.shuffle(retranslators)


    now_messages = [] # для проверки, теряются ли сообщения просто из-за плохой связи
    lost_messages = []

    infinite_id = 0
    while infinite_id < MESSAGES_TO_SEND:
        if random.random() <= NEW_MESSAGE_PROBABILITY:
            now_messages.append(infinite_id)
            Id = infinite_id % IDS
            startRet = retranslators[random.randint(0, len(retranslators)-1)]
            startRet.send(Id, infinite_id)
            infinite_id += 1
            if (infinite_id) % 100 == 0:
                print("    ", infinite_id, "messages sent")
        for ret in retranslators:
            ret.send_all(i)

        # проверка на потерю сообщений по любым причинам
        for j in range(len(now_messages) - 1, -1, -1):
            message_received_by_all = True
            for ret in retranslators:
                if now_messages[j] not in ret.infinite_buf:
                    message_received_by_all = False
                    break
            if message_received_by_all:
                now_messages.pop(j)
        translating_messages = set().union(*((pair[1] for pair in ret.to_send) for ret in retranslators))
        for message in now_messages:
            if message not in translating_messages:
                if message not in lost_messages:
                    print("message lost", message)
                    lost_messages.append(message)
    print("lost", len(lost_messages)*100/MESSAGES_TO_SEND, "% of messages")
    print("end")


main()
