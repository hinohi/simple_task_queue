from distutils.core import setup

setup(
    name='simple-task-queue',
    version='0.1.0',
    description='single host single process task queue',
    author='hinohi',
    author_email='42.daiju@gmail.com',
    maintainer='hinohi',
    maintainer_email='42.daiju@gmail.com',
    packages=['simple_task_queue/'],
    url='https://github.com/hinohi/simple_task_queue',
    license='MIT',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Japanese',
        'Topic :: Utilities',
    ]
)