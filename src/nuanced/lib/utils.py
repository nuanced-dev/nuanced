from collections import namedtuple
import multiprocessing
import select

WithTimeoutResult = namedtuple("WithTimeoutResult", ["errors", "value"])


def send_target_return_value_to_conn(conn, target, args, kwargs):
    return_value = target(args, **kwargs)
    conn.send(return_value)
    conn.close()


def with_timeout(target, args, kwargs, timeout):
    errors = []
    value = None

    parent_conn, child_conn = multiprocessing.Pipe()
    process = multiprocessing.Process(
       target=send_target_return_value_to_conn,
       args=(child_conn, target, args, kwargs),
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

def grouped_by_package(file_paths: list[str]):
    packages = {}
    package_roots = set()

    package_definition_file_paths = list(filter(lambda p: p.endswith("__init__.py"), file_paths))

    for path in package_definition_file_paths:
        package_root = path.rsplit("/", 1)[0]
        is_nested_package = any(package_root.startswith(p) for p in package_roots)
        if not is_nested_package:
            package_roots.add(package_root)

    for path in file_paths:
        for package_root in package_roots:
            if path.startswith(package_root + "/"):
                if package_root not in packages:
                    packages[package_root] = []
                packages[package_root].append(path)
                break

    return packages

def grouped_by_directory(file_paths: list[str]):
    directory_groups = {}

    for path in file_paths:
        directory = path.rsplit("/", 1)[0]

        if directory not in directory_groups:
            directory_groups[directory] = []
        directory_groups[directory].append(path)

    return directory_groups
