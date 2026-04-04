import contextvars
import uuid

# Define a context variable to store the request_id
request_id_var = contextvars.ContextVar("request_id", default="SYSTEM")

def set_request_id(request_id: str):
    """Sets the request_id in the current context."""
    return request_id_var.set(request_id)

def get_request_id() -> str:
    """Gets the request_id from the current context."""
    return request_id_var.get()

def reset_request_id(token):
    """Resets the request_id to its previous value."""
    request_id_var.reset(token)
