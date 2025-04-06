# Python Function Tracer

A lightweight utility for measuring the execution time of specific functions in a Python program.


## Installation

```bash
git clone git@github.com:JanaDragovic/pycharm-debug-standalone-class.git
cd function-tracer
```

## Test Results
```
=== Function Tracer Tests ===
=== Test 1: Basic Function Tracing ===
Calling slow_function...
Calling fast_function...
Results after basic tracing:
Function Tracing Results:
--------------------------------------------------------------------------------
Function Name                            Calls      Total (s)    Avg (ms)     Min (ms)     Max (ms)    
--------------------------------------------------------------------------------
slow_function                            1          0.102150     102.150100   102.150100   102.150100  
fast_function                            1          0.001417     1.417300     1.417300     1.417300    

=== Test 2: Built-in Function Tracing ===
Calling time.sleep...
Results after tracing built-in function:
Function Tracing Results:
--------------------------------------------------------------------------------
Function Name                            Calls      Total (s)    Avg (ms)     Min (ms)     Max (ms)    
--------------------------------------------------------------------------------
time.sleep                               2          0.151579     75.789600    50.617500    100.961700  

=== Test 3: Decorator Approach ===
Calling decorated_function...
Results after tracing decorated function:
Function Tracing Results:
--------------------------------------------------------------------------------
Function Name                            Calls      Total (s)    Avg (ms)     Min (ms)     Max (ms)    
--------------------------------------------------------------------------------
decorated_function                       1          0.011803     11.802700    11.802700    11.802700   

=== Test 4: Mixed Function Tracing ===
Calling various functions...
Results after mixed tracing:
Function Tracing Results:
--------------------------------------------------------------------------------
Function Name                            Calls      Total (s)    Avg (ms)     Min (ms)     Max (ms)    
--------------------------------------------------------------------------------
time.sleep                               3          0.112766     37.588600    10.808200    51.013000   
slow_function                            1          0.051067     51.067300    51.067300    51.067300   

=== Test 5: Dynamic Function Toggling ===
Calling slow_function...
Intermediate results:
Function Tracing Results:
--------------------------------------------------------------------------------
Function Name                            Calls      Total (s)    Avg (ms)     Min (ms)     Max (ms)    
--------------------------------------------------------------------------------
slow_function                            1          0.050624     50.623700    50.623700    50.623700   

Updating trace list to fast_function and time.sleep...
Calling updated functions...
Calling slow_function again (should not be traced)...
Results after dynamic toggling:
Function Tracing Results:
--------------------------------------------------------------------------------
Function Name                            Calls      Total (s)    Avg (ms)     Min (ms)     Max (ms)    
--------------------------------------------------------------------------------
slow_function                            1          0.050624     50.623700    50.623700    50.623700   
fast_function                            1          0.000447     0.446800     0.446800     0.446800    
time.sleep                               2          0.101102     50.551200    50.187800    50.914600   
=== All tests completed ===
```
