import time
import random
from tracer import FunctionTracer


def slow_function(sleep_time=0.1):
    """A deliberately slow function that sleeps for a specified time."""
    time.sleep(sleep_time)
    return f"Slept for {sleep_time}s"


def fast_function():
    """A relatively fast function that does a simple calculation."""
    result = 0
    for i in range(1000):
        result += i
    return result


@FunctionTracer.trace
def decorated_function(iterations=1000):
    """A function decorated with the tracer decorator."""
    result = 0
    for i in range(iterations):
        result += i * i
    time.sleep(0.01)  # Small sleep to make timing more noticeable
    return result


def varying_duration():
    """Function with variable execution times."""
    sleep_time = random.uniform(0.01, 0.05)
    time.sleep(sleep_time)
    return sleep_time


def test_basic_tracing():
    """Test basic function tracing."""
    print("\n=== Test 1: Basic Function Tracing ===")

    tracer = FunctionTracer()

    tracer.enable([slow_function, fast_function])

    print("Calling slow_function...")
    slow_function(0.1)

    print("Calling fast_function...")
    fast_function()

    results = tracer.disable()
    print("\nResults after basic tracing:")
    print(tracer.format_results())


def test_builtin_function_tracing():
    """Test tracing built-in functions."""
    print("\n=== Test 2: Built-in Function Tracing ===")

    tracer = FunctionTracer()

    tracer.enable([time.sleep])

    print("Calling time.sleep...")
    time.sleep(0.1)
    time.sleep(0.05)

    print("\nResults after tracing built-in function:")
    print(tracer.format_results())

    tracer.disable()


def test_decorator_approach():
    """Test the decorator-based approach."""
    print("\n=== Test 3: Decorator Approach ===")

    tracer = FunctionTracer.get_instance()

    tracer.enable()

    print("Calling decorated_function...")
    decorated_function()

    print("\nResults after tracing decorated function:")
    print(tracer.format_results())

    tracer.disable()


def test_mixed_tracing():
    """Test tracing a mix of regular, built-in, and decorated functions."""
    print("\n=== Test 4: Mixed Function Tracing ===")

    tracer = FunctionTracer()

    tracer.enable([slow_function, time.sleep])

    print("Calling various functions...")
    slow_function(0.05)
    time.sleep(0.05)
    decorated_function(500)

    print("\nResults after mixed tracing:")
    print(tracer.format_results())

    tracer.disable()


def test_dynamic_toggling():
    """Test dynamically toggling functions being traced."""
    print("\n=== Test 5: Dynamic Function Toggling ===")

    tracer = FunctionTracer()

    tracer.enable([slow_function])

    print("Calling slow_function...")
    slow_function(0.05)

    print("\nIntermediate results:")
    print(tracer.format_results())

    print("\nUpdating trace list to fast_function and time.sleep...")
    tracer.update_functions([fast_function, time.sleep])

    print("Calling updated functions...")
    fast_function()
    time.sleep(0.05)

    print("Calling slow_function again (should not be traced)...")
    slow_function(0.05)

    print("\nResults after dynamic toggling:")
    print(tracer.format_results())

    tracer.disable()


def main():
    """Run all tests."""
    print("=== Enhanced Function Tracer Tests ===")

    test_basic_tracing()
    test_builtin_function_tracing()
    test_decorator_approach()
    test_mixed_tracing()
    test_dynamic_toggling()

    print("\n=== All tests completed ===")


if __name__ == "__main__":
    main()