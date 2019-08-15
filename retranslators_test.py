# скрипт останавливается после первого "что-то пошло не так"

import random
 
RETRANSLATORS = 200 # число люстр
BUF_LEN = 10 # размер кольцевого буфера
IDS = 15 # число разных возможных id
NEIGH_NUM = 5 # метрика числа cocедей у люстры, на самом деле их получается примерно NEIGH_NUM*2 + 1
              # если NEIGH_NUM = 0, то соседей 2
TRANSMISSION_PROBABILITY = 0.9 # вероятность передачи между люстрами
ITERATIONS = 10000 # число итераций
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
            if random.random() < TRANSMISSION_PROBABILITY:
                res = ret.receive(Id, infinite_id)
                if res:
                    return res
    def receive(self, Id, infinite_id):
        if Id not in self.buf:
            if infinite_id in self.infinite_buf:
                return "false_received"
            self.to_send.append((Id, infinite_id))
            self.buf.add(Id)
            self.infinite_buf.append(infinite_id)
        else:
            if infinite_id not in self.infinite_buf:
                return "false_not_received"
        
    def send_all(self, iteration):
        for ids in self.to_send:
            res = self.send(*ids)
            if res:
                return res
        self.to_send = []
    
def main():
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


    infinite_id = 0
    for i in range(ITERATIONS):
        if random.random() < NEW_MESSAGE_PROBABILITY:
            Id = infinite_id % IDS
            startRet = retranslators[random.randint(0, len(retranslators)-1)]
            res = startRet.send(Id, infinite_id)
            if res:
                print(res)
                return
            infinite_id += 1
        for ret in retranslators:
            res = ret.send_all(i)
            if res:
                print(res)
                return
    print("good")
        


main()
