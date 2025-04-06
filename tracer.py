import sys
import time
import inspect
import functools
from typing import Dict, List, Callable, Set, Any, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class FunctionStats:
    """Class for storing statistics about a traced function."""
    call_count: int = 0
    total_time: float = 0.0  # Total execution time in seconds
    min_time: float = float('inf')  # Minimum execution time seen
    max_time: float = 0.0  # Maximum execution time seen

    @property
    def avg_time(self) -> float:
        """Calculate average execution time."""
        return self.total_time / self.call_count if self.call_count > 0 else 0


class FunctionTracer:
    """
    A utility for tracing and measuring execution time of specific Python functions.
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        """Get or create a singleton instance of FunctionTracer."""
        if cls._instance is None:
            cls._instance = FunctionTracer()
        return cls._instance

    @classmethod
    def trace(cls, func=None):
        """
        Decorator to mark a function for tracing.

        Can be used as:
            @FunctionTracer.trace
            def function_to_trace():
                pass

        Returns:
            The original function unchanged
        """

        def decorator(function):
            tracer = cls.get_instance()
            if not hasattr(tracer, '_decorated_functions'):
                tracer._decorated_functions = set()
            tracer._decorated_functions.add(function)

            @functools.wraps(function)
            def wrapper(*args, **kwargs):
                return function(*args, **kwargs)

            return wrapper

        if func is None:
            return decorator
        return decorator(func)

    def __init__(self):
        self._enabled = False
        self._traced_functions: Set[Callable] = set()  # Regular functions being traced
        self._decorated_functions: Set[Callable] = set()  # Functions with @trace decorator
        self._stats: Dict[Callable, FunctionStats] = defaultdict(FunctionStats)
        self._call_stack: Dict[int, Tuple[Callable, float]] = {}  # thread_id -> (func, start_time)
        self._original_trace_function = None

        self._builtin_functions: Set[Callable] = set()  # Built-in functions being traced
        self._original_builtins: Dict[Callable, Callable] = {}  # Original built-in functions
        self._wrapped_builtins: Dict[Callable, Callable] = {}  # Wrapped built-in functions

    def enable(self, functions: List[Callable] = None) -> None:
        """
        Enable function tracing for the specified list of functions.

        Args:
            functions: List of function objects to trace. If None, only trace
                      functions decorated with @FunctionTracer.trace
        """
        if self._enabled:
            # If already enabled, update the function list
            if functions is not None:
                self.update_functions(functions)
            return

        self._traced_functions = set(self._decorated_functions)

        if functions:
            for func in functions:
                if self._is_builtin_function(func):
                    self._builtin_functions.add(func)
                else:
                    self._traced_functions.add(func)

        self._original_trace_function = sys.gettrace()
        sys.settrace(self._trace_function)

        self._setup_builtin_tracing()

        self._enabled = True

    def disable(self) -> Dict[Callable, FunctionStats]:
        """
        Disable function tracing and return the collected statistics.

        Returns:
            Dictionary mapping functions to their execution statistics
        """
        if not self._enabled:
            return dict(self._stats)

        sys.settrace(self._original_trace_function)

        self._restore_builtin_functions()

        self._enabled = False
        self._call_stack.clear()

        return dict(self._stats)

    def update_functions(self, functions: List[Callable]) -> None:
        """
        Update the list of functions being traced without disabling tracing.

        Args:
            functions: New list of function objects to trace
        """
        if not self._enabled:
            raise RuntimeError("Tracing is not enabled")

        self._restore_builtin_functions()

        self._traced_functions = set(self._decorated_functions)  # Keep decorated functions
        self._builtin_functions.clear()

        for func in functions:
            if self._is_builtin_function(func):
                self._builtin_functions.add(func)
            else:
                self._traced_functions.add(func)

        self._setup_builtin_tracing()

    def get_results(self) -> Dict[Callable, FunctionStats]:
        """
        Get the current results of function tracing.

        Returns:
            Dictionary mapping functions to their execution statistics
        """
        return dict(self._stats)

    def _is_builtin_function(self, func: Callable) -> bool:
        """
        Check if a function is a built-in function that needs special handling.

        Args:
            func: Function to check

        Returns:
            True if the function is a built-in function, False otherwise
        """
        return (not hasattr(func, '__code__') and callable(func))

    def _setup_builtin_tracing(self) -> None:
        """Set up tracing for built-in functions by wrapping them."""
        for func in self._builtin_functions:
            if func in self._wrapped_builtins:
                continue

            self._original_builtins[func] = func

            @functools.wraps(func)
            def wrapped_function(*args, **kwargs):
                if not self._enabled:
                    return func(*args, **kwargs)

                start_time = time.perf_counter()
                result = func(*args, **kwargs)
                duration = time.perf_counter() - start_time

                stats = self._stats[func]
                stats.call_count += 1
                stats.total_time += duration
                stats.min_time = min(stats.min_time, duration)
                stats.max_time = max(stats.max_time, duration)

                return result

            self._wrapped_builtins[func] = wrapped_function

            if hasattr(func, '__module__') and hasattr(func, '__name__'):
                try:
                    module_name = func.__module__
                    func_name = func.__name__

                    import importlib
                    module = importlib.import_module(module_name)
                    setattr(module, func_name, wrapped_function)
                except Exception as e:
                    print(f"Warning: Could not wrap {func.__name__}: {e}")

    def _restore_builtin_functions(self) -> None:
        """Restore original built-in functions."""
        for func, original in self._original_builtins.items():
            if hasattr(func, '__module__') and hasattr(func, '__name__'):
                try:
                    module_name = func.__module__
                    func_name = func.__name__

                    import importlib
                    module = importlib.import_module(module_name)
                    setattr(module, func_name, original)
                except Exception as e:
                    print(f"Warning: Could not restore {func.__name__}: {e}")

        self._builtin_functions.clear()
        self._original_builtins.clear()
        self._wrapped_builtins.clear()

    def _trace_function(self, frame, event, arg) -> Optional[Callable]:
        """
        Trace function that will be registered with sys.settrace().

        Args:
            frame: Current execution frame
            event: Event type ('call', 'return', 'line', 'exception')
            arg: Event-specific argument

        Returns:
            Self if the function should be traced, None otherwise
        """
        try:
            if event == 'call':
                # A function is being called
                func = None
                code = frame.f_code

                for traced_func in self._traced_functions:
                    if hasattr(traced_func, '__code__') and traced_func.__code__ is code:
                        func = traced_func
                        break

                if func is not None:
                    thread_id = id(frame)
                    self._call_stack[thread_id] = (func, time.perf_counter())
                    return self._trace_function

            elif event == 'return':
                thread_id = id(frame)
                if thread_id in self._call_stack:
                    # It's a function we're tracing
                    func, start_time = self._call_stack.pop(thread_id)
                    duration = time.perf_counter() - start_time

                    # Update stats
                    stats = self._stats[func]
                    stats.call_count += 1
                    stats.total_time += duration
                    stats.min_time = min(stats.min_time, duration)
                    stats.max_time = max(stats.max_time, duration)
        except Exception as e:
            print(f"Tracing error: {e}")

        return None

    def format_results(self) -> str:
        """
        Format the tracing results into a human-readable string.

        Returns:
            Formatted results as a string
        """
        if not self._stats:
            return "No tracing data collected."

        lines = ["Function Tracing Results:", "-" * 80]
        header = f"{'Function Name':<40} {'Calls':<10} {'Total (s)':<12} {'Avg (ms)':<12} {'Min (ms)':<12} {'Max (ms)':<12}"
        lines.append(header)
        lines.append("-" * 80)

        for func, stats in self._stats.items():
            # Get a readable function name
            if callable(func):
                if hasattr(func, '__name__'):
                    if hasattr(func, '__module__') and func.__module__ != '__main__':
                        func_name = f"{func.__module__}.{func.__name__}"
                    else:
                        func_name = func.__name__
                else:
                    func_name = str(func)
            else:
                func_name = str(func)

            if len(func_name) > 38:
                func_name = "..." + func_name[-35:]

            line = (
                f"{func_name:<40} "
                f"{stats.call_count:<10} "
                f"{stats.total_time:<12.6f} "
                f"{stats.avg_time * 1000:<12.6f} "
                f"{stats.min_time * 1000:<12.6f} "
                f"{stats.max_time * 1000:<12.6f}"
            )
            lines.append(line)

        return "\n".join(lines)
