import threading
import multiprocessing

def chunk_list(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def run_threads(threads):
    for thread in threads:
        print("running thread", thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("all threads finished")

def create_thread(func, arg: tuple):
    thread = threading.Thread(target=func, args=arg)
    return thread

def create_thread_for_each(threads, some_list, func):
    some_list = [threading.Thread(target=func, args=(item,)) for item in some_list]
    threads += some_list


def create_processes(func, args):
    processes = []
    for arg in args:
        processes.append(multiprocessing.Process(target=func, args=(arg,)))
    return processes

def run_processes(processes):
    for process in processes:
        process.start()

    for process in processes:
        process.join()

def create_process(func, args: tuple):
    process = multiprocessing.Process(target=func, args=args)
    return process

def create_process_for_each(processes, some_list, func):
    some_list = [multiprocessing.Process(target=func, args=(item,)) for item in some_list]
    processes += some_list