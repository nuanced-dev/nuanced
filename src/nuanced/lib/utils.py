from collections import namedtuple
import multiprocessing
import select

WithTimeoutResult = namedtuple("WithTimeoutResult", ["errors", "value"])

def send_target_return_value_to_conn(conn, target, args):
    return_value = target(args)
    conn.send(return_value)
    conn.close()

def with_timeout(target, args, timeout):
    errors = []
    value = None

    parent_conn, child_conn = multiprocessing.Pipe()
    process = multiprocessing.Process(
       target=send_target_return_value_to_conn,
       args=(child_conn, target, args)
    )
    process.start()

    readable, _, _ = select.select([parent_conn], [], [], timeout)

    if readable:
        value = parent_conn.recv()
        parent_conn.close()
    else:
        process.terminate()
        parent_conn.close()
        errors.append(multiprocessing.TimeoutError("Operation timed out"))

    process.join()

    return WithTimeoutResult(errors=errors, value=value)
