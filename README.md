# simple task queue
## What
Python library.

+ woking in single host, single process
+ no middleware

I make this to use in chat-bot framework like slack with interactive mode.

## install
TBA

## How to use
most simple use

```python
from simple_task_queue import task, Task, WorkerPool

@task('add')  # register task
def add(a, b):
    return a + b

if __name__ == '__main__':
    with WorkerPool():
        print(Task('add')(2, 3))  # 5
```

async

```python
from simple_task_queue import task, Task, WorkerPool

@task('div')
def div(a, b):
    return a / b

if __name__ == '__main__':
    with WorkerPool():
        t = Task('div')
        t1 = t.promise(1, 0)
        t2 = t.promise(3, 2)
        # do something
        print(t2.result())  # 1.5
        print(t1.result())  # raise ZeroDivisionError
```

use priority

```python
from simple_task_queue import task, Task, WorkerPool

@task('add')
def add(a, b):
    return a + b

@task('background.sleep')
def sleep(name, sec):
    import time
    print('sleep:', name)
    time.sleep(sec)
    print('wake up:', name)

if __name__ == '__main__':
    with WorkerPool(worker_num=10, default_priority=50) as pool:
        # add 'background' queue
        pool.add_queue('background', priority=30)
        for i in range(20):
            # sleepy task goto 'background' queue
            Task('background.sleep').promise(i, 3)
        # This task may be evaluated 11th
        print(Task('add')(4, 3))
    # when exit 'with' join all task
```