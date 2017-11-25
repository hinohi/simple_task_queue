# coding: utf-8
import sys
import uuid
import time
from queue import PriorityQueue, Queue
from threading import Thread, Event
from typing import Dict, Callable, Optional
from collections import namedtuple


_TaskInfo = namedtuple('_TaskInfo', ['name', 'func', 'ignore_result'])
_QueueInfo = namedtuple('_QueueInfo', ['name', 'priority'])

_task_registry: Dict[str, _TaskInfo] = {}


def task(name: str, ignore_result=False):
    def wrapper(func):
        _task_registry[name] = _TaskInfo(name, func, ignore_result)
        return func
    return wrapper


class Job:

    def __init__(self, func: Callable, ignore_result=True):
        self.job_id = uuid.uuid4().hex
        self.created = time.time()
        self.__func = func
        self.__ret_value = None
        self.__error = None
        self.ignore_result = ignore_result
        self.__lock = Event()

    def __lt__(self, other):
        return True

    def __call__(self):
        try:
            self.__ret_value = self.__func()
        except Exception as e:
            self.__ret_value = None
            tb = sys.exc_info()[2]
            self.__error = (e, tb)
        self.__lock.set()

    def is_done(self):
        return self.__lock.is_set()

    def result(self):
        if self.ignore_result:
            return
        self.__lock.wait()
        if self.__error is not None:
            e, tb = self.__error
            raise e.__class__(*e.args).with_traceback(tb)
        return self.__ret_value


class Worker:

    def __init__(self, worker_id: int, iq: PriorityQueue, backend):
        self.worker_id = worker_id
        self.iq = iq
        self.backend = backend
        self.__worker = None

    def start(self):
        if self.__worker is None:
            self.__worker = self.backend(target=self.do_work)
            self.__worker.start()

    def do_work(self):
        print('start worker %i' % self.worker_id)
        while True:
            _, job = self.iq.get()
            if job is None:
                break
            job()

    def join(self):
        return self.__worker.join()


class TaskQueue:

    task_queue_instance = None

    def __init__(self, worker_num=4, default_priority=50):
        # TODO: multiprocessing
        self.worker_num = worker_num
        self.default_priority = default_priority
        self.iq = PriorityQueue()
        self.workers = []
        self.task_queues = []

        self.results = {}

    def __enter__(self):
        self.__class__.task_queue_instance = self
        for i in range(self.worker_num):
            worker = Worker(i, self.iq, Thread)
            worker.start()
            self.workers.append(worker)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__class__.task_queue_instance = None
        for i in range(self.worker_num):
            self.iq.put((self.default_priority*100, None))
        for worker in self.workers:
            worker.join()
        return False

    def add_queue(self, name, priority):
        self.task_queues.append(_QueueInfo(name, priority))

    def add_task(self, name: str, func: Callable, async) -> Job:
        dot_sep_name = name.split('.')
        match_len = 0
        priority = self.default_priority
        for q_info in self.task_queues:
            q_name = q_info.name.split('.')
            if len(q_name) > match_len and q_name == dot_sep_name[:len(q_name)]:
                priority = q_info.priority
                match_len = len(q_name)
        job = Job(func, async)
        self.iq.put((priority, job))
        return job


class Task:

    def __init__(self, name: str):
        self.name = name
        self.task = _task_registry.get(name)
        if self.task is None:
            raise ValueError('unknown task: %s' % name)
        if self.task_queue is None:
            raise RuntimeError('task queue is not working')

    @property
    def task_queue(self):
        return TaskQueue.task_queue_instance

    def _make_job(self, args, kwargs):
        def func():
            return self.task.func(*args, **kwargs)
        job = self.task_queue.add_task(
            self.name,
            func,
            self.task.ignore_result)
        return job

    def __call__(self, *args, **kwargs):
        job = self._make_job(args, kwargs)
        return job.result()

    def promise(self, *args, **kwargs) -> Job:
        job = self._make_job(args, kwargs)
        return job
