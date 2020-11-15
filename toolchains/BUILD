load("@bazel_tools//tools/python:toolchain.bzl", "py_runtime_pair")

py_runtime(
    name = "py3",
    interpreter_path = "/usr/bin/python3",
    python_version = "PY3",
)

py_runtime(
    name = "py2",
    interpreter_path = "/usr/bin/python2",
    python_version = "PY2",
)

py_runtime_pair(
    name = "my_py_runtime_pair",
    py2_runtime = ":py2",
    py3_runtime = ":py3",
)

toolchain(
    name="my_py_toolchain",
    toolchain = ":my_py_runtime_pair",
    toolchain_type = "@bazel_tools//tools/python:toolchain_type",
)
