import time

def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

def handler(event, context):
    name = event.get("name", "World")
    delay = int(event.get("delay", 1))  # delay in seconds
    load = int(event.get("load", 10))   # simulate CPU load

    time.sleep(delay)
    _ = fib(load)

    return {
        "statusCode": 200,
        "body": f"Hello, {name}! [Delay: {delay}s | Load: {load}]"
    }
