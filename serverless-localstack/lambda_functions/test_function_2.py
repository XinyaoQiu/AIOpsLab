import time

def handler(event, context):
    user = event.get("user", "Guest")
    delay = int(event.get("delay", 2))

    # Simulate resource release delay
    time.sleep(delay)

    if user.lower() == "error":
        raise Exception("Simulated application fault for testing.")

    return {
        "statusCode": 200,
        "body": f"Goodbye, {user}. Resources cleaned up."
    }
