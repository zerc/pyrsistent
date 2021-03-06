"""
Script to try do detect any memory leaks that may be lurking in the C implementation of the PVector.
"""
import inspect
import sys
import time
import memory_profiler
import vector_test

try:
    from pvectorc import pvector
except ImportError:
    print("No C implementation of PVector available, terminating")
    sys.exit()


PROFILING_DURATION = 2.0

def run_function(fn):
    stop = time.time() + PROFILING_DURATION
    while time.time() < stop:
        fn(pvector)

def detect_memory_leak(samples):
    # Skip the first half to get rid of the build up period and the last since it seems
    # a little less precise
    samples = samples[int(len(samples)/2):len(samples)-1]
    return not samples.count(samples[0]) > len(samples) - 2

def profile_tests():
    test_functions = [fn for fn in inspect.getmembers(vector_test, inspect.isfunction)
                      if fn[0].startswith('test_')]

    for name, fn in test_functions:
        # There are a couple of tests that are not run for the C implementation, skip those
        fn_args = inspect.getargspec(fn)[0]
        if 'pvector' in fn_args:
            print('Executing %s' % name)
            result = memory_profiler.memory_usage((run_function, (fn,), {}), interval=.1)
            assert not detect_memory_leak(result), (name, result)

if __name__ == "__main__":
    profile_tests()