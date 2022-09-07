import time
from multiprocess import Process
from threading import Thread


def lucky_recount(interval):
    start_val = interval[0]
    count = 0
    for itm in range(250001):
        sum_one = int(interval[0][0]) + int(interval[0][1]) + int(interval[0][2])
        sum_two = int(interval[0][3]) + int(interval[0][4]) + int(interval[0][5])
        modify = int(interval[0]) + 1
        interval[0] = str(modify)
        if len(interval[0]) < 6:
            interval[0] = '0'*(6-len(interval[0]))+interval[0]
        if sum_one == sum_two:
            count += 1
    print(f"Кiлькiсть щасливих квиткiв: {count}  |  iнтервал номерiв:  {start_val} - {interval[1]}")


def view_threads():

    interval_1 = ['000000', '250000']
    interval_2 = ['250001', '500000']
    interval_3 = ['500001', '750000']
    interval_4 = ['750001', '999999']

    print('>>>>>>>>>>>>>>>>>>>>> START THREADS')
    time_start = time.time()
    test_1 = Thread(target=lucky_recount, args=(interval_1,))
    test_2 = Thread(target=lucky_recount, args=(interval_2,))
    test_3 = Thread(target=lucky_recount, args=(interval_3,))
    test_4 = Thread(target=lucky_recount, args=(interval_4,))
    test_1.start()
    test_2.start()
    test_3.start()
    test_4.start()
    test_1.join()
    test_2.join()
    test_3.join()
    test_4.join()
    time_end = time.time()
    print(f'{"-" * 50}\nЗагальний час пiдрахунку {time_end - time_start} секунди')
    print(f'\n{"*" * 50}')

def view_multiprocess():
    interval_1 = ['000000', '250000']
    interval_2 = ['250001', '500000']
    interval_3 = ['500001', '750000']
    interval_4 = ['750001', '999999']
    print('>>>>>>>>>>>>>>>>>>>>> START PROCESSES')
    time_start = time.time()
    test_5 = Process(target=lucky_recount, args=(interval_1,))
    test_6 = Process(target=lucky_recount, args=(interval_2,))
    test_7 = Process(target=lucky_recount, args=(interval_3,))
    test_8 = Process(target=lucky_recount, args=(interval_4,))
    test_5.start()
    test_6.start()
    test_7.start()
    test_8.start()
    test_5.join()
    test_6.join()
    test_7.join()
    test_8.join()
    time_end = time.time()
    print(f'{"-" * 50}\nЗагальний час пiдрахунку {time_end - time_start} секунди')
    print(f'\n{"*" * 50}')

if __name__ == '__main__':
    view_threads()
    view_multiprocess()



