from os import getpid
from datetime import datetime
from multiprocessing import Process, Pipe



def update_counter(received_counter, counter, pid):
    for id in range(len(counter)):
        counter[id] = max(received_counter[id], counter[id])
        if id == pid:
            counter[id] += 1

    return counter

def get_current_time(counter):
    return '<vector clock is: {}, system time is: {}>'.format(counter, datetime.now())

def launch_an_event(pid, counter):
    counter[pid] += 1
    print('Process {}: an event happened without sending/receiving. '.format(pid) + get_current_time(counter))

    return counter

def send_message(pipe, pid, counter):
    counter[pid] += 1
    pipe.send(('Hello world', counter))
    print('Process ' + str(pid) + ': sent a message. ' + get_current_time(counter))
    
    return counter

def recv_message(pipe, pid, counter):
    message, received_counter = pipe.recv()
    counter = update_counter(received_counter, counter, pid)
    print('Process ' + str(pid) + ': received a message. ' + get_current_time(counter))
    
    return counter

def process_0(p0_to_p1):
    pid = 0
    counter = [0,0,0]
    counter  = launch_an_event(pid, counter)
    counter = send_message(p0_to_p1, pid, counter)
    counter  = launch_an_event(pid, counter)
    counter = recv_message(p0_to_p1, pid, counter)
    counter  = launch_an_event(pid, counter)


def process_1(p1_to_p0, p1_to_p2):
    pid = 1
    counter = [0,0,0]
    counter = recv_message(p1_to_p0, pid, counter)
    counter = launch_an_event(pid, counter)
    counter = send_message(p1_to_p0, pid, counter)
    counter = send_message(p1_to_p2, pid, counter)
    counter = recv_message(p1_to_p2, pid, counter)


def process_2(p2_to_p1):
    pid = 2
    counter = [0,0,0]
    counter = recv_message(p2_to_p1, pid, counter)
    counter = send_message(p2_to_p1, pid, counter)
    

if __name__ == '__main__':
    p0_to_p1, p1_to_p0 = Pipe()
    p1_to_p2, p2_to_p1 = Pipe()

    process0 = Process(target=process_0, args=(p0_to_p1, ))
    process1 = Process(target=process_1, args=(p1_to_p0, p1_to_p2))
    process2 = Process(target=process_2, args=(p2_to_p1, ))

    process0.start()
    process1.start()
    process2.start()

    process0.join()
    process1.join()
    process2.join()